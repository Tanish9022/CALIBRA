import pytest
from decimal import Decimal
from engine.context.gravity_service import GravityContextService
from engine.context.impact_service import ImpactAnalysisService
from engine.coverage_gate import CoverageGate
from engine.test_plan_service import TestPlanService

def test_somigliana_gravity_estimation():
    # Delhi: Lat 28.6139, Elev 216m
    res = GravityContextService.estimate_gravity_somigliana(28.6139, 216.0)
    assert res["gravity_source"] == "ESTIMATED"
    assert 9.78 < res["estimated_gravity_ms2"] < 9.80
    assert res["free_air_correction_ms2"] < 0 # Elevation decreases gravity

    # High latitude (Zurich 47.37 deg) should have higher sea-level gravity than Delhi (28.61 deg)
    res_zurich = GravityContextService.estimate_gravity_somigliana(47.3769, 408.0)
    assert res_zurich["sea_level_gravity_ms2"] > res["sea_level_gravity_ms2"]

def test_gravity_transferability_delhi_to_leh():
    # Class III Commercial Scale, Max 30kg, e=10g, no internal cal
    eval_res = GravityContextService.evaluate_location_transferability(
        accuracy_class="III",
        max_capacity_kg=30.0,
        verification_interval_e_g=10.0,
        has_internal_calibration=False,
        is_gravity_sensitive=True,
        test_location_name="New Delhi",
        test_gravity_ms2=9.7912,
        intended_location_name="Leh Ladakh",
        intended_gravity_ms2=9.7744
    )
    # The relative shift is ~1715 ppm which exceeds MPE limit of 500 ppm
    assert eval_res["decision"] == "RE-TEST / LOCATION-SPECIFIC EVALUATION REQUIRED"
    assert eval_res["is_transferable"] is False
    assert eval_res["relative_delta_g_ppm"] > eval_res["relative_mpe_ppm"]

def test_internal_calibration_makes_instrument_transferable():
    # Even if moved from Delhi to Leh, self-calibrating balance is TRANSFERABLE
    eval_res = GravityContextService.evaluate_location_transferability(
        accuracy_class="II",
        max_capacity_kg=0.22,
        verification_interval_e_g=0.01,
        has_internal_calibration=True,
        is_gravity_sensitive=False,
        test_location_name="New Delhi",
        test_gravity_ms2=9.7912,
        intended_location_name="Leh Ladakh",
        intended_gravity_ms2=9.7744
    )
    assert eval_res["decision"] == "TRANSFERABLE"
    assert eval_res["is_transferable"] is True

def test_dynamic_test_plan_compilation():
    plan = TestPlanService.compile_test_plan("III", 30.0, 10.0, "INITIAL")
    codes = [p["code"] for p in plan]
    assert "ADM-01" in codes
    assert "WP-01" in codes
    assert "WP-04" in codes
    assert "RP-01" in codes
    assert "EC-01" in codes

def test_coverage_gate_blocks_on_missing_tests():
    plan = TestPlanService.compile_test_plan("III", 30.0, 10.0, "INITIAL")
    # Empty results
    gate = CoverageGate.evaluate_session_coverage(plan, [], [])
    assert gate["status"] == "BLOCKED"
    assert gate["is_ready_for_report"] is False
    assert gate["coverage_percentage"] == 0.0
