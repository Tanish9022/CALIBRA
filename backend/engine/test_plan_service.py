from typing import Dict, Any, List, Optional
from decimal import Decimal

class TestPlanService:
    """
    Dynamic OIML R76 Requirement Compiler & Test Plan Service.
    
    Generates tailored test plans based on:
    - Instrument Profile (Class I, II, III, IIII, Max, Min, e, d)
    - Configuration (has tare, auto-zero, electronic indication)
    - Compliance Context (initial verification vs in-service)
    """

    MASTER_CATALOG = [
        {
            "code": "ADM-01",
            "title": "Administrative & Markings Examination",
            "clause": "OIML R76-1:2006 Clause 3.1 & 7.1",
            "category": "Visual / Administrative",
            "description": "Verification of descriptive markings, accuracy class oval, Max, Min, e, serial number, and software version.",
            "mandatory": True,
            "min_observations": 1,
            "evidence_required": ["nameplate_photo"]
        },
        {
            "code": "ZT-01",
            "title": "Zero-Setting & Zero-Tracking Range",
            "clause": "OIML R76-1:2006 Clause 4.5 & A.4.1.2",
            "category": "Zero Operations",
            "description": "Verification that initial and semi-automatic zero-setting is within 4% of Max (or 20% for initial zero).",
            "mandatory": True,
            "min_observations": 1,
            "evidence_required": []
        },
        {
            "code": "WP-01",
            "title": "Weighing Performance at Min",
            "clause": "OIML R76-1:2006 Clause 3.5.1 & A.4.4.1",
            "category": "Weighing Performance",
            "description": "Determination of indication error at Minimum Capacity (Min).",
            "load_point": "Min",
            "mandatory": True,
            "min_observations": 1,
            "evidence_required": ["turning_point_log"]
        },
        {
            "code": "WP-02",
            "title": "Weighing Performance at 500e (Step 1 Boundary)",
            "clause": "OIML R76-1:2006 Clause 3.5.1 & Table 6",
            "category": "Weighing Performance",
            "description": "Determination of error at or near the 500e change-of-error boundary.",
            "load_point": "500e",
            "mandatory": True,
            "min_observations": 1,
            "evidence_required": ["turning_point_log"]
        },
        {
            "code": "WP-03",
            "title": "Weighing Performance at 2000e (Step 2 Boundary)",
            "clause": "OIML R76-1:2006 Clause 3.5.1 & Table 6",
            "category": "Weighing Performance",
            "description": "Determination of error at or near the 2000e change-of-error boundary.",
            "load_point": "2000e",
            "mandatory": True,
            "min_observations": 1,
            "evidence_required": ["turning_point_log"]
        },
        {
            "code": "WP-04",
            "title": "Weighing Performance at Max",
            "clause": "OIML R76-1:2006 Clause 3.5.1 & A.4.4.1",
            "category": "Weighing Performance",
            "description": "Determination of indication error at Maximum Capacity (Max).",
            "load_point": "Max",
            "mandatory": True,
            "min_observations": 1,
            "evidence_required": ["turning_point_log"]
        },
        {
            "code": "RP-01",
            "title": "Repeatability Test at 0.5 Max",
            "clause": "OIML R76-1:2006 Clause 3.6.1 & A.4.5",
            "category": "Repeatability",
            "description": "At least 3 successive weighings with 50% Max load. Difference between max and min must not exceed |MPE|.",
            "mandatory": True,
            "min_observations": 3,
            "evidence_required": []
        },
        {
            "code": "RP-02",
            "title": "Repeatability Test at Max",
            "clause": "OIML R76-1:2006 Clause 3.6.1 & A.4.5",
            "category": "Repeatability",
            "description": "At least 3 successive weighings with 100% Max load. Difference between max and min must not exceed |MPE|.",
            "mandatory": True,
            "min_observations": 3,
            "evidence_required": []
        },
        {
            "code": "EC-01",
            "title": "Eccentricity Test (1/3 Max)",
            "clause": "OIML R76-1:2006 Clause 3.6.2 & A.4.7",
            "category": "Eccentricity",
            "description": "Load of approx 1/3 Max placed at center and each of the 4 quadrants of the load receptor.",
            "mandatory": True,
            "min_observations": 5,
            "evidence_required": ["quadrant_diagram"]
        },
        {
            "code": "TR-01",
            "title": "Tare Balancing & Weighing with Tare",
            "clause": "OIML R76-1:2006 Clause 4.6 & A.4.6",
            "category": "Tare Operation",
            "description": "Verification that tare mechanism operates properly and error with tare does not exceed MPE.",
            "mandatory": False,
            "min_observations": 1,
            "evidence_required": []
        }
    ]

    @classmethod
    def compile_test_plan(
        cls,
        accuracy_class: str,
        max_capacity_kg: float,
        verification_interval_e_g: float,
        verification_type: str = "INITIAL",
        has_tare: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Compiles the applicable test list for a given instrument.
        """
        tests = []
        max_g = Decimal(str(max_capacity_kg)) * Decimal("1000")
        e_g = Decimal(str(verification_interval_e_g))
        total_intervals_n = max_g / e_g

        for template in cls.MASTER_CATALOG:
            item = dict(template)
            
            # Check 2000e applicability: if instrument has fewer than 2000 intervals, skip WP-03
            if item["code"] == "WP-03" and total_intervals_n < Decimal("2000"):
                continue
                
            # Tare test only if instrument has tare feature
            if item["code"] == "TR-01" and not has_tare:
                continue

            item["status"] = "PENDING"
            tests.append(item)

        return tests
