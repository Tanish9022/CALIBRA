from decimal import Decimal, getcontext
from typing import Dict, Any, Optional

getcontext().prec = 34

class CalculationEngine:
    """
    Deterministic Metrological Calculation Engine.
    Implements OIML R76-1:2006 Clauses A.4.4.1 and A.4.4.3 with Decimal precision.
    """
    
    # Base SI mass unit: gram (g)
    MASS_UNITS_TO_GRAM = {
        "mg": Decimal("0.001"),
        "g": Decimal("1.0"),
        "kg": Decimal("1000.0"),
        "t": Decimal("1000000.0")
    }

    @classmethod
    def clean_unit(cls, unit: str) -> str:
        if not unit or not isinstance(unit, str):
            raise ValueError(f"Invalid unit specification: '{unit}'")
        u = unit.strip().lower()
        if u not in cls.MASS_UNITS_TO_GRAM:
            raise ValueError(f"Unsupported unit: '{unit}'. Permitted units: mg, g, kg, t")
        return u
    
    @classmethod
    def normalize(cls, value: Any, from_unit: str, to_unit: str = "g") -> Decimal:
        """
        Normalizes a mass value using arbitrary-precision Decimal arithmetic.
        """
        if value is None:
            raise ValueError("Cannot normalize None value.")
        
        dec_value = Decimal(str(value))
        u_from = cls.clean_unit(from_unit)
        u_to = cls.clean_unit(to_unit)
        
        if u_from == u_to:
            return dec_value
            
        # Convert from source to gram, then gram to target
        grams = dec_value * cls.MASS_UNITS_TO_GRAM[u_from]
        target = grams / cls.MASS_UNITS_TO_GRAM[u_to]
        return target
        
    @classmethod
    def calculate_digital_turning_point(cls, indication: Decimal, delta_l: Decimal, e_norm: Decimal) -> Decimal:
        """
        OIML R76-1:2006 Clause A.4.4.3:
        Pre-rounding indication P = I + 1/2 e - delta_L
        """
        return indication + (Decimal("0.5") * e_norm) - delta_l

    @classmethod
    def calculate_weighing_error(cls, p_or_i: Decimal, load: Decimal) -> Decimal:
        """
        OIML R76-1:2006 Clause A.4.4.1:
        Error = Indication - Load (E = I - L or E = P - L)
        """
        return p_or_i - load

    @classmethod
    def calculate_corrected_error(cls, raw_error: Decimal, e0: Decimal = Decimal("0")) -> Decimal:
        """
        OIML R76-1:2006 Clause A.4.4.3:
        Corrected Error Ec = E - E0
        """
        return raw_error - e0
        
    @classmethod
    def process_observation(
        cls,
        raw_load: Any,
        load_unit: str,
        raw_indication: Any,
        ind_unit: str,
        raw_e: Any,
        e_unit: str = "g",
        raw_delta_l: Optional[Any] = None,
        delta_l_unit: Optional[str] = None,
        raw_e0: Optional[Any] = None,
        e0_unit: Optional[str] = None,
        base_unit: str = "g"
    ) -> Dict[str, Any]:
        """
        Normalizes inputs, evaluates pre-rounding indication P, basic error E, and corrected error Ec.
        Returns immutable calculation lineage trace for metrological evidence chain.
        """
        norm_load = cls.normalize(raw_load, load_unit, base_unit)
        norm_ind = cls.normalize(raw_indication, ind_unit, base_unit)
        norm_e = cls.normalize(raw_e, e_unit, base_unit)
        
        # Determine P
        if raw_delta_l is not None and delta_l_unit is not None:
            norm_delta_l = cls.normalize(raw_delta_l, delta_l_unit, base_unit)
            norm_p = cls.calculate_digital_turning_point(norm_ind, norm_delta_l, norm_e)
            used_turning_point = True
            formula_p = "P = I + 0.5e - delta_L"
        else:
            norm_delta_l = None
            norm_p = norm_ind
            used_turning_point = False
            formula_p = "P = I (digital step / continuous)"
            
        # Basic Error E
        raw_error = cls.calculate_weighing_error(norm_p, norm_load)
        
        # Zero error E0 & Corrected Error Ec
        if raw_e0 is not None:
            norm_e0 = cls.normalize(raw_e0, e0_unit if e0_unit else base_unit, base_unit)
        else:
            norm_e0 = Decimal("0")
            
        corrected_error = cls.calculate_corrected_error(raw_error, norm_e0)
        
        return {
            "normalization": {
                "load": {"raw": str(raw_load), "unit": load_unit, "normalized": str(norm_load), "base_unit": base_unit},
                "indication": {"raw": str(raw_indication), "unit": ind_unit, "normalized": str(norm_ind), "base_unit": base_unit},
                "e": {"raw": str(raw_e), "unit": e_unit, "normalized": str(norm_e), "base_unit": base_unit},
                "delta_l": {"raw": str(raw_delta_l) if raw_delta_l is not None else None, "unit": delta_l_unit, "normalized": str(norm_delta_l) if norm_delta_l is not None else None},
                "e0": {"raw": str(raw_e0) if raw_e0 is not None else None, "unit": e0_unit, "normalized": str(norm_e0)}
            },
            "calculation": {
                "formula_p": formula_p,
                "used_turning_point": used_turning_point,
                "indication_prior_to_rounding_p": float(norm_p),
                "p_decimal": str(norm_p),
                "formula_error": "E = P - L",
                "raw_error": float(raw_error),
                "raw_error_decimal": str(raw_error),
                "zero_error_e0": float(norm_e0),
                "e0_decimal": str(norm_e0),
                "formula_corrected": "Ec = E - E0",
                "error": float(corrected_error),
                "corrected_error_decimal": str(corrected_error),
                "unit": base_unit
            },
            # Internal Decimals for exact downstream comparison
            "_internal_decimals": {
                "norm_load": norm_load,
                "norm_ind": norm_ind,
                "norm_e": norm_e,
                "norm_p": norm_p,
                "raw_error": raw_error,
                "e0": norm_e0,
                "corrected_error": corrected_error
            }
        }
