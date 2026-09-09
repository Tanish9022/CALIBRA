from typing import Dict, Any

class CalculationEngine:
    """
    Handles unit normalization and error calculations.
    """
    
    UNIT_CONVERSIONS = {
        "kg": {"g": 1000.0, "mg": 1000000.0},
        "g": {"kg": 0.001, "mg": 1000.0},
        "mg": {"kg": 0.000001, "g": 0.001}
    }
    
    @classmethod
    def normalize(cls, value: float, from_unit: str, to_unit: str) -> float:
        if from_unit == to_unit:
            return value
        if from_unit in cls.UNIT_CONVERSIONS and to_unit in cls.UNIT_CONVERSIONS[from_unit]:
            return value * cls.UNIT_CONVERSIONS[from_unit][to_unit]
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")
        
    @classmethod
    def calculate_weighing_error(cls, load: float, indication: float) -> float:
        """Error = indication - load"""
        return indication - load
        
    @classmethod
    def process_observation(cls, raw_load: float, load_unit: str, raw_indication: float, ind_unit: str, base_unit: str = "g") -> Dict[str, Any]:
        """
        Normalizes inputs and calculates basic error.
        Returns trace for evidence chain.
        """
        norm_load = cls.normalize(raw_load, load_unit, base_unit)
        norm_ind = cls.normalize(raw_indication, ind_unit, base_unit)
        error = cls.calculate_weighing_error(norm_load, norm_ind)
        
        return {
            "normalization": {
                "load": {"raw": raw_load, "unit": load_unit, "normalized": norm_load, "base_unit": base_unit},
                "indication": {"raw": raw_indication, "unit": ind_unit, "normalized": norm_ind, "base_unit": base_unit}
            },
            "calculation": {
                "formula": "indication - load",
                "error": error,
                "unit": base_unit
            }
        }
