from typing import Dict, Any

class EvidenceBuilder:
    @classmethod
    def build_evidence(cls, instrument: Any, observation: Any, trace: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs the full evidence chain for the "Why?" screen.
        """
        return {
            "instrument_profile": {
                "class": instrument.accuracy_class,
                "e": instrument.verification_interval_e,
                "max": instrument.max_capacity,
                "min": instrument.min_capacity
            },
            "raw_input": {
                "load": observation.raw_value,
                "load_unit": observation.raw_unit,
                "indication": observation.metadata_json.get("indication"),
                "indication_unit": observation.metadata_json.get("indication_unit")
            },
            "normalization": trace.get("normalization", {}),
            "calculation": trace.get("calculation", {}),
            "rule": {
                "code": evaluation.get("applicable_rule"),
                "threshold": evaluation.get("threshold")
            },
            "decision": {
                "passed": evaluation.get("evaluation", {}).get("passed"),
                "requires_review": evaluation.get("evaluation", {}).get("requires_review", False)
            }
        }
