from typing import Dict, Any, List, Optional
from engine.context.gravity_service import GravityContextService

class ImpactAnalysisService:
    """
    Analyzes changes in Compliance Context or RuleSets.
    Identifies affected tests, calculations, evidence items, and reports.
    Prevents automatic blanket invalidation while highlighting dependencies.
    """

    @classmethod
    def analyze_context_change(
        cls,
        instrument_profile: Dict[str, Any],
        old_context: Dict[str, Any],
        new_context: Dict[str, Any],
        rule_version: str = "OIML R76-1:2006"
    ) -> Dict[str, Any]:
        """
        Detects differences between old_context and new_context and evaluates
        metrological impact on active test plan and previous decisions.
        """
        changes_detected = []
        affected_tests = []
        requires_retest = False
        reasons = []

        # 1. Location / Gravity Check
        old_loc = old_context.get("intended_location", old_context.get("test_location", "Unknown"))
        new_loc = new_context.get("intended_location", new_context.get("test_location", "Unknown"))
        old_g = old_context.get("local_gravity", 9.80665)
        new_g = new_context.get("local_gravity", 9.80665)

        if old_loc != new_loc or abs(float(old_g) - float(new_g)) > 0.0001:
            changes_detected.append({
                "field": "location_and_gravity",
                "old_value": f"{old_loc} (g = {old_g} m/s²)",
                "new_value": f"{new_loc} (g = {new_g} m/s²)",
                "dependency": "OIML R76-1 Clause 3.9.2 (Gravity Dependency)"
            })

            # Run transferability evaluation
            trans_eval = GravityContextService.evaluate_location_transferability(
                accuracy_class=instrument_profile.get("accuracy_class", "III"),
                max_capacity_kg=float(instrument_profile.get("max_capacity", 30.0)),
                verification_interval_e_g=float(instrument_profile.get("verification_interval_e", 10.0)),
                has_internal_calibration=bool(instrument_profile.get("has_internal_calibration", False)),
                is_gravity_sensitive=bool(instrument_profile.get("is_gravity_sensitive", True)),
                test_location_name=str(old_loc),
                test_gravity_ms2=float(old_g),
                intended_location_name=str(new_loc),
                intended_gravity_ms2=float(new_g),
                rule_version=f"{rule_version} Clause 3.9.2"
            )

            if trans_eval["decision"] == "RE-TEST / LOCATION-SPECIFIC EVALUATION REQUIRED":
                requires_retest = True
                affected_tests.extend(["WP-01", "WP-02", "WP-03", "WP-04", "RP-01", "RP-02", "EC-01"])
                reasons.append(trans_eval["reason"])
            elif trans_eval["decision"] == "CONDITIONAL":
                reasons.append(trans_eval["reason"])
                affected_tests.extend(["WP-04"]) # at minimum verify at Max or check zone marking

        # 2. Environmental Limits Check (Clause 3.9.1)
        old_temp = old_context.get("temperature_c")
        new_temp = new_context.get("temperature_c")
        if old_temp is not None and new_temp is not None:
            if abs(float(old_temp) - float(new_temp)) >= 10.0:
                changes_detected.append({
                    "field": "temperature",
                    "old_value": f"{old_temp} °C",
                    "new_value": f"{new_temp} °C",
                    "dependency": "OIML R76-1 Clause 3.9.1 (Temperature limits)"
                })
                affected_tests.append("ZT-01") # Zero tracking / span stability

        # 3. Test Equipment Calibration Validity
        equipment_status = new_context.get("equipment_calibration_status", "VALID")
        if equipment_status == "EXPIRED":
            changes_detected.append({
                "field": "test_equipment_calibration",
                "old_value": "VALID",
                "new_value": "EXPIRED",
                "dependency": "ISO/IEC 17025 & OIML R76-1 Test Standards Traceability"
            })
            requires_retest = True
            affected_tests.extend(["WP-01", "WP-02", "WP-03", "WP-04", "RP-01", "RP-02", "EC-01"])
            reasons.append("Test equipment calibration expired. Results cannot be certified until standard weights are re-calibrated.")

        action = "RE_TEST_REQUIRED" if requires_retest else ("REVIEW_REQUIRED" if changes_detected else "NO_ACTION")

        return {
            "has_changes": len(changes_detected) > 0,
            "changes_detected": changes_detected,
            "affected_tests": list(set(affected_tests)),
            "requires_retest": requires_retest,
            "recommended_action": action,
            "reasons": reasons,
            "summary": (
                f"Context change analysis: {len(changes_detected)} environmental or location shifts detected. "
                f"Action: {action}. {len(set(affected_tests))} test items flagged."
            )
        }
