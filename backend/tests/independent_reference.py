"""
INDEPENDENT REFERENCE MODEL FOR OIML R76-1:2006
Part 1: Metrological and Technical Requirements - Tests

CRITICAL ARCHITECTURAL CONSTRAINT:
This reference implementation is completely isolated and derives directly
from the authoritative OIML R76-1:2006 standard.
It does NOT import, reference, or call any CALIBRA production modules.
"""

from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

getcontext().prec = 34

class VerificationType(str, Enum):
    INITIAL = "INITIAL"
    IN_SERVICE = "IN_SERVICE"

class AccuracyClass(str, Enum):
    I = "I"
    II = "II"
    III = "III"
    IIII = "IIII"

class MetrologicalStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INVALID = "INVALID"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

class OIMLR76ReferenceModel:
    """
    Authoritative reference implementation of OIML R76-1:2006.
    Uses strict Decimal arithmetic for metrological correctness.
    """

    # OIML R76-1:2006 Table 6: Maximum permissible errors on initial verification
    # Structured as: { Class: [ (min_m_exclusive, max_m_inclusive, mpe_factor_in_e) ] }
    # Note: For the first step (0 to boundary), min_m is inclusive (0 <= m <= max_m).
    TABLE_6_INITIAL = {
        AccuracyClass.I: [
            (Decimal("0"), Decimal("50000"), Decimal("0.5")),
            (Decimal("50000"), Decimal("200000"), Decimal("1.0")),
            (Decimal("200000"), Decimal("Infinity"), Decimal("1.5")),
        ],
        AccuracyClass.II: [
            (Decimal("0"), Decimal("5000"), Decimal("0.5")),
            (Decimal("5000"), Decimal("20000"), Decimal("1.0")),
            (Decimal("20000"), Decimal("100000"), Decimal("1.5")),
        ],
        AccuracyClass.III: [
            (Decimal("0"), Decimal("500"), Decimal("0.5")),
            (Decimal("500"), Decimal("2000"), Decimal("1.0")),
            (Decimal("2000"), Decimal("10000"), Decimal("1.5")),
        ],
        AccuracyClass.IIII: [
            (Decimal("0"), Decimal("50"), Decimal("0.5")),
            (Decimal("50"), Decimal("200"), Decimal("1.0")),
            (Decimal("200"), Decimal("1000"), Decimal("1.5")),
        ]
    }

    # Maximum verification intervals n_max per Table 3 (Section 3.2)
    TABLE_3_NMAX = {
        AccuracyClass.I: Decimal("Infinity"),
        AccuracyClass.II: Decimal("100000"),
        AccuracyClass.III: Decimal("10000"),
        AccuracyClass.IIII: Decimal("1000"),
    }

    # Unit conversion rates strictly normalized to SI gram (g)
    MASS_UNITS_TO_GRAM = {
        "mg": Decimal("0.001"),
        "g": Decimal("1.0"),
        "kg": Decimal("1000.0"),
        "t": Decimal("1000000.0"),
    }

    @classmethod
    def normalize_mass(cls, value: Any, unit: str) -> Decimal:
        """
        Normalizes mass input to grams using Decimal.
        Performs case-insensitive unit stripping.
        """
        if value is None:
            raise ValueError("Mass value cannot be None.")
        clean_unit = str(unit).strip().lower()
        if clean_unit not in cls.MASS_UNITS_TO_GRAM:
            raise ValueError(f"Unsupported unit: '{unit}'. Allowed: mg, g, kg, t")
        return Decimal(str(value)) * cls.MASS_UNITS_TO_GRAM[clean_unit]

    @classmethod
    def calculate_digital_turning_point(cls, indication: Decimal, delta_l: Decimal, e_val: Decimal) -> Decimal:
        """
        OIML R76-1:2006 Clause A.4.4.3:
        Determination of indication prior to rounding (digital indication with d = e):
        P = I + 1/2 e - delta_L
        """
        return indication + (Decimal("0.5") * e_val) - delta_l

    @classmethod
    def calculate_basic_error(cls, p_or_i: Decimal, load: Decimal) -> Decimal:
        """
        OIML R76-1:2006 Clause A.4.4.1:
        E = I - L  (or P - L if turning point determined)
        """
        return p_or_i - load

    @classmethod
    def calculate_corrected_error(cls, error: Decimal, e0: Decimal = Decimal("0")) -> Decimal:
        """
        OIML R76-1:2006 Clause A.4.4.3:
        Ec = E - E0
        """
        return error - e0

    @classmethod
    def get_mpe(cls, accuracy_class: AccuracyClass, m: Decimal, e_norm: Decimal, 
                verification_type: VerificationType = VerificationType.INITIAL) -> Decimal:
        """
        Determines Maximum Permissible Error (MPE) per Table 6 (Clause 3.5.1)
        or Clause 3.5.2 for in-service inspection.
        Returns MPE in the same unit as e_norm.
        """
        if m < Decimal("0"):
            raise ValueError("Verification interval m cannot be negative.")

        if accuracy_class not in cls.TABLE_6_INITIAL:
            raise ValueError(f"Accuracy class {accuracy_class} is not recognized by OIML R76-1.")

        # Check maximum verification intervals for the class
        n_max = cls.TABLE_3_NMAX[accuracy_class]
        if m > n_max:
            raise ValueError(f"Load {m} e exceeds maximum allowable intervals for Class {accuracy_class.value} (n_max = {n_max})")

        intervals = cls.TABLE_6_INITIAL[accuracy_class]
        mpe_factor = None

        # First interval: 0 <= m <= boundary
        first_low, first_high, first_fac = intervals[0]
        if first_low <= m <= first_high:
            mpe_factor = first_fac
        else:
            for low, high, fac in intervals[1:]:
                # low < m <= high
                if low < m <= high:
                    mpe_factor = fac
                    break

        if mpe_factor is None:
            raise ValueError(f"Verification interval m = {m} does not map to an MPE step in Class {accuracy_class.value}")

        if verification_type == VerificationType.IN_SERVICE:
            # OIML R76-1 Clause 3.5.2: In-service MPE is twice initial verification MPE
            mpe_factor = mpe_factor * Decimal("2.0")

        return mpe_factor * e_norm

    @classmethod
    def evaluate_weighing_test(
        cls,
        raw_load: Any,
        load_unit: str,
        raw_indication: Any,
        ind_unit: str,
        accuracy_class: str,
        verification_interval_e: Any,
        e_unit: str,
        max_capacity: Any,
        max_unit: str,
        min_capacity: Optional[Any] = None,
        min_unit: Optional[str] = None,
        raw_delta_l: Optional[Any] = None,
        delta_l_unit: Optional[str] = None,
        raw_e0: Optional[Any] = None,
        e0_unit: Optional[str] = None,
        verification_type: str = "INITIAL"
    ) -> Dict[str, Any]:
        """
        Complete independent metrological evaluation of a weighing performance observation.
        """
        errors: List[str] = []

        # 1. Parse Enums & Verification Type
        try:
            verif_type = VerificationType(verification_type.strip().upper())
        except Exception:
            return {
                "status": MetrologicalStatus.INVALID,
                "error_code": "INVALID_VERIFICATION_TYPE",
                "reason": f"Verification type '{verification_type}' is invalid. Allowed: INITIAL, IN_SERVICE."
            }

        try:
            acc_class = AccuracyClass(accuracy_class.strip().upper())
        except Exception:
            return {
                "status": MetrologicalStatus.INVALID,
                "error_code": "UNSUPPORTED_ACCURACY_CLASS",
                "reason": f"Accuracy class '{accuracy_class}' is invalid. Supported: I, II, III, IIII."
            }

        # 2. Normalize units & basic parameter validation
        try:
            e_norm = cls.normalize_mass(verification_interval_e, e_unit)
            if e_norm <= Decimal("0"):
                return {
                    "status": MetrologicalStatus.INVALID,
                    "error_code": "INVALID_VERIFICATION_INTERVAL",
                    "reason": f"Verification interval e must be strictly positive (got {e_norm} g)."
                }
        except Exception as ex:
            return {"status": MetrologicalStatus.INVALID, "error_code": "INVALID_UNIT", "reason": str(ex)}

        try:
            max_norm = cls.normalize_mass(max_capacity, max_unit)
            if max_norm <= Decimal("0"):
                return {
                    "status": MetrologicalStatus.INVALID,
                    "error_code": "INVALID_MAX_CAPACITY",
                    "reason": f"Max capacity must be strictly positive (got {max_norm} g)."
                }
        except Exception as ex:
            return {"status": MetrologicalStatus.INVALID, "error_code": "INVALID_UNIT", "reason": str(ex)}

        if min_capacity is not None and min_unit is not None:
            try:
                min_norm = cls.normalize_mass(min_capacity, min_unit)
                if min_norm > max_norm:
                    return {
                        "status": MetrologicalStatus.INVALID,
                        "error_code": "INVALID_MIN_CAPACITY",
                        "reason": f"Min capacity ({min_norm} g) cannot exceed Max capacity ({max_norm} g)."
                    }
            except Exception as ex:
                return {"status": MetrologicalStatus.INVALID, "error_code": "INVALID_UNIT", "reason": str(ex)}
        else:
            min_norm = None

        # 3. Normalize Load & Indication
        try:
            load_norm = cls.normalize_mass(raw_load, load_unit)
            ind_norm = cls.normalize_mass(raw_indication, ind_unit)
        except Exception as ex:
            return {"status": MetrologicalStatus.INVALID, "error_code": "INVALID_UNIT", "reason": str(ex)}

        # 4. Metrological Load Validity Checks
        # Load cannot be negative
        if load_norm < Decimal("0"):
            return {
                "status": MetrologicalStatus.INVALID,
                "error_code": "NEGATIVE_LOAD",
                "reason": f"Negative test load ({load_norm} g) is prohibited under OIML R76-1."
            }

        # OIML R76-1:2006 Clause 4.1.2.6: No indication above Max + 9e
        max_overload_limit = max_norm + (Decimal("9.0") * e_norm)
        if load_norm > max_overload_limit:
            return {
                "status": MetrologicalStatus.INVALID,
                "error_code": "OVERLOAD_EXCEEDS_MAX_PLUS_9E",
                "reason": f"Load {load_norm} g exceeds instrument overload limit Max + 9e ({max_overload_limit} g)."
            }

        # 5. Delta L & Pre-rounding Indication P
        if raw_delta_l is not None and delta_l_unit is not None:
            try:
                delta_l_norm = cls.normalize_mass(raw_delta_l, delta_l_unit)
                p_norm = cls.calculate_digital_turning_point(ind_norm, delta_l_norm, e_norm)
                used_turning_point = True
            except Exception as ex:
                return {"status": MetrologicalStatus.INVALID, "error_code": "INVALID_UNIT", "reason": str(ex)}
        else:
            delta_l_norm = None
            p_norm = ind_norm
            used_turning_point = False

        # 6. Basic Error E
        raw_error = cls.calculate_basic_error(p_norm, load_norm)

        # 7. Zero Error E0 & Corrected Error Ec
        if raw_e0 is not None:
            e0_u = e0_unit if e0_unit is not None else "g"
            try:
                e0_norm = cls.normalize_mass(raw_e0, e0_u)
            except Exception as ex:
                return {"status": MetrologicalStatus.INVALID, "error_code": "INVALID_UNIT", "reason": str(ex)}
        else:
            e0_norm = Decimal("0")

        corrected_error = cls.calculate_corrected_error(raw_error, e0_norm)

        # 8. Verification interval m
        m = load_norm / e_norm

        # 9. Determine MPE
        try:
            mpe = cls.get_mpe(acc_class, m, e_norm, verification_type=verif_type)
        except Exception as ex:
            return {
                "status": MetrologicalStatus.INVALID,
                "error_code": "EXCEEDS_CLASS_NMAX",
                "reason": str(ex),
                "load_norm": load_norm,
                "m": m,
                "raw_error": raw_error,
                "corrected_error": corrected_error
            }

        # 10. Compliance Decision
        passed = abs(corrected_error) <= mpe
        status = MetrologicalStatus.PASS if passed else MetrologicalStatus.FAIL

        # Explainability Trace
        rule_clause = "OIML R76-1:2006 Clause 3.5.1 (Table 6)" if verif_type == VerificationType.INITIAL else "OIML R76-1:2006 Clause 3.5.2 (In-Service)"
        comparison_sym = "<=" if passed else ">"
        explanation = (
            f"Observed corrected error |{corrected_error} g| {comparison_sym} permissible MPE limit {mpe} g "
            f"for Class {acc_class.value} at m = {m:.4f} e ({verif_type.value})."
        )

        return {
            "status": status,
            "normalized_load_g": load_norm,
            "normalized_indication_g": ind_norm,
            "e_g": e_norm,
            "m": m,
            "p_g": p_norm,
            "raw_error_g": raw_error,
            "e0_g": e0_norm,
            "corrected_error_g": corrected_error,
            "mpe_g": mpe,
            "passed": passed,
            "used_turning_point": used_turning_point,
            "applicable_rule": rule_clause,
            "decision_reason": explanation
        }

    @classmethod
    def evaluate_repeatability_test(
        cls,
        observations: List[Tuple[Any, str]], # [(indication, unit)]
        load: Any,
        load_unit: str,
        accuracy_class: str,
        verification_interval_e: Any,
        e_unit: str,
        verification_type: str = "INITIAL"
    ) -> Dict[str, Any]:
        """
        OIML R76-1:2006 Clause 3.6.1 & A.4.10:
        The difference between the results of several weighings with the same load
        shall not exceed the absolute value of the MPE for that load.
        Delta I = I_max - I_min <= |MPE(L)|
        """
        if len(observations) < 3:
            return {
                "status": MetrologicalStatus.INVALID,
                "error_code": "INSUFFICIENT_OBSERVATIONS",
                "reason": "Repeatability test requires at least 3 consecutive weighings."
            }

        norm_inds = [cls.normalize_mass(ind, u) for ind, u in observations]
        load_norm = cls.normalize_mass(load, load_unit)
        e_norm = cls.normalize_mass(verification_interval_e, e_unit)
        acc_class = AccuracyClass(accuracy_class.strip().upper())
        verif_type = VerificationType(verification_type.strip().upper())

        i_max = max(norm_inds)
        i_min = min(norm_inds)
        spread = i_max - i_min

        m = load_norm / e_norm
        mpe = cls.get_mpe(acc_class, m, e_norm, verification_type=verif_type)

        passed = spread <= mpe
        return {
            "status": MetrologicalStatus.PASS if passed else MetrologicalStatus.FAIL,
            "spread_g": spread,
            "i_max_g": i_max,
            "i_min_g": i_min,
            "mpe_g": mpe,
            "passed": passed,
            "applicable_rule": "OIML R76-1:2006 Clause 3.6.1 Repeatability",
            "decision_reason": f"Spread |{spread} g| {'<=' if passed else '>'} MPE limit {mpe} g."
        }
