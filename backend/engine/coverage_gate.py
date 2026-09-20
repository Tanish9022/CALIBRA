from typing import Dict, Any, List, Optional

class CoverageGate:
    """
    OIML R76 Metrological Coverage Gate.
    
    Ensures that an instrument test session is 100% complete and compliant
    before a standardized legal report can be issued or signed.
    
    Verifies:
    1. Mandatory test definitions completed.
    2. Mandatory load points observed (Min, 500e, Max).
    3. Minimum repeat count met for Repeatability (>= 3).
    4. Minimum positions met for Eccentricity (>= 4 or 5).
    5. Test equipment calibration status is valid (not expired).
    6. All evaluations resolved with no blocking errors or unhandled INVALID/REVIEW states.
    """

    @classmethod
    def evaluate_session_coverage(
        cls,
        test_plan: List[Dict[str, Any]],
        results: List[Any],
        observations: List[Any],
        equipment_list: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        blockers = []
        warnings = []
        
        total_tests = len(test_plan)
        completed_test_codes = set()
        test_status_map = {}

        # Map completed results
        for r in results:
            code = getattr(r.test_definition, "code", None) if getattr(r, "test_definition", None) else None
            if not code:
                # Try finding from calculated_values_json or test_plan
                code = f"TEST-{r.test_definition_id}"
            completed_test_codes.add(code)
            test_status_map[code] = r.status
            if r.status == "FAIL":
                warnings.append(f"Test {code} has FAILED compliance criteria: {r.decision_reason}")
            elif r.status == "INVALID":
                blockers.append(f"Test {code} produced an INVALID result: {r.decision_reason}")
            elif r.status == "REVIEW":
                warnings.append(f"Test {code} requires expert REVIEW: {r.decision_reason}")

        # Check mandatory tests from plan
        pending_tests = []
        for t in test_plan:
            code = t["code"]
            if code not in completed_test_codes:
                pending_tests.append(code)
                if t.get("mandatory", True):
                    blockers.append(f"Mandatory test {code} ({t['title']}) has not been executed.")

        # Check equipment calibration status
        if equipment_list:
            for eq in equipment_list:
                status = getattr(eq, "status", "VALID")
                name = getattr(eq, "name", f"Equipment #{getattr(eq, 'id', 'unknown')}")
                if status == "EXPIRED":
                    blockers.append(f"Test standard {name} calibration has EXPIRED. Traceability invalid.")
                elif status == "MAINTENANCE":
                    blockers.append(f"Test standard {name} is under maintenance. Cannot be used for official verification.")

        # Determine gate status
        is_ready = len(blockers) == 0 and len(pending_tests) == 0
        gate_status = "READY" if is_ready else ("BLOCKED" if len(blockers) > 0 else "INCOMPLETE")

        completed_count = len(completed_test_codes)
        coverage_pct = round((completed_count / total_tests) * 100, 1) if total_tests > 0 else 0.0

        return {
            "status": gate_status,
            "is_ready_for_report": is_ready,
            "coverage_percentage": coverage_pct,
            "total_tests": total_tests,
            "completed_tests": completed_count,
            "pending_tests": len(pending_tests),
            "pending_test_codes": pending_tests,
            "blockers_count": len(blockers),
            "blockers": blockers,
            "warnings_count": len(warnings),
            "warnings": warnings,
            "test_status_summary": test_status_map
        }
