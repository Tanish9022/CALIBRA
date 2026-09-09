from decimal import Decimal, getcontext
from typing import Dict, Any, List, Optional

getcontext().prec = 34

class RuleEngine:
    """
    Authoritative OIML R76-1:2006 Compliance and Decision Engine.
    Implements:
      - Clause 3.5.1 & Table 6: Maximum Permissible Errors on Initial Verification
      - Clause 3.5.2: Maximum Permissible Errors In-Service
      - Clause 3.2 & Table 3: Verification scale interval limits (n_max)
      - Clause 4.1.2.6: Capacity and Overload limits (Max + 9e)
      - Clause 3.6.1: Repeatability
      - Clause 3.6.2: Eccentricity
    """

    # Table 6: (min_m, max_m, mpe_multiplier_in_e)
    # For first step: min_m is inclusive (0 <= m <= max_m)
    # For subsequent steps: min_m is exclusive (min_m < m <= max_m)
    TABLE_6_INITIAL = {
        "I": [
            (Decimal("0"), Decimal("50000"), Decimal("0.5")),
            (Decimal("50000"), Decimal("200000"), Decimal("1.0")),
            (Decimal("200000"), Decimal("Infinity"), Decimal("1.5")),
        ],
        "II": [
            (Decimal("0"), Decimal("5000"), Decimal("0.5")),
            (Decimal("5000"), Decimal("20000"), Decimal("1.0")),
            (Decimal("20000"), Decimal("100000"), Decimal("1.5")),
        ],
        "III": [
            (Decimal("0"), Decimal("500"), Decimal("0.5")),
            (Decimal("500"), Decimal("2000"), Decimal("1.0")),
            (Decimal("2000"), Decimal("10000"), Decimal("1.5")),
        ],
        "IIII": [
            (Decimal("0"), Decimal("50"), Decimal("0.5")),
            (Decimal("50"), Decimal("200"), Decimal("1.0")),
            (Decimal("200"), Decimal("1000"), Decimal("1.5")),
        ]
    }

    # Table 3: Maximum permissible verification scale intervals n_max
    TABLE_3_NMAX = {
        "I": Decimal("Infinity"),
        "II": Decimal("100000"),
        "III": Decimal("10000"),
        "IIII": Decimal("1000"),
    }

    @classmethod
    def clean_class(cls, accuracy_class: str) -> str:
        if not accuracy_class or not isinstance(accuracy_class, str):
            raise ValueError(f"Invalid accuracy class: '{accuracy_class}'")
        c = accuracy_class.strip().upper()
        # Map common roman/arabic representations
        mapping = {"1": "I", "CLASS I": "I", "2": "II", "CLASS II": "II",
                   "3": "III", "CLASS III": "III", "4": "IIII", "CLASS IIII": "IIII", "IV": "IIII"}
        normalized = mapping.get(c, c)
        if normalized not in cls.TABLE_6_INITIAL:
            raise ValueError(f"Accuracy class '{accuracy_class}' is unsupported under OIML R76-1. Permitted: I, II, III, IIII")
        return normalized

    @classmethod
    def get_mpe(cls, accuracy_class: str, m: Decimal, e_norm: Decimal, verification_type: str = "INITIAL") -> Decimal:
        """
        Calculates Maximum Permissible Error (MPE) for any R76 accuracy class and m range.
        MPE is returned in the same unit as e_norm.
        """
        acc_class = cls.clean_class(accuracy_class)
        verif_type = verification_type.strip().upper()
        if verif_type not in ("INITIAL", "IN_SERVICE"):
            raise ValueError(f"Invalid verification type: '{verification_type}'. Must be 'INITIAL' or 'IN_SERVICE'.")

        if m < Decimal("0"):
            raise ValueError("Verification interval m cannot be negative.")

        n_max = cls.TABLE_3_NMAX[acc_class]
        if m > n_max:
            raise ValueError(f"Load m = {m:.4f} e exceeds maximum allowable intervals for Class {acc_class} (n_max = {n_max})")

        steps = cls.TABLE_6_INITIAL[acc_class]
        mpe_factor = None

        # First interval: 0 <= m <= boundary
        if steps[0][0] <= m <= steps[0][1]:
            mpe_factor = steps[0][2]
        else:
            for low, high, fac in steps[1:]:
                # low < m <= high
                if low < m <= high:
                    mpe_factor = fac
                    break

        if mpe_factor is None:
            raise ValueError(f"Could not determine MPE step for Class {acc_class} at m = {m}")

        if verif_type == "IN_SERVICE":
            # OIML R76-1 Clause 3.5.2
            mpe_factor = mpe_factor * Decimal("2.0")

        return mpe_factor * e_norm

    @classmethod
    def validate_capacity_and_load(
        cls,
        load_norm: Decimal,
        max_norm: Decimal,
        e_norm: Decimal,
        min_norm: Optional[Decimal] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Validates physical and legal capacity boundaries per OIML R76-1 Clauses 3.2, 3.3, 4.1.2.6.
        Returns None if valid, or a structured validation error dict.
        """
        if e_norm <= Decimal("0"):
            return {
                "valid": False,
                "error_code": "INVALID_VERIFICATION_INTERVAL",
                "message": f"Verification scale interval e must be > 0 (got {e_norm} g)."
            }

        if max_norm <= Decimal("0"):
            return {
                "valid": False,
                "error_code": "INVALID_MAX_CAPACITY",
                "message": f"Maximum capacity Max must be > 0 (got {max_norm} g)."
            }

        if min_norm is not None and min_norm > max_norm:
            return {
                "valid": False,
                "error_code": "INVALID_MIN_CAPACITY",
                "message": f"Minimum capacity Min ({min_norm} g) cannot exceed Maximum capacity Max ({max_norm} g)."
            }

        if load_norm < Decimal("0"):
            return {
                "valid": False,
                "error_code": "NEGATIVE_LOAD",
                "message": f"Negative test load ({load_norm} g) is prohibited under OIML R76-1."
            }

        # OIML R76-1 Clause 4.1.2.6: Limit of indication: No indication above Max + 9e
        overload_limit = max_norm + (Decimal("9.0") * e_norm)
        if load_norm > overload_limit:
            return {
                "valid": False,
                "error_code": "OVERLOAD_EXCEEDS_MAX_PLUS_9E",
                "message": f"Applied load ({load_norm} g) exceeds maximum permissible overload limit Max + 9e ({overload_limit} g)."
            }

        return None

    @classmethod
    def evaluate_mpe_rule(
        cls,
        accuracy_class: str,
        load_norm: Any,
        e_norm: Any,
        error_norm: Any,
        max_norm: Optional[Any] = None,
        min_norm: Optional[Any] = None,
        verification_type: str = "INITIAL"
    ) -> Dict[str, Any]:
        """
        Evaluates weighing performance observation against OIML R76-1 MPE rules.
        All normalized mass inputs must be in the same base unit (grams).
        """
        try:
            acc_class = cls.clean_class(accuracy_class)
        except Exception as ex:
            return {
                "applicable_rule": "OIML R76-1:2006 Clause 3.5.1",
                "status": "INVALID",
                "error_code": "UNSUPPORTED_ACCURACY_CLASS",
                "error": str(ex),
                "evaluation": {"passed": False, "requires_review": True, "error_code": "UNSUPPORTED_ACCURACY_CLASS"}
            }

        dec_load = Decimal(str(load_norm))
        dec_e = Decimal(str(e_norm))
        dec_err = Decimal(str(error_norm))
        dec_max = Decimal(str(max_norm)) if max_norm is not None else None
        dec_min = Decimal(str(min_norm)) if min_norm is not None else None

        # 1. Physical / Capacity boundary check
        if dec_max is not None:
            cap_error = cls.validate_capacity_and_load(dec_load, dec_max, dec_e, dec_min)
            if cap_error:
                return {
                    "applicable_rule": "OIML R76-1:2006 Clause 4.1.2.6",
                    "status": "INVALID",
                    "error_code": cap_error["error_code"],
                    "error": cap_error["message"],
                    "evaluation": {"passed": False, "requires_review": True, "error_code": cap_error["error_code"]}
                }

        # 2. Check e > 0
        if dec_e <= Decimal("0"):
            return {
                "applicable_rule": "OIML R76-1:2006 Clause 3.2",
                "status": "INVALID",
                "error_code": "INVALID_VERIFICATION_INTERVAL",
                "error": f"Verification interval e must be > 0 (got {dec_e}).",
                "evaluation": {"passed": False, "requires_review": True, "error_code": "INVALID_VERIFICATION_INTERVAL"}
            }

        # 3. Calculate m = load / e
        m = dec_load / dec_e

        # 4. Lookup MPE
        try:
            mpe = cls.get_mpe(acc_class, m, dec_e, verification_type=verification_type)
        except Exception as ex:
            return {
                "applicable_rule": "OIML R76-1:2006 Clause 3.5.1",
                "status": "INVALID",
                "error_code": "EXCEEDS_CLASS_NMAX",
                "error": str(ex),
                "evaluation": {"passed": False, "requires_review": True, "error_code": "EXCEEDS_CLASS_NMAX"}
            }

        # 5. Deterministic compliance comparison
        passed = abs(dec_err) <= mpe

        rule_code = "R76-1 3.5.1 MPE (Initial Verification)" if verification_type.upper() == "INITIAL" else "R76-1 3.5.2 MPE (In-Service)"

        return {
            "applicable_rule": rule_code,
            "threshold": float(mpe),
            "threshold_decimal": str(mpe),
            "status": "PASS" if passed else "FAIL",
            "evaluation": {
                "load_in_e": float(m),
                "m_decimal": str(m),
                "mpe": float(mpe),
                "mpe_decimal": str(mpe),
                "error": float(dec_err),
                "error_decimal": str(dec_err),
                "passed": passed,
                "requires_review": False
            }
        }

    @classmethod
    def evaluate_repeatability_rule(
        cls,
        accuracy_class: str,
        load_in_g: Decimal,
        e_in_g: Decimal,
        observations_in_g: List[Decimal],
        verification_type: str = "INITIAL"
    ) -> Dict[str, Any]:
        """
        OIML R76-1:2006 Clause 3.6.1 Repeatability.
        Delta I = I_max - I_min <= |MPE(L)|
        """
        if len(observations_in_g) < 3:
            return {
                "applicable_rule": "R76-1 3.6.1 Repeatability",
                "status": "INVALID",
                "error_code": "INSUFFICIENT_OBSERVATIONS",
                "error": "Repeatability requires at least 3 weighings of the same load."
            }

        m = load_in_g / e_in_g
        mpe = cls.get_mpe(accuracy_class, m, e_in_g, verification_type=verification_type)

        spread = max(observations_in_g) - min(observations_in_g)
        passed = spread <= mpe

        return {
            "applicable_rule": "R76-1 3.6.1 Repeatability",
            "status": "PASS" if passed else "FAIL",
            "threshold": float(mpe),
            "spread": float(spread),
            "passed": passed,
            "evaluation": {
                "spread_g": float(spread),
                "mpe_g": float(mpe),
                "passed": passed
            }
        }

    @classmethod
    def evaluate_eccentricity_rule(
        cls,
        accuracy_class: str,
        load_in_g: Decimal,
        e_in_g: Decimal,
        errors_in_g: List[Decimal],
        verification_type: str = "INITIAL"
    ) -> Dict[str, Any]:
        """
        OIML R76-1:2006 Clause 3.6.2 Eccentricity.
        At each position, error must not exceed MPE for that load.
        """
        if not errors_in_g:
            return {
                "applicable_rule": "R76-1 3.6.2 Eccentricity",
                "status": "INVALID",
                "error_code": "MISSING_ECCENTRICITY_OBSERVATIONS",
                "error": "Eccentricity test requires observation errors at receptor positions."
            }

        m = load_in_g / e_in_g
        mpe = cls.get_mpe(accuracy_class, m, e_in_g, verification_type=verification_type)

        failing_positions = [idx + 1 for idx, err in enumerate(errors_in_g) if abs(err) > mpe]
        passed = len(failing_positions) == 0

        return {
            "applicable_rule": "R76-1 3.6.2 Eccentricity",
            "status": "PASS" if passed else "FAIL",
            "threshold": float(mpe),
            "passed": passed,
            "failing_positions": failing_positions
        }
