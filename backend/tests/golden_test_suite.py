"""
CALIBRA OIML R76-1:2006 GOLDEN TEST SUITE & DIFFERENTIAL TEST HARNESS
Automated verification against Independent Reference Model.
"""

import sys
import os
from decimal import Decimal, getcontext

getcontext().prec = 34

# Ensure backend root is in path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tests.independent_reference import (
    OIMLR76ReferenceModel,
    VerificationType,
    AccuracyClass,
    MetrologicalStatus
)
from engine.calculation import CalculationEngine
from engine.rules import RuleEngine

EPSILON = Decimal("0.000001")

def build_golden_test_cases():
    cases = [
        # 1. Class III normal PASS
        {
            "id": "GT-01",
            "name": "Class III Normal PASS (m=100e, E=+2.0g <= MPE=5.0g)",
            "load": "1.0", "load_u": "kg", "ind": "1.002", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 2. Class III normal FAIL
        {
            "id": "GT-02",
            "name": "Class III Normal FAIL (m=100e, E=+8.0g > MPE=5.0g)",
            "load": "1.0", "load_u": "kg", "ind": "1.008", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 3. m = 500 exactly
        {
            "id": "GT-03",
            "name": "Class III Boundary m=500e exactly (L=5kg, e=10g, MPE=0.5e=5g, E=+5g)",
            "load": "5.0", "load_u": "kg", "ind": "5.005", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 4. m just below 500 (m = 500 - eps => 499.9999e, MPE=0.5e)
        {
            "id": "GT-04",
            "name": "Class III Boundary m just below 500 (m=499.99e, MPE=0.5e=5g)",
            "load": "4.9999", "load_u": "kg", "ind": "5.0049", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 5. m just above 500 (m = 500.01e => MPE=1.0e=10g)
        {
            "id": "GT-05",
            "name": "Class III Boundary m just above 500 (m=500.01e, MPE step to 1.0e=10g)",
            "load": "5.0001", "load_u": "kg", "ind": "5.0081", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 6. m = 2000 exactly
        {
            "id": "GT-06",
            "name": "Class III Boundary m=2000e exactly (L=20kg, e=10g, MPE=1.0e=10g, E=+10g)",
            "load": "20.0", "load_u": "kg", "ind": "20.010", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 7. m just below 2000 (m=1999.99e, MPE=1.0e=10g)
        {
            "id": "GT-07",
            "name": "Class III Boundary m just below 2000 (m=1999.99e, MPE=1.0e=10g)",
            "load": "19.9999", "load_u": "kg", "ind": "20.0099", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 8. m just above 2000 (m=2000.01e => MPE step to 1.5e=15g)
        {
            "id": "GT-08",
            "name": "Class III Boundary m just above 2000 (m=2000.01e, MPE step to 1.5e=15g)",
            "load": "20.0001", "load_u": "kg", "ind": "20.0131", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 9. m = 10000 exactly
        {
            "id": "GT-09",
            "name": "Class III Boundary m=10000e ceiling (L=100kg, e=10g, MPE=1.5e=15g, E=+15g)",
            "load": "100.0", "load_u": "kg", "ind": "100.015", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "100.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 10. m > 10000 (m = 10001e exceeds Class III n_max)
        {
            "id": "GT-10",
            "name": "Class III Exceeds n_max (m=10001e > 10000e)",
            "load": "100.01", "load_u": "kg", "ind": "100.01", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "120.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 11. Positive Error within MPE
        {
            "id": "GT-11",
            "name": "Class III Positive Error (E = +9.5g at m=1000e, MPE=10g)",
            "load": "10.0", "load_u": "kg", "ind": "10.0095", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 12. Negative Error within MPE
        {
            "id": "GT-12",
            "name": "Class III Negative Error (E = -9.5g at m=1000e, MPE=10g)",
            "load": "10.0", "load_u": "kg", "ind": "9.9905", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 13. Exact MPE boundary (|E| == MPE => PASS)
        {
            "id": "GT-13",
            "name": "Exact MPE Boundary (|E| = 10.000000g == MPE=10.0g => PASS)",
            "load": "10.0", "load_u": "kg", "ind": "10.010", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 14. MPE + epsilon (|E| = MPE + 0.001g => FAIL)
        {
            "id": "GT-14",
            "name": "MPE + Epsilon (|E| = 10.001g > MPE=10.0g => FAIL)",
            "load": "10.0", "load_u": "kg", "ind": "10.010001", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 15. MPE - epsilon (|E| = MPE - 0.001g => PASS)
        {
            "id": "GT-15",
            "name": "MPE - Epsilon (|E| = 9.999g < MPE=10.0g => PASS)",
            "load": "10.0", "load_u": "kg", "ind": "10.009999", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 16. Zero Error (E = 0.0g)
        {
            "id": "GT-16",
            "name": "Zero Error (E = 0.000g => PASS)",
            "load": "10.0", "load_u": "kg", "ind": "10.0", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 17. Non-zero E0 correction (E = +12g, E0 = +4g => Ec = +8g <= 10g => PASS)
        {
            "id": "GT-17",
            "name": "Non-Zero E0 Correction (E=+12g, E0=+4g => Ec=+8g <= 10g PASS)",
            "load": "10.0", "load_u": "kg", "ind": "10.012", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": "4.0", "e0_u": "g", "verif_type": "INITIAL"
        },
        # 18. Digital Turning Point with Delta L (I=10.00kg, delta_L=4.0g, e=10g => P=10.001kg => E=+1.0g)
        {
            "id": "GT-18",
            "name": "Digital Turning Point with delta_L (P = I + 0.5e - delta_L => E=+1.0g)",
            "load": "10.0", "load_u": "kg", "ind": "10.00", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": "4.0", "delta_l_u": "g", "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 19. Digital Indication without Turning Point (d=e step)
        {
            "id": "GT-19",
            "name": "Digital Indication without Turning Point (Continuous / Discrete Step)",
            "load": "10.0", "load_u": "kg", "ind": "10.00", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 20. kg Input
        {
            "id": "GT-20",
            "name": "Standard Kilogram Input (10 kg / 10.008 kg)",
            "load": "10.0", "load_u": "kg", "ind": "10.008", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 21. Gram Input
        {
            "id": "GT-21",
            "name": "Standard Gram Input (10000 g / 10008 g)",
            "load": "10000.0", "load_u": "g", "ind": "10008.0", "ind_u": "g",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 22. Milligram Input
        {
            "id": "GT-22",
            "name": "Milligram Input (500000 mg = 500 g, E=+5mg <= MPE=5000mg)",
            "load": "500000.0", "load_u": "mg", "ind": "500005.0", "ind_u": "mg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 23. Uppercase Units ('KG', 'G')
        {
            "id": "GT-23",
            "name": "Case Insensitive Units ('KG', 'G')",
            "load": "10.0", "load_u": "KG", "ind": "10.008", "ind_u": "KG",
            "cls": "III", "e": "10.0", "e_u": "G", "max": "30.0", "max_u": "KG", "min": "0.2", "min_u": "KG",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 24. Negative Load
        {
            "id": "GT-24",
            "name": "Negative Load Validation (L = -5.0 kg => INVALID)",
            "load": "-5.0", "load_u": "kg", "ind": "-5.0", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 25. Load > Max + 9e Overload Limit (Max=30kg, e=10g, Max+9e=30.090kg, Load=35kg => INVALID)
        {
            "id": "GT-25",
            "name": "Overload Rejection: L > Max + 9e (L=35kg on Max=30kg => INVALID)",
            "load": "35.0", "load_u": "kg", "ind": "35.010", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 26. e = 0
        {
            "id": "GT-26",
            "name": "Zero Verification Interval (e = 0 g => INVALID)",
            "load": "10.0", "load_u": "kg", "ind": "10.0", "ind_u": "kg",
            "cls": "III", "e": "0.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 27. e < 0
        {
            "id": "GT-27",
            "name": "Negative Verification Interval (e = -5 g => INVALID)",
            "load": "10.0", "load_u": "kg", "ind": "10.0", "ind_u": "kg",
            "cls": "III", "e": "-5.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 28. Class I Instrument
        {
            "id": "GT-28",
            "name": "Class I Special Accuracy (Max=100g, e=1mg, m=60000e, MPE=1.0e=1mg, E=+0.8mg)",
            "load": "60.0", "load_u": "g", "ind": "60.0008", "ind_u": "g",
            "cls": "I", "e": "0.001", "e_u": "g", "max": "100.0", "max_u": "g", "min": "0.1", "min_u": "g",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 29. Class II Instrument
        {
            "id": "GT-29",
            "name": "Class II High Accuracy (Max=200g, e=0.01g, m=10000e, MPE=1.0e=0.01g, E=+0.005g)",
            "load": "100.0", "load_u": "g", "ind": "100.005", "ind_u": "g",
            "cls": "II", "e": "0.01", "e_u": "g", "max": "200.0", "max_u": "g", "min": "0.5", "min_u": "g",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 30. Class IIII Instrument
        {
            "id": "GT-30",
            "name": "Class IIII Ordinary Accuracy (Max=500kg, e=0.5kg, m=150e, MPE=1.0e=0.5kg, E=+0.05kg)",
            "load": "75.0", "load_u": "kg", "ind": "75.05", "ind_u": "kg",
            "cls": "IIII", "e": "0.5", "e_u": "kg", "max": "500.0", "max_u": "kg", "min": "5.0", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 31. In-Service Inspection MPE (m=500e, E=+8g => FAIL initial verif MPE=5g, PASS in-service MPE=10g)
        {
            "id": "GT-31",
            "name": "In-Service Inspection Clause 3.5.2 (m=500e, E=+8g, MPE=2xInitial=10g => PASS)",
            "load": "5.0", "load_u": "kg", "ind": "5.008", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "IN_SERVICE"
        },
        # 32. Overload limit exact boundary Max + 9e (Max=30kg, e=10g, Max+9e=30.090kg => PASS/Valid)
        {
            "id": "GT-32",
            "name": "Overload Limit Exact Boundary Max + 9e (L = 30.090 kg)",
            "load": "30.090", "load_u": "kg", "ind": "30.095", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 33. Overload limit slightly above Max + 9e + epsilon (L = 30.090001 kg => INVALID)
        {
            "id": "GT-33",
            "name": "Overload Exceeded (L = 30.090001 kg > Max + 9e => INVALID)",
            "load": "30.090001", "load_u": "kg", "ind": "30.095", "ind_u": "kg",
            "cls": "III", "e": "10.0", "e_u": "g", "max": "30.0", "max_u": "kg", "min": "0.2", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        },
        # 34. Tonne Input (1 t = 1000 kg, e = 0.5 kg, m = 2000e)
        {
            "id": "GT-34",
            "name": "Metric Ton Unit Normalization (1 t = 1000 kg, E = +0.4 kg <= MPE = 0.5 kg)",
            "load": "1.0", "load_u": "t", "ind": "1.0004", "ind_u": "t",
            "cls": "III", "e": "0.5", "e_u": "kg", "max": "5.0", "max_u": "t", "min": "10.0", "min_u": "kg",
            "delta_l": None, "delta_l_u": None, "e0": None, "e0_u": None, "verif_type": "INITIAL"
        }
    ]
    return cases

def run_differential_testing():
    cases = build_golden_test_cases()
    results = []

    for tc in cases:
        # 1. Independent Reference Model
        ref_res = OIMLR76ReferenceModel.evaluate_weighing_test(
            raw_load=tc["load"],
            load_unit=tc["load_u"],
            raw_indication=tc["ind"],
            ind_unit=tc["ind_u"],
            accuracy_class=tc["cls"],
            verification_interval_e=tc["e"],
            e_unit=tc["e_u"],
            max_capacity=tc["max"],
            max_unit=tc["max_u"],
            min_capacity=tc["min"],
            min_unit=tc["min_u"],
            raw_delta_l=tc["delta_l"],
            delta_l_unit=tc["delta_l_u"],
            raw_e0=tc["e0"],
            e0_unit=tc["e0_u"],
            verification_type=tc["verif_type"]
        )

        # 2. CALIBRA Production Engine
        cal_res = {}
        try:
            # Calculation & Normalization
            trace = CalculationEngine.process_observation(
                raw_load=tc["load"],
                load_unit=tc["load_u"],
                raw_indication=tc["ind"],
                ind_unit=tc["ind_u"],
                raw_e=tc["e"],
                e_unit=tc["e_u"],
                raw_delta_l=tc["delta_l"],
                delta_l_unit=tc["delta_l_u"],
                raw_e0=tc["e0"],
                e0_unit=tc["e0_u"],
                base_unit="g"
            )
            
            norm_load = trace["_internal_decimals"]["norm_load"]
            norm_e = trace["_internal_decimals"]["norm_e"]
            norm_err = trace["_internal_decimals"]["corrected_error"]
            
            norm_max = CalculationEngine.normalize(tc["max"], tc["max_u"], "g")
            norm_min = CalculationEngine.normalize(tc["min"], tc["min_u"], "g") if tc["min"] else None
            
            # Rule Evaluation
            eval_res = RuleEngine.evaluate_mpe_rule(
                accuracy_class=tc["cls"],
                load_norm=norm_load,
                e_norm=norm_e,
                error_norm=norm_err,
                max_norm=norm_max,
                min_norm=norm_min,
                verification_type=tc["verif_type"]
            )
            
            cal_res = {
                "status": eval_res.get("status", "INVALID"),
                "normalized_load_g": norm_load,
                "normalized_indication_g": trace["_internal_decimals"]["norm_ind"],
                "e_g": norm_e,
                "m": eval_res.get("evaluation", {}).get("load_in_e"),
                "p_g": trace["_internal_decimals"]["norm_p"],
                "raw_error_g": trace["_internal_decimals"]["raw_error"],
                "e0_g": trace["_internal_decimals"]["e0"],
                "corrected_error_g": norm_err,
                "mpe_g": eval_res.get("threshold"),
                "error_code": eval_res.get("error_code")
            }
        except Exception as ex:
            cal_res = {
                "status": "INVALID",
                "error_code": "CRASH",
                "reason": str(ex)
            }

        # 3. Compare Results
        ref_status = ref_res["status"].value if isinstance(ref_res["status"], MetrologicalStatus) else ref_res["status"]
        cal_status = cal_res["status"]

        # Check status match
        status_match = (ref_status == cal_status)
        
        # Check numerical agreement if not INVALID
        numerical_match = True
        num_diffs = []
        if status_match and ref_status in ("PASS", "FAIL"):
            # Compare corrected error
            ref_err = Decimal(str(ref_res["corrected_error_g"]))
            cal_err = Decimal(str(cal_res["corrected_error_g"]))
            if abs(ref_err - cal_err) > EPSILON:
                numerical_match = False
                num_diffs.append(f"Err: Ref={ref_err} Cal={cal_err}")

            # Compare MPE
            ref_mpe = Decimal(str(ref_res["mpe_g"]))
            cal_mpe = Decimal(str(cal_res["mpe_g"]))
            if abs(ref_mpe - cal_mpe) > EPSILON:
                numerical_match = False
                num_diffs.append(f"MPE: Ref={ref_mpe} Cal={cal_mpe}")

        overall_match = status_match and numerical_match
        severity = "NONE" if overall_match else (
            "CRITICAL" if (cal_status == "PASS" and ref_status != "PASS") else "HIGH"
        )

        results.append({
            "tc": tc,
            "ref": ref_res,
            "cal": cal_res,
            "status_match": status_match,
            "numerical_match": numerical_match,
            "overall_match": overall_match,
            "severity": severity,
            "num_diffs": num_diffs
        })

    return results

def run_metamorphic_tests():
    """
    Phase 6: Metamorphic Testing.
    Verify that equivalent unit inputs produce strictly identical decisions.
    """
    equivalents = [
        ("10.0", "kg", "10.008", "kg"),
        ("10000.0", "g", "10008.0", "g"),
        ("10000000.0", "mg", "10008000.0", "mg"),
        ("0.010", "t", "0.010008", "t"),
    ]
    results = []
    base_decision = None
    all_identical = True

    for l_val, l_u, i_val, i_u in equivalents:
        trace = CalculationEngine.process_observation(
            raw_load=l_val, load_unit=l_u,
            raw_indication=i_val, ind_unit=i_u,
            raw_e="10.0", e_unit="g",
            base_unit="g"
        )
        load_g = trace["_internal_decimals"]["norm_load"]
        e_g = trace["_internal_decimals"]["norm_e"]
        err_g = trace["_internal_decimals"]["corrected_error"]
        
        eval_res = RuleEngine.evaluate_mpe_rule(
            accuracy_class="III",
            load_norm=load_g,
            e_norm=e_g,
            error_norm=err_g,
            max_norm=Decimal("30000.0"),
            verification_type="INITIAL"
        )
        dec = eval_res["status"]
        if base_decision is None:
            base_decision = dec
        elif dec != base_decision:
            all_identical = False
        results.append((f"{l_val} {l_u} / {i_val} {i_u}", dec, eval_res["threshold"], float(err_g)))

    return all_identical, results

if __name__ == "__main__":
    print("=================================================================")
    print("RUNNING CALIBRA OIML R76-1:2006 GOLDEN TEST SUITE (34 CASES)")
    print("=================================================================")
    diff_results = run_differential_testing()
    
    total = len(diff_results)
    matched = sum(1 for r in diff_results if r["overall_match"])
    mismatched = total - matched
    crashes = sum(1 for r in diff_results if r["cal"].get("error_code") == "CRASH")
    false_passes = sum(1 for r in diff_results if r["cal"].get("status") == "PASS" and r["ref"].get("status") != "PASS")
    false_fails = sum(1 for r in diff_results if r["cal"].get("status") == "FAIL" and r["ref"].get("status") == "PASS")

    for r in diff_results:
        tc = r["tc"]
        c = r["cal"]
        ref = r["ref"]
        ref_stat = ref["status"].value if hasattr(ref["status"], "value") else ref["status"]
        print(f"[{tc['id']}] {tc['name']}")
        print(f"   REF     : Status={ref_stat} | Err={ref.get('corrected_error_g')} | MPE={ref.get('mpe_g')}")
        print(f"   CALIBRA : Status={c.get('status')} | Err={c.get('corrected_error_g')} | MPE={c.get('mpe_g')}")
        print(f"   MATCH   : {r['overall_match']} (Severity: {r['severity']})")
        if r["num_diffs"]:
            print(f"   DIFFS   : {r['num_diffs']}")
        print("-" * 65)

    print("\n=================================================================")
    print("METAMORPHIC TEST RESULTS (UNIT INVARIANCE)")
    print("=================================================================")
    meta_pass, meta_details = run_metamorphic_tests()
    for item in meta_details:
        print(f"  Input: {item[0]} -> Decision={item[1]}, MPE={item[2]}g, Error={item[3]}g")
    print(f"Metamorphic Invariance Preserved: {meta_pass}")

    print("\n=================================================================")
    print("SUMMARY METRICS")
    print("=================================================================")
    print(f"Total Tests Executed        : {total}")
    print(f"Passed & Perfectly Matched  : {matched}")
    print(f"Mismatched                  : {mismatched}")
    print(f"Crashes                     : {crashes}")
    print(f"False PASS Results          : {false_passes}")
    print(f"False FAIL Results          : {false_fails}")
