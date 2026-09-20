import sys
import os
from decimal import Decimal, getcontext
getcontext().prec = 28

# Add backend directory to sys.path
backend_path = r"c:\Users\tanish\OneDrive\Tài liệu\Desktop\oiml\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from engine.calculation import CalculationEngine
from engine.rules import RuleEngine

# -------------------------------------------------------------
# INDEPENDENT OIML R76-1:2006 REFERENCE IMPLEMENTATION
# -------------------------------------------------------------

class OIMLR76ReferenceEngine:
    """
    Independent reference implementation strictly following OIML R76-1:2006.
    Does NOT copy CALIBRA logic or formulas.
    """
    
    # Standard MPE table 6 definitions on initial verification (in units of e)
    # Range: (min_m, max_m, mpe_factor_in_e)
    MPE_INITIAL_TABLE = {
        "I": [
            (0, 50000, Decimal("0.5")),
            (50000, 200000, Decimal("1.0")),
            (200000, Decimal("Infinity"), Decimal("1.5")),
        ],
        "II": [
            (0, 5000, Decimal("0.5")),
            (5000, 20000, Decimal("1.0")),
            (20000, 100000, Decimal("1.5")),
        ],
        "III": [
            (0, 500, Decimal("0.5")),
            (500, 2000, Decimal("1.0")),
            (2000, 10000, Decimal("1.5")),
        ],
        "IIII": [
            (0, 50, Decimal("0.5")),
            (50, 200, Decimal("1.0")),
            (200, 1000, Decimal("1.5")),
        ]
    }
    
    UNIT_TO_GRAM = {
        "mg": Decimal("0.001"),
        "g": Decimal("1.0"),
        "kg": Decimal("1000.0"),
        "t": Decimal("1000000.0"),
    }

    @classmethod
    def normalize_mass(cls, value, unit: str):
        u = unit.strip().lower()
        if u not in cls.UNIT_TO_GRAM:
            raise ValueError(f"OIML R76 invalid/unsupported unit: '{unit}'")
        return Decimal(str(value)) * cls.UNIT_TO_GRAM[u]

    @classmethod
    def calculate_basic_error(cls, indication, load):
        """E = I - L per OIML R76-1 A.4.4.1"""
        return Decimal(str(indication)) - Decimal(str(load))

    @classmethod
    def calculate_digital_turning_point(cls, indication, delta_l, e_val):
        """
        P = I + 1/2 e - delta_L per OIML R76-1 A.4.4.3
        """
        return Decimal(str(indication)) + Decimal("0.5") * Decimal(str(e_val)) - Decimal(str(delta_l))

    @classmethod
    def calculate_corrected_error(cls, error, e0):
        """Ec = E - E0 per OIML R76-1 A.4.4.3"""
        return Decimal(str(error)) - Decimal(str(e0))

    @classmethod
    def get_mpe(cls, accuracy_class: str, m_intervals: Decimal, e_norm: Decimal, in_service: bool = False):
        """
        Calculates MPE per Table 6 (Section 3.5.1) or Section 3.5.2 (in-service).
        """
        acc_class = accuracy_class.strip().upper()
        if acc_class not in cls.MPE_INITIAL_TABLE:
            raise ValueError(f"OIML R76 undefined accuracy class: '{accuracy_class}'")
        
        if m_intervals < 0:
            raise ValueError("Negative load is invalid under OIML R76 weighing tests.")
        
        table = cls.MPE_INITIAL_TABLE[acc_class]
        mpe_factor = None
        for low, high, factor in table:
            if low == 0:
                if low <= m_intervals <= high:
                    mpe_factor = factor
                    break
            else:
                if low < m_intervals <= high:
                    mpe_factor = factor
                    break
        
        if mpe_factor is None:
            raise ValueError(f"Load {m_intervals} e exceeds maximum allowable verification intervals for Class {acc_class}")
        
        if in_service:
            mpe_factor = mpe_factor * Decimal("2.0")
            
        return mpe_factor * e_norm

    @classmethod
    def evaluate_observation(cls, raw_load, load_unit, raw_ind, ind_unit, 
                             acc_class, e_val, e_unit, max_cap, max_unit, 
                             min_cap=None, min_unit=None, e0=Decimal("0"), 
                             delta_l=None, in_service=False):
        """
        Full end-to-end OIML R76 metrological evaluation.
        """
        # Validate e
        if Decimal(str(e_val)) <= 0:
            return {"status": "INVALID", "reason": "Verification interval e must be > 0"}

        norm_load = cls.normalize_mass(raw_load, load_unit)
        norm_ind = cls.normalize_mass(raw_ind, ind_unit)
        norm_e = cls.normalize_mass(e_val, e_unit)
        norm_max = cls.normalize_mass(max_cap, max_unit)
        
        if norm_load < 0:
            return {"status": "INVALID", "reason": "Load cannot be negative"}
            
        # OIML R76 4.1.2.6: No indication above Max + 9e
        if norm_load > (norm_max + Decimal("9") * norm_e):
            return {"status": "INVALID", "reason": f"Load {norm_load}g exceeds Max + 9e ({norm_max + 9*norm_e}g)"}

        # Check Min capacity warning/applicability
        is_below_min = False
        if min_cap is not None and min_unit is not None:
            norm_min = cls.normalize_mass(min_cap, min_unit)
            if norm_load < norm_min:
                is_below_min = True

        # Calculate indication and error
        if delta_l is not None:
            norm_delta_l = cls.normalize_mass(delta_l, load_unit)
            p = cls.calculate_digital_turning_point(norm_ind, norm_delta_l, norm_e)
            e_calc = p - norm_load
        else:
            p = norm_ind
            e_calc = cls.calculate_basic_error(norm_ind, norm_load)

        # Corrected error
        ec = cls.calculate_corrected_error(e_calc, Decimal(str(e0)))

        m = norm_load / norm_e

        try:
            mpe = cls.get_mpe(acc_class, m, norm_e, in_service=in_service)
        except Exception as ex:
            return {"status": "INVALID", "reason": str(ex), "load_in_e": m, "error": ec}

        passed = abs(ec) <= mpe

        return {
            "status": "PASS" if passed else "FAIL",
            "load_in_e": m,
            "error": ec,
            "mpe": mpe,
            "below_min": is_below_min,
            "passed": passed
        }

