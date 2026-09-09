from typing import Dict, Any, List

class RuleEngine:
    """
    Evaluates R76 rules against instrument profiles and calculations.
    """
    
    @classmethod
    def get_mpe(cls, accuracy_class: str, load_in_e: float, e: float) -> float:
        """
        Retrieves Maximum Permissible Error (MPE) for Class III
        Returns MPE in the same unit as 'e'
        """
        if accuracy_class == "III":
            if 0 <= load_in_e <= 500:
                return 1.0 * e
            elif 500 < load_in_e <= 2000:
                return 2.0 * e
            elif 2000 < load_in_e <= 10000:
                return 3.0 * e
            else:
                raise ValueError("Load exceeds Maximum Capacity for Class III (10000 e)")
        else:
            raise NotImplementedError(f"Accuracy class {accuracy_class} MPE logic not fully implemented yet.")

    @classmethod
    def evaluate_mpe_rule(cls, accuracy_class: str, load: float, e: float, error: float) -> Dict[str, Any]:
        """
        Evaluates the calculated error against the permissible limit.
        All inputs must be in the same unit.
        """
        load_in_e = load / e
        try:
            mpe = cls.get_mpe(accuracy_class, load_in_e, e)
            passed = abs(error) <= mpe
            
            return {
                "applicable_rule": "R76-1 3.5.1 MPE",
                "threshold": mpe,
                "evaluation": {
                    "load_in_e": load_in_e,
                    "mpe": mpe,
                    "error": error,
                    "passed": passed
                }
            }
        except Exception as ex:
            return {
                "applicable_rule": "R76-1 3.5.1 MPE",
                "error": str(ex),
                "evaluation": {"passed": False, "requires_review": True}
            }
