"""
Phase 10: Regression Test of the Exact Failures from the Initial Validation Report
"""

import sys
import os
from decimal import Decimal

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from engine.calculation import CalculationEngine
from engine.rules import RuleEngine
from tests.independent_reference import OIMLR76ReferenceModel

def test_regression_failures():
    print("=================================================================")
    print("PHASE 10: REGRESSION TESTING EXACT REPORTED FAILURES")
    print("=================================================================")

    # 1. TC-03: L = 5 kg, I = 5.0051 kg, e = 10 g, Class III, Initial Verif
    trace_03 = CalculationEngine.process_observation(5.0, "kg", 5.0051, "kg", 10.0, "g")
    res_03 = RuleEngine.evaluate_mpe_rule("III", trace_03["_internal_decimals"]["norm_load"],
                                          trace_03["_internal_decimals"]["norm_e"],
                                          trace_03["_internal_decimals"]["corrected_error"],
                                          max_norm=Decimal("30000.0"), verification_type="INITIAL")
    print(f"[TC-03] L=5kg, I=5.0051kg -> MPE={res_03['threshold']}g (Expected: 5.0g) | Status={res_03['status']} (Expected: FAIL)")
    assert res_03["threshold"] == 5.0, f"Expected MPE=5.0g, got {res_03['threshold']}"
    assert res_03["status"] == "FAIL", f"Expected FAIL, got {res_03['status']}"

    # 2. TC-06: L = 20 kg, I = 20.011 kg, e = 10 g, Class III, Initial Verif
    trace_06 = CalculationEngine.process_observation(20.0, "kg", 20.011, "kg", 10.0, "g")
    res_06 = RuleEngine.evaluate_mpe_rule("III", trace_06["_internal_decimals"]["norm_load"],
                                          trace_06["_internal_decimals"]["norm_e"],
                                          trace_06["_internal_decimals"]["corrected_error"],
                                          max_norm=Decimal("30000.0"), verification_type="INITIAL")
    print(f"[TC-06] L=20kg, I=20.011kg -> MPE={res_06['threshold']}g (Expected: 10.0g) | Status={res_06['status']} (Expected: FAIL)")
    assert res_06["threshold"] == 10.0, f"Expected MPE=10.0g, got {res_06['threshold']}"
    assert res_06["status"] == "FAIL", f"Expected FAIL, got {res_06['status']}"

    # 3. TC-11: L = 10 kg, I = 9.988 kg, e = 10 g, Class III, Initial Verif
    trace_11 = CalculationEngine.process_observation(10.0, "kg", 9.988, "kg", 10.0, "g")
    res_11 = RuleEngine.evaluate_mpe_rule("III", trace_11["_internal_decimals"]["norm_load"],
                                          trace_11["_internal_decimals"]["norm_e"],
                                          trace_11["_internal_decimals"]["corrected_error"],
                                          max_norm=Decimal("30000.0"), verification_type="INITIAL")
    print(f"[TC-11] L=10kg, I=9.988kg -> MPE={res_11['threshold']}g (Expected: 10.0g) | Status={res_11['status']} (Expected: FAIL)")
    assert res_11["threshold"] == 10.0
    assert res_11["status"] == "FAIL"

    # 4. TC-15: L = 35 kg, Max = 30 kg, e = 10 g -> Expected INVALID (overload)
    trace_15 = CalculationEngine.process_observation(35.0, "kg", 35.010, "kg", 10.0, "g")
    res_15 = RuleEngine.evaluate_mpe_rule("III", trace_15["_internal_decimals"]["norm_load"],
                                          trace_15["_internal_decimals"]["norm_e"],
                                          trace_15["_internal_decimals"]["corrected_error"],
                                          max_norm=Decimal("30000.0"), verification_type="INITIAL")
    print(f"[TC-15] Overload 35kg on 30kg Max -> Status={res_15['status']} (Expected: INVALID) | Code={res_15.get('error_code')}")
    assert res_15["status"] == "INVALID"
    assert res_15["error_code"] == "OVERLOAD_EXCEEDS_MAX_PLUS_9E"

    # 5. TC-17: e = 0 -> Clean validation error, no crash
    res_17 = RuleEngine.evaluate_mpe_rule("III", Decimal("10000.0"), Decimal("0.0"), Decimal("0.0"), max_norm=Decimal("30000.0"))
    print(f"[TC-17] e = 0 -> Status={res_17['status']} (Expected: INVALID) | Code={res_17.get('error_code')}")
    assert res_17["status"] == "INVALID"
    assert res_17["error_code"] == "INVALID_VERIFICATION_INTERVAL"

    # 6. TC-18: Class II -> Valid Class II evaluation
    trace_18 = CalculationEngine.process_observation(100.0, "g", 100.005, "g", 0.01, "g")
    res_18 = RuleEngine.evaluate_mpe_rule("II", trace_18["_internal_decimals"]["norm_load"],
                                          trace_18["_internal_decimals"]["norm_e"],
                                          trace_18["_internal_decimals"]["corrected_error"],
                                          max_norm=Decimal("200.0"))
    print(f"[TC-18] Class II -> Status={res_18['status']} (Expected: PASS) | MPE={res_18['threshold']}g")
    assert res_18["status"] == "PASS"
    assert res_18["threshold"] == 0.01

    # 7. TC-19: Class I -> Valid Class I evaluation
    trace_19 = CalculationEngine.process_observation(60.0, "g", 60.0008, "g", 0.001, "g")
    res_19 = RuleEngine.evaluate_mpe_rule("I", trace_19["_internal_decimals"]["norm_load"],
                                          trace_19["_internal_decimals"]["norm_e"],
                                          trace_19["_internal_decimals"]["corrected_error"],
                                          max_norm=Decimal("100.0"))
    print(f"[TC-19] Class I -> Status={res_19['status']} (Expected: PASS) | MPE={res_19['threshold']}g")
    assert res_19["status"] == "PASS"
    assert res_19["threshold"] == 0.001

    # 8. TC-20: Class IIII -> Valid Class IIII evaluation
    trace_20 = CalculationEngine.process_observation(75.0, "kg", 75.05, "kg", 0.5, "kg")
    res_20 = RuleEngine.evaluate_mpe_rule("IIII", trace_20["_internal_decimals"]["norm_load"],
                                          trace_20["_internal_decimals"]["norm_e"],
                                          trace_20["_internal_decimals"]["corrected_error"],
                                          max_norm=Decimal("500000.0"))
    print(f"[TC-20] Class IIII -> Status={res_20['status']} (Expected: PASS) | MPE={res_20['threshold']}g")
    assert res_20["status"] == "PASS"
    assert res_20["threshold"] == 500.0

    # 9. TC-21: Digital Turning Point -> Delta L participates in calculation
    trace_21 = CalculationEngine.process_observation(
        raw_load=10.0, load_unit="kg",
        raw_indication=10.00, ind_unit="kg",
        raw_e=10.0, e_unit="g",
        raw_delta_l=4.0, delta_l_unit="g"
    )
    # P = 10000 + 5 - 4 = 10001 g. Error = 10001 - 10000 = +1.0 g
    p_val = trace_21["_internal_decimals"]["norm_p"]
    err_val = trace_21["_internal_decimals"]["corrected_error"]
    print(f"[TC-21] Digital Turning Point: delta_L=4.0g -> P={p_val}g (Expected: 10001.0g), Ec={err_val}g (Expected: 1.0g)")
    assert p_val == Decimal("10001.0")
    assert err_val == Decimal("1.0")

    # 10. TC-22: E0 Correction -> Ec = E - E0
    trace_22 = CalculationEngine.process_observation(
        raw_load=10.0, load_unit="kg",
        raw_indication=10.012, ind_unit="kg",
        raw_e=10.0, e_unit="g",
        raw_e0=4.0, e0_unit="g"
    )
    raw_e = trace_22["_internal_decimals"]["raw_error"]
    ec_val = trace_22["_internal_decimals"]["corrected_error"]
    print(f"[TC-22] Zero Correction: Raw E={raw_e}g, E0=4.0g -> Corrected Ec={ec_val}g (Expected: 8.0g)")
    assert raw_e == Decimal("12.0")
    assert ec_val == Decimal("8.0")

    print("\n--> ALL 10 PREVIOUSLY FAILING TEST CASES SUCCESSFULLY REGRESSION-VERIFIED!")
    return True

if __name__ == "__main__":
    test_regression_failures()