# -------------------------------------------------------------
# RUN COMPARATIVE TEST SUITE
# -------------------------------------------------------------

def run_tests():
    test_cases = [
        # 1. Normal PASS within 0-500e (m=100)
        {
            "id": "TC-01",
            "name": "Class III normal PASS (m=100, E=+0.2e)",
            "load": 1.0, "load_u": "kg", "ind": 1.002, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 2. Boundary m=500e exactly, error = +0.5e (exact limit on initial verification)
        {
            "id": "TC-02",
            "name": "Class III boundary m=500e, E=+0.5e (Exact limit Initial Verif)",
            "load": 5.0, "load_u": "kg", "ind": 5.005, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 3. Boundary m=500e, error = +0.501e (Just above limit on initial verif)
        {
            "id": "TC-03",
            "name": "Class III boundary m=500e, E=+0.51e (FAIL Initial Verif, CALIBRA PASS bug)",
            "load": 5.0, "load_u": "kg", "ind": 5.0051, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 4. Immediate right of boundary m=500.1e (m in (500, 2000], MPE=1.0e)
        {
            "id": "TC-04",
            "name": "Class III transition m=501e, E=+0.8e (PASS Initial Verif)",
            "load": 5.01, "load_u": "kg", "ind": 5.018, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 5. Boundary m=2000e exactly, error = +1.0e (Exact limit Initial Verif)
        {
            "id": "TC-05",
            "name": "Class III boundary m=2000e, E=+1.0e (Exact limit Initial Verif)",
            "load": 20.0, "load_u": "kg", "ind": 20.010, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 6. Boundary m=2000e, error = +1.1e (FAIL Initial Verif, CALIBRA PASS bug because CALIBRA uses 2.0e)
        {
            "id": "TC-06",
            "name": "Class III boundary m=2000e, E=+1.1e (FAIL Initial Verif, CALIBRA False PASS)",
            "load": 20.0, "load_u": "kg", "ind": 20.011, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 7. Immediate right of boundary m=2001e (m in (2000, 10000], MPE=1.5e)
        {
            "id": "TC-07",
            "name": "Class III transition m=2001e, E=+1.4e (PASS Initial Verif)",
            "load": 20.01, "load_u": "kg", "ind": 20.024, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 8. Boundary m=10000e, error = +1.5e (Exact limit Initial Verif)
        {
            "id": "TC-08",
            "name": "Class III boundary m=10000e, E=+1.5e (Exact limit Initial Verif)",
            "load": 100.0, "load_u": "kg", "ind": 100.015, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 100.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 9. Load m=10000.1e (> 10000e for Class III)
        {
            "id": "TC-09",
            "name": "Class III load m=10001e (> 10000e limit)",
            "load": 100.01, "load_u": "kg", "ind": 100.01, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 120.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 10. Negative error exactly at -MPE (Initial Verif m=1000, MPE=10g, E=-10g)
        {
            "id": "TC-10",
            "name": "Class III negative error at exact -MPE (E = -1.0e at m=1000)",
            "load": 10.0, "load_u": "kg", "ind": 9.990, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 11. Negative error exceeding -MPE (Initial Verif m=1000, MPE=10g, E=-12g)
        {
            "id": "TC-11",
            "name": "Class III negative error exceeding -MPE (E = -1.2e at m=1000)",
            "load": 10.0, "load_u": "kg", "ind": 9.988, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 12. Unit conversion consistency: 10 kg vs 10000 g
        {
            "id": "TC-12",
            "name": "Unit Conversion: 10 kg vs 10000 g (Load in kg, Indication in g)",
            "load": 10.0, "load_u": "kg", "ind": 10008.0, "ind_u": "g",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 13. Unit conversion uppercase / alternative formatting
        {
            "id": "TC-13",
            "name": "Unit Conversion: Uppercase 'KG' / 'G' input handling",
            "load": 10.0, "load_u": "KG", "ind": 10.008, "ind_u": "KG",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 14. Milligram units conversion: 500000 mg = 500 g
        {
            "id": "TC-14",
            "name": "Unit Conversion: mg handling (500000 mg = 500 g)",
            "load": 500000.0, "load_u": "mg", "ind": 500005.0, "ind_u": "mg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 15. Load > declared Max capacity (Max=30kg, Load=35kg <= 10000e)
        {
            "id": "TC-15",
            "name": "Capacity Overload: Load > declared Max (Load 35kg on 30kg Max)",
            "load": 35.0, "load_u": "kg", "ind": 35.010, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 16. Negative Load (-5 kg)
        {
            "id": "TC-16",
            "name": "Impossible Load: Negative Load (-5 kg)",
            "load": -5.0, "load_u": "kg", "ind": -5.0, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 17. Invalid verification interval e <= 0 (e = 0)
        {
            "id": "TC-17",
            "name": "Invalid Parameter: e = 0 g",
            "load": 10.0, "load_u": "kg", "ind": 10.0, "ind_u": "kg",
            "acc_class": "III", "e": 0.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 18. Class II Instrument (Analytical balance, e=0.01g, Max=200g, m=10000e)
        {
            "id": "TC-18",
            "name": "Class II Evaluation (High Accuracy class unsupported in CALIBRA)",
            "load": 100.0, "load_u": "g", "ind": 100.005, "ind_u": "g",
            "acc_class": "II", "e": 0.01, "e_u": "g", "max": 200.0, "max_u": "g",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 19. Class I Instrument (Special Accuracy, m=60000e)
        {
            "id": "TC-19",
            "name": "Class I Evaluation (Special Accuracy class unsupported in CALIBRA)",
            "load": 60.0, "load_u": "g", "ind": 60.0008, "ind_u": "g",
            "acc_class": "I", "e": 0.001, "e_u": "g", "max": 100.0, "max_u": "g",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 20. Class IIII Instrument (Ordinary Accuracy, m=150e)
        {
            "id": "TC-20",
            "name": "Class IIII Evaluation (Ordinary Accuracy class unsupported in CALIBRA)",
            "load": 75.0, "load_u": "kg", "ind": 75.05, "ind_u": "kg",
            "acc_class": "IIII", "e": 0.5, "e_u": "kg", "max": 500.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 21. Digital indication with turning point weights delta_L = 4g (e=10g, P = I + 0.5e - delta_L)
        {
            "id": "TC-21",
            "name": "Digital Indication Turning Point: delta_L = 4g, e=10g, I=10.00kg, L=10.00kg",
            "load": 10.0, "load_u": "kg", "ind": 10.00, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": 0.004, "e0": 0.0, "in_service": False
        },
        # 22. Corrected Error Ec = E - E0 where E0 = +4g, E = +12g => Ec = +8g
        {
            "id": "TC-22",
            "name": "Corrected Error: Zero error E0=+4g, E=+12g => Ec=+8g (PASS vs FAIL)",
            "load": 10.0, "load_u": "kg", "ind": 10.012, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 4.0, "in_service": False
        },
        # 23. Zero load testing (m = 0 e)
        {
            "id": "TC-23",
            "name": "Zero load error evaluation (m=0, E=+2g, MPE=±5g)",
            "load": 0.0, "load_u": "kg", "ind": 0.002, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 24. Floating Point Precision Edge Case: Error exactly at boundary (10.000000000000002)
        {
            "id": "TC-24",
            "name": "Floating Point Precision Edge Case (MPE=10.0, calculated E=10.000000000000002)",
            "load": 10.0, "load_u": "kg", "ind": 10.010, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        },
        # 25. CALIBRA demo failing case from UI: Load 10kg, Ind 10.035kg (E=+35g, m=1000e)
        {
            "id": "TC-25",
            "name": "CALIBRA UI Demo Failing Case (Load 10kg, Ind 10.035kg, E=+35g)",
            "load": 10.0, "load_u": "kg", "ind": 10.035, "ind_u": "kg",
            "acc_class": "III", "e": 10.0, "e_u": "g", "max": 30.0, "max_u": "kg",
            "delta_l": None, "e0": 0.0, "in_service": False
        }
    ]

    results = []

    for tc in test_cases:
        # Run CALIBRA
        calibra_res = {}
        try:
            max_val = tc.get("max")
            max_u = tc.get("max_u", "kg")
            min_val = tc.get("min")
            min_u = tc.get("min_u", "kg")

            trace = CalculationEngine.process_observation(
                raw_load=tc["load"],
                load_unit=tc["load_u"],
                raw_indication=tc["ind"],
                ind_unit=tc["ind_u"],
                raw_e=tc["e"],
                e_unit=tc.get("e_u", "g"),
                raw_delta_l=tc.get("delta_l"),
                delta_l_unit=tc.get("delta_l_u", "g") if tc.get("delta_l") is not None else None,
                raw_e0=tc.get("e0"),
                e0_unit=tc.get("e0_u", "g") if tc.get("e0") is not None else None,
                base_unit="g"
            )

            err = trace["_internal_decimals"]["corrected_error"]
            norm_load = trace["_internal_decimals"]["norm_load"]
            norm_e = trace["_internal_decimals"]["norm_e"]

            max_norm = CalculationEngine.normalize(max_val, max_u, "g") if max_val is not None else None
            min_norm = CalculationEngine.normalize(min_val, min_u, "g") if min_val is not None else None

            # Rule evaluation
            eval_res = RuleEngine.evaluate_mpe_rule(
                accuracy_class=tc["acc_class"],
                load_norm=norm_load,
                e_norm=norm_e,
                error_norm=err,
                max_norm=max_norm,
                min_norm=min_norm,
                verification_type="IN_SERVICE" if tc.get("in_service") else "INITIAL"
            )

            status = eval_res.get("status")
            if status == "INVALID":
                calibra_res = {
                    "status": "INVALID",
                    "error_val": float(err) if err is not None else None,
                    "mpe": None,
                    "reason": eval_res.get("error", "Invalid")
                }
            elif "error" in eval_res:
                calibra_res = {
                    "status": "ERROR",
                    "error_val": float(err) if err is not None else None,
                    "mpe": None,
                    "reason": eval_res["error"]
                }
            else:
                passed = eval_res["evaluation"]["passed"]
                calibra_res = {
                    "status": "PASS" if passed else "FAIL",
                    "error_val": float(err),
                    "mpe": eval_res["threshold"],
                    "reason": "Evaluated"
                }
        except Exception as e:
            calibra_res = {
                "status": "EXCEPTION",
                "error_val": None,
                "mpe": None,
                "reason": str(e)
            }

        # Run Reference
        ref_res = {}
        try:
            ref_eval = OIMLR76ReferenceEngine.evaluate_observation(
                raw_load=tc["load"],
                load_unit=tc["load_u"],
                raw_ind=tc["ind"],
                ind_unit=tc["ind_u"],
                acc_class=tc["acc_class"],
                e_val=tc["e"],
                e_unit=tc["e_u"],
                max_cap=tc["max"],
                max_unit=tc["max_u"],
                e0=Decimal(str(tc["e0"])),
                delta_l=Decimal(str(tc["delta_l"])) if tc["delta_l"] is not None else None,
                in_service=tc["in_service"]
            )
            ref_res = ref_eval
        except Exception as e:
            ref_res = {"status": "EXCEPTION", "reason": str(e)}

        # Compare
        match = False
        severity = "LOW"
        notes = []

        # Check status match
        c_stat = calibra_res.get("status")
        r_stat = ref_res.get("status")

        if c_stat == r_stat:
            match = True
            severity = "NONE"
        else:
            match = False
            # Determine severity
            if c_stat == "PASS" and r_stat == "FAIL":
                severity = "CRITICAL (FALSE PASS)"
            elif c_stat == "FAIL" and r_stat == "PASS":
                severity = "HIGH (FALSE REJECT)"
            elif c_stat == "PASS" and r_stat == "INVALID":
                severity = "CRITICAL (FALSE PASS ON INVALID LOAD)"
            elif c_stat in ("EXCEPTION", "ERROR") and r_stat in ("PASS", "FAIL"):
                severity = "HIGH (UNHANDLED EXCEPTION / MISSING R76 CLASS)"
            else:
                severity = "MEDIUM"

        results.append({
            "tc": tc,
            "calibra": calibra_res,
            "ref": ref_res,
            "match": match,
            "severity": severity
        })

    return results

if __name__ == "__main__":
    res = run_tests()
    for r in res:
        tc = r["tc"]
        c = r["calibra"]
        rf = r["ref"]
        print(f"[{tc['id']}] {tc['name']}")
        print(f"  CALIBRA : status={c.get('status')} error={c.get('error_val')} mpe={c.get('mpe')} msg={c.get('reason')}")
        print(f"  REF     : status={rf.get('status')} error={rf.get('error')} mpe={rf.get('mpe')} msg={rf.get('reason')}")
        print(f"  MATCH?  : {r['match']} | Severity: {r['severity']}")
        print("-" * 75)
