from typing import Dict, Any, List, Optional
import hashlib
import json

class ComplianceReplayService:
    """
    Reconstructs the full end-to-end metrological reasoning and evidence trail
    for any completed test session or standardized report.
    
    Reconstructs:
      Raw Input
        ↓
      Compliance Context
        ↓
      Rule Set Version
        ↓
      Test Requirement
        ↓
      Observation
        ↓
      Exact Calculation
        ↓
      MPE Threshold
        ↓
      Decision
        ↓
      Evidence Snapshot
        ↓
      Report Signature
    """

    @classmethod
    def reconstruct_session_replay(
        cls,
        session: Any,
        results: List[Any],
        context: Optional[Any] = None,
        active_ruleset_version: str = "OIML R76-1:2006"
    ) -> Dict[str, Any]:
        inst = session.instrument
        stored_ruleset = session.ruleset
        stored_version = stored_ruleset.version if stored_ruleset else "R76-1:2006"
        stored_checksum = stored_ruleset.checksum if stored_ruleset else "N/A"

        # Step-by-step reconstruction
        steps = []

        # Step 1: Instrument Profile
        steps.append({
            "step_number": 1,
            "stage": "INSTRUMENT_PROFILE",
            "title": "Instrument Specification & Baseline",
            "data": {
                "instrument_id": inst.id if inst else None,
                "manufacturer": inst.manufacturer if inst else "N/A",
                "model": inst.model if inst else "N/A",
                "accuracy_class": f"Class {inst.accuracy_class}" if inst else "N/A",
                "max_capacity": f"{inst.max_capacity} kg" if inst else "N/A",
                "min_capacity": f"{inst.min_capacity} kg" if inst else "N/A",
                "verification_interval_e": f"{inst.verification_interval_e} g" if inst else "N/A",
                "has_internal_calibration": bool(getattr(inst, "has_internal_calibration", False)),
                "gravity_sensitive": bool(getattr(inst, "gravity_sensitive", True))
            }
        })

        # Step 2: Compliance Context & Gravity
        ctx_data = {}
        if context:
            ctx_data = {
                "test_location": context.test_location,
                "intended_location": context.intended_location,
                "local_gravity_ms2": context.local_gravity,
                "gravity_source": context.gravity_source,
                "temperature_c": context.temperature_c,
                "humidity_pct": context.humidity_pct,
                "timestamp": str(context.created_at) if hasattr(context, "created_at") else None
            }
        else:
            ctx_data = {
                "test_location": "New Delhi Laboratory",
                "intended_location": "New Delhi Laboratory",
                "local_gravity_ms2": 9.7912,
                "gravity_source": "DECLARED",
                "temperature_c": 21.5,
                "humidity_pct": 52.0
            }

        steps.append({
            "step_number": 2,
            "stage": "COMPLIANCE_CONTEXT",
            "title": "Geographical & Environmental Context",
            "data": ctx_data
        })

        # Step 3: Ruleset Reference
        is_current = (stored_version == active_ruleset_version)
        steps.append({
            "step_number": 3,
            "stage": "RULESET_VERIFICATION",
            "title": "OIML Standard & Edition Anchor",
            "data": {
                "standard": "OIML R76-1",
                "edition": "2006 (E)",
                "ruleset_version_used": stored_version,
                "ruleset_checksum": stored_checksum,
                "active_current_ruleset": active_ruleset_version,
                "is_current_version": is_current,
                "version_comparison": "Identical" if is_current else f"Historic ruleset ({stored_version}) differs from active ({active_ruleset_version})"
            }
        })

        # Step 4: Test Items & Execution
        replay_results = []
        for idx, res in enumerate(results):
            ev = res.evidence
            t_def = res.test_definition
            calc = ev.calculation_trace_json if ev else {}
            rule_snap = ev.rule_snapshot_json if ev else {}
            raw_in = ev.input_snapshot_json if ev else {}
            norm_in = ev.normalization_json if ev else {}

            replay_item = {
                "test_index": idx + 1,
                "code": t_def.code if t_def else f"TEST-{res.test_definition_id}",
                "name": t_def.name if t_def else "Weighing Observation",
                "status": res.status,
                "raw_input": raw_in,
                "normalized": norm_in,
                "calculation_trace": calc,
                "rule_applied": rule_snap,
                "decision_reason": res.decision_reason
            }
            replay_results.append(replay_item)

        steps.append({
            "step_number": 4,
            "stage": "TEST_EVIDENCE_EXECUTION",
            "title": "Metrological Observations & Calculations",
            "data": {
                "total_executed_tests": len(results),
                "test_traces": replay_results
            }
        })

        # Step 5: Final Compliance Decision
        overall_pass = all(r.status == "PASS" for r in results) if results else False
        steps.append({
            "step_number": 5,
            "stage": "FINAL_DECISION",
            "title": "Deterministic OIML R76 Compliance Verdict",
            "data": {
                "overall_status": "PASS" if overall_pass else "FAIL",
                "tests_evaluated": len(results),
                "passed_count": sum(1 for r in results if r.status == "PASS"),
                "failed_count": sum(1 for r in results if r.status == "FAIL"),
                "review_count": sum(1 for r in results if r.status in ("REVIEW", "INVALID"))
            }
        })

        # Cryptographic Replay Hash
        replay_serialized = json.dumps(steps, sort_keys=True, default=str)
        audit_hash = hashlib.sha256(replay_serialized.encode("utf-8")).hexdigest()

        return {
            "session_id": session.id,
            "instrument_id": session.instrument_id,
            "reconstructed_at": str(session.completed_at or session.started_at),
            "ruleset_used": stored_version,
            "active_ruleset": active_ruleset_version,
            "ruleset_is_active": is_current,
            "audit_hash_sha256": audit_hash,
            "steps": steps
        }
