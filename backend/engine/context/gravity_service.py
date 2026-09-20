import math
from decimal import Decimal, getcontext
from typing import Dict, Any, Optional, Tuple

getcontext().prec = 34

class GravityContextService:
    """
    Authoritative Gravity Context & Location Service for Legal Metrology.
    
    Implements:
    1. Somigliana International Gravity Formula (1980 / WGS84):
       gamma(phi) = 9.780327 * (1 + 0.0053024 * sin^2(phi) - 0.0000058 * sin^2(2*phi)) m/s^2
    2. Free-Air Elevation Correction:
       delta_g = -3.086e-6 * elevation (m)
    3. Evaluation under OIML R76-1:2006 Clause 3.9.2:
       "Metrological characteristics depending on gravity"
    """

    # Somigliana constants (WGS84)
    GAMMA_E = Decimal("9.780327") # Equatorial gravity in m/s^2
    K_SOMIGLIANA = Decimal("0.0053024")
    K2_SOMIGLIANA = Decimal("0.0000058")
    FREE_AIR_GRADIENT = Decimal("-0.000003086") # m/s^2 per meter of elevation

    @classmethod
    def estimate_gravity_somigliana(cls, latitude_deg: float, elevation_m: float = 0.0) -> Dict[str, Any]:
        """
        Estimates local theoretical acceleration due to gravity using the Somigliana (WGS84)
        formula with free-air elevation reduction.
        
        Note: This is a mathematical approximation and is explicitly labeled ESTIMATED.
        It never replaces authoritative measured or declared values.
        """
        if not (-90.0 <= latitude_deg <= 90.0):
            raise ValueError(f"Latitude must be between -90 and +90 degrees. Got {latitude_deg}")
        
        lat_rad = math.radians(latitude_deg)
        sin_lat = math.sin(lat_rad)
        sin_2lat = math.sin(2.0 * lat_rad)

        # Theoretical sea-level gravity gamma(phi)
        gamma_0 = float(cls.GAMMA_E) * (1.0 + float(cls.K_SOMIGLIANA) * (sin_lat ** 2) - float(cls.K2_SOMIGLIANA) * (sin_2lat ** 2))
        
        # Free-air correction
        free_air = float(cls.FREE_AIR_GRADIENT) * float(elevation_m)
        
        g_est = gamma_0 + free_air

        return {
            "latitude_deg": latitude_deg,
            "elevation_m": elevation_m,
            "sea_level_gravity_ms2": round(gamma_0, 6),
            "free_air_correction_ms2": round(free_air, 6),
            "estimated_gravity_ms2": round(g_est, 6),
            "gravity_source": "ESTIMATED",
            "source_formula": "Somigliana (1980 / WGS84) + Free-Air Correction (-3.086 uGal/m)",
            "metrological_disclaimer": (
                "CALIBRA does not physically measure gravity. This value is an international theoretical "
                "estimate for contextual compliance screening. Authoritative verification requires declared "
                "or measured local gravity."
            )
        }

    @classmethod
    def resolve_local_gravity(
        cls,
        declared_gravity: Optional[float] = None,
        latitude_deg: Optional[float] = None,
        elevation_m: Optional[float] = 0.0
    ) -> Dict[str, Any]:
        """
        Resolves gravity context. Strictly prioritizes measured/declared gravity over estimation.
        Never silently replaces authoritative gravity.
        """
        if declared_gravity is not None and declared_gravity > 0:
            return {
                "local_gravity_ms2": float(declared_gravity),
                "gravity_source": "DECLARED",
                "is_authoritative": True,
                "notes": "Authoritative declared/measured local acceleration of gravity."
            }
        
        if latitude_deg is not None:
            est = cls.estimate_gravity_somigliana(latitude_deg, elevation_m or 0.0)
            return {
                "local_gravity_ms2": est["estimated_gravity_ms2"],
                "gravity_source": "ESTIMATED",
                "is_authoritative": False,
                "estimation_details": est,
                "notes": "Theoretical gravity estimate. Subject to on-site validation."
            }
        
        return {
            "local_gravity_ms2": 9.80665, # Standard standard gravity gn
            "gravity_source": "STANDARD_DEFAULT",
            "is_authoritative": False,
            "notes": "Default standard gravity gn = 9.80665 m/s^2 used because no local coordinates were provided."
        }

    @classmethod
    def evaluate_location_transferability(
        cls,
        accuracy_class: str,
        max_capacity_kg: float,
        verification_interval_e_g: float,
        has_internal_calibration: bool,
        is_gravity_sensitive: bool,
        test_location_name: str,
        test_gravity_ms2: float,
        intended_location_name: str,
        intended_gravity_ms2: float,
        rule_version: str = "OIML R76-1:2006 Clause 3.9.2"
    ) -> Dict[str, Any]:
        """
        Evaluates whether a test result obtained at test_location is legally transferable
        to intended_location per OIML R76-1:2006 Clause 3.9.2 & WELMEC 2 Guide.
        
        Transferability Logic:
        1. If instrument has automatic internal calibration adjustment (self-calibrating weight)
           or is not gravity sensitive (e.g. beam balance with deadweights):
           -> TRANSFERABLE.
        2. If gravity sensitive:
           Calculate relative gravity difference: delta_g / g_test = abs(g_test - g_intended) / g_test.
           Calculate relative MPE at Max: MPE(Max) in grams / (Max in grams).
           For Initial Verification, max permissible shift without recalibration is typically 1/3 of MPE(Max).
           - If delta_g / g <= (1/3) * (MPE(Max) / Max) -> TRANSFERABLE (gravitational shift is negligible within tolerance).
           - If delta_g / g <= (MPE(Max) / Max) -> CONDITIONAL (requires gravity zone marking or on-site adjustment).
           - If delta_g / g > (MPE(Max) / Max) -> RE-TEST / LOCATION-SPECIFIC EVALUATION REQUIRED.
        """
        g1 = Decimal(str(test_gravity_ms2))
        g2 = Decimal(str(intended_gravity_ms2))
        delta_g = abs(g1 - g2)
        relative_delta_g = delta_g / g1 # relative gravity change (dimensionless, ppm)

        # 1. Check if instrument is self-calibrating or insensitive
        if has_internal_calibration:
            return {
                "decision": "TRANSFERABLE",
                "r76_clause": rule_version,
                "is_transferable": True,
                "gravity_sensitive": False,
                "reason": (
                    f"Instrument possesses built-in automatic internal calibration mechanism. "
                    f"Per {rule_version}, gravitational acceleration variations between {test_location_name} "
                    f"({g1:.4f} m/s^2) and {intended_location_name} ({g2:.4f} m/s^2) are automatically compensated."
                ),
                "delta_g_ms2": float(delta_g),
                "relative_delta_g_ppm": float(relative_delta_g * Decimal("1000000")),
                "permissible_limit_ppm": None,
                "recommended_action": "NO_ACTION_REQUIRED"
            }

        if not is_gravity_sensitive:
            return {
                "decision": "TRANSFERABLE",
                "r76_clause": rule_version,
                "is_transferable": True,
                "gravity_sensitive": False,
                "reason": (
                    f"Instrument is declared non-gravity-sensitive (e.g., direct mass-to-mass comparison mechanism). "
                    f"Compliance verified at {test_location_name} is valid at {intended_location_name}."
                ),
                "delta_g_ms2": float(delta_g),
                "relative_delta_g_ppm": float(relative_delta_g * Decimal("1000000")),
                "permissible_limit_ppm": None,
                "recommended_action": "NO_ACTION_REQUIRED"
            }

        # 2. Instrument is gravity sensitive without internal auto-calibration
        # Calculate MPE at Max
        max_g = Decimal(str(max_capacity_kg)) * Decimal("1000")
        e_g = Decimal(str(verification_interval_e_g))
        m_max = max_g / e_g # number of intervals n

        # MPE factor at Max for initial verification
        acc_cls = accuracy_class.strip().upper()
        if acc_cls in ("III", "CLASS III"):
            mpe_factor = Decimal("1.5") if m_max > Decimal("2000") else (Decimal("1.0") if m_max > Decimal("500") else Decimal("0.5"))
        elif acc_cls in ("II", "CLASS II"):
            mpe_factor = Decimal("1.5") if m_max > Decimal("20000") else (Decimal("1.0") if m_max > Decimal("5000") else Decimal("0.5"))
        elif acc_cls in ("I", "CLASS I"):
            mpe_factor = Decimal("1.5") if m_max > Decimal("200000") else (Decimal("1.0") if m_max > Decimal("50000") else Decimal("0.5"))
        else: # Class IIII
            mpe_factor = Decimal("1.5") if m_max > Decimal("200") else (Decimal("1.0") if m_max > Decimal("50") else Decimal("0.5"))

        mpe_max_g = mpe_factor * e_g
        relative_mpe = mpe_max_g / max_g # MPE in ratio (e.g. 15g / 30000g = 0.0005 = 500 ppm)
        one_third_mpe = relative_mpe / Decimal("3.0") # 1/3 MPE zone threshold

        rel_g_ppm = float(relative_delta_g * Decimal("1000000"))
        rel_mpe_ppm = float(relative_mpe * Decimal("1000000"))
        one_third_ppm = float(one_third_mpe * Decimal("1000000"))

        if relative_delta_g <= one_third_mpe:
            decision = "TRANSFERABLE"
            is_trans = True
            action = "NO_ACTION_REQUIRED"
            explanation = (
                f"Relative gravity shift between {test_location_name} and {intended_location_name} is "
                f"{rel_g_ppm:.1f} ppm ({delta_g:.4f} m/s^2), which is within the 1/3 MPE metrological tolerance "
                f"({one_third_ppm:.1f} ppm). Test results remain legally transferable."
            )
        elif relative_delta_g <= relative_mpe:
            decision = "CONDITIONAL"
            is_trans = False
            action = "ON_SITE_ADJUSTMENT_OR_ZONE_MARKING"
            explanation = (
                f"Relative gravity shift is {rel_g_ppm:.1f} ppm, which exceeds 1/3 MPE ({one_third_ppm:.1f} ppm) "
                f"but is within full MPE ({rel_mpe_ppm:.1f} ppm). Under OIML R76-1 Clause 3.9.2, verification "
                f"requires confirmed gravity zone marking or on-site span adjustment at {intended_location_name}."
            )
        else:
            decision = "RE-TEST / LOCATION-SPECIFIC EVALUATION REQUIRED"
            is_trans = False
            action = "MANDATORY_RE_VERIFICATION_AT_INTENDED_LOCATION"
            explanation = (
                f"Relative gravity shift between {test_location_name} and {intended_location_name} is "
                f"{rel_g_ppm:.1f} ppm ({delta_g:.4f} m/s^2), which drastically exceeds the Maximum Permissible Error "
                f"limit of {rel_mpe_ppm:.1f} ppm (±{float(mpe_max_g):.2f} g at Max). "
                f"Under OIML R76-1 Clause 3.9.2, testing performed at {test_location_name} cannot be transferred to "
                f"{intended_location_name} without full re-verification."
            )

        return {
            "decision": decision,
            "r76_clause": rule_version,
            "is_transferable": is_trans,
            "gravity_sensitive": True,
            "test_location": {"name": test_location_name, "g_ms2": float(g1)},
            "intended_location": {"name": intended_location_name, "g_ms2": float(g2)},
            "delta_g_ms2": float(delta_g),
            "relative_delta_g_ppm": round(rel_g_ppm, 2),
            "mpe_at_max_g": float(mpe_max_g),
            "relative_mpe_ppm": round(rel_mpe_ppm, 2),
            "one_third_mpe_ppm": round(one_third_ppm, 2),
            "recommended_action": action,
            "reason": explanation
        }
