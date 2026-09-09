from typing import Dict, Any, Optional

class EvidenceBuilder:
    @classmethod
    def build_evidence(
        cls,
        instrument: Any,
        observation: Any,
        trace: Dict[str, Any],
        evaluation: Dict[str, Any],
        verification_type: str = "INITIAL"
    ) -> Dict[str, Any]:
        """
        Constructs the comprehensive, immutable evidence chain for audit and explainability.
        Explains deterministically: "Why did this result PASS/FAIL?"
        """
        meta = observation.metadata_json or {}
        eval_data = evaluation.get("evaluation", {})
        passed = eval_data.get("passed", False)
        error_code = evaluation.get("error_code") or eval_data.get("error_code")
        
        # Build deterministic explanation
        calc = trace.get("calculation", {})
        m = eval_data.get("load_in_e")
        mpe = eval_data.get("mpe")
        err = eval_data.get("error")
        p = calc.get("indication_prior_to_rounding_p")
        
        if error_code:
            why = f"Evaluation failed metrological validity check: {evaluation.get('error')} [Error Code: {error_code}]."
        else:
            comp = "<=" if passed else ">"
            why = (
                f"Observed corrected error Ec = {err:+.4f} g has magnitude |{err:.4f}| g which is {comp} "
                f"the applicable MPE limit of ±{mpe:.4f} g for Class {instrument.accuracy_class} "
                f"at m = {m:.2f} e ({verification_type} verification)."
            )

        return {
            "instrument_profile": {
                "class": instrument.accuracy_class,
                "e": instrument.verification_interval_e,
                "max": instrument.max_capacity,
                "min": instrument.min_capacity,
                "unit": getattr(instrument, "unit", "kg")
            },
            "raw_input": {
                "load": observation.raw_value,
                "load_unit": observation.raw_unit,
                "indication": meta.get("indication"),
                "indication_unit": meta.get("indication_unit", observation.raw_unit),
                "delta_l": meta.get("delta_l"),
                "delta_l_unit": meta.get("delta_l_unit"),
                "e0": meta.get("e0"),
                "e0_unit": meta.get("e0_unit"),
                "verification_type": verification_type
            },
            "normalization": trace.get("normalization", {}),
            "calculation": {
                "formula_p": calc.get("formula_p"),
                "indication_p": p,
                "formula_raw_error": calc.get("formula_error"),
                "raw_error_E": calc.get("raw_error"),
                "formula_corrected": calc.get("formula_corrected"),
                "zero_error_E0": calc.get("zero_error_e0"),
                "corrected_error_Ec": calc.get("error"),
                "unit": calc.get("unit")
            },
            "rule": {
                "standard": "OIML R76",
                "edition": "2006",
                "code": evaluation.get("applicable_rule"),
                "threshold_mpe": evaluation.get("threshold"),
                "load_in_e": m,
                "verification_type": verification_type
            },
            "decision": {
                "status": evaluation.get("status", "FAIL" if not passed else "PASS"),
                "passed": passed,
                "requires_review": eval_data.get("requires_review", False),
                "error_code": error_code,
                "explanation": why
            }
        }
