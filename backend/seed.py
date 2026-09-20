import os
import sys
import hashlib
from datetime import datetime, timedelta

from database import SessionLocal, engine
import models
from engine.calculation import CalculationEngine
from engine.rules import RuleEngine
from engine.evidence import EvidenceBuilder
from engine.report_generator import ReportGenerator

models.Base.metadata.create_all(bind=engine)

def seed(force: bool = False):
    db = SessionLocal()
    try:
        if force:
            print("Force flag set: dropping and recreating all database tables...")
            models.Base.metadata.drop_all(bind=engine)
            models.Base.metadata.create_all(bind=engine)
        else:
            existing = db.query(models.Instrument).first()
            if existing:
                print("Database already populated. To re-seed, run with force=True.")
                return

        print("Seeding CALIBRA metrology database...")

        # 1. Seed Reference Testing Locations
        locations_data = [
            {
                "name": "New Delhi Central Laboratory",
                "country": "India",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "elevation": 216.0,
                "declared_gravity": 9.7912,
                "description": "National Physical Laboratory / Central Legal Metrology Testing Center"
            },
            {
                "name": "Leh Ladakh High-Altitude Facility",
                "country": "India",
                "latitude": 34.1526,
                "longitude": 77.5771,
                "elevation": 3500.0,
                "declared_gravity": 9.7744,
                "description": "High-altitude testing laboratory. Low local gravity creates strong R76 Clause 3.9.2 dependency."
            },
            {
                "name": "Mumbai Coastal Verification Station",
                "country": "India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "elevation": 14.0,
                "declared_gravity": 9.7865,
                "description": "Port verification facility near sea level."
            },
            {
                "name": "METAS Bern / Zurich Reference Facility",
                "country": "Switzerland",
                "latitude": 47.3769,
                "longitude": 8.5417,
                "elevation": 408.0,
                "declared_gravity": 9.8066,
                "description": "European high-latitude metrology testing station."
            },
            {
                "name": "Singapore National Metrology Centre",
                "country": "Singapore",
                "latitude": 1.3521,
                "longitude": 103.8198,
                "elevation": 15.0,
                "declared_gravity": 9.7807,
                "description": "Equatorial verification baseline."
            }
        ]
        for loc in locations_data:
            db.add(models.Location(**loc))
        db.commit()

        # 2. Seed Test Standards & Equipment Registry
        now = datetime.utcnow()
        equipment_data = [
            {
                "equipment_id": "EQ-E2-001",
                "name": "Class E2 Stainless Steel Weight Set (1mg - 500g)",
                "equipment_type": "STANDARD_WEIGHTS",
                "class_standard": "E2",
                "manufacturer": "Häfner Gewichte",
                "model": "E2-Precision",
                "serial_number": "HAF-2024-8891",
                "calibration_date": now - timedelta(days=60),
                "calibration_expiry": now + timedelta(days=305),
                "certificate_number": "NPL-IND-CAL-2026-041",
                "traceability_reference": "NPL/SI/MASS-01",
                "status": "VALID"
            },
            {
                "equipment_id": "EQ-F1-002",
                "name": "Class F1 Cylindrical Weights (1kg - 20kg)",
                "equipment_type": "STANDARD_WEIGHTS",
                "class_standard": "F1",
                "manufacturer": "Troemner LLC",
                "model": "F1-Industrial",
                "serial_number": "TRM-99214",
                "calibration_date": now - timedelta(days=90),
                "calibration_expiry": now + timedelta(days=275),
                "certificate_number": "NPL-IND-CAL-2026-118",
                "traceability_reference": "NPL/SI/MASS-02",
                "status": "VALID"
            },
            {
                "equipment_id": "EQ-M1-003",
                "name": "Class M1 Cast Iron Grip Handle Weights (50kg x 4)",
                "equipment_type": "STANDARD_WEIGHTS",
                "class_standard": "M1",
                "manufacturer": "Mettler Toledo",
                "model": "M1-Block",
                "serial_number": "MT-M1-4401",
                "calibration_date": now - timedelta(days=120),
                "calibration_expiry": now + timedelta(days=245),
                "certificate_number": "NPL-IND-CAL-2026-250",
                "traceability_reference": "NPL/SI/MASS-04",
                "status": "VALID"
            },
            {
                "equipment_id": "EQ-EXP-004",
                "name": "Class M2 Trade Weights Set (5kg - 20kg)",
                "equipment_type": "STANDARD_WEIGHTS",
                "class_standard": "M2",
                "manufacturer": "Standard Scales Co",
                "model": "M2-Trade",
                "serial_number": "STD-8812",
                "calibration_date": now - timedelta(days=400),
                "calibration_expiry": now - timedelta(days=35), # Expired!
                "certificate_number": "OLD-STATE-CAL-2025-001",
                "traceability_reference": "EXPIRED/REVOKED",
                "status": "EXPIRED"
            }
        ]
        for eq in equipment_data:
            db.add(models.TestEquipment(**eq))
        db.commit()

        # 3. Seed RuleSets
        ruleset_r76 = models.RuleSet(
            standard="OIML R76-1",
            edition="2006",
            version="OIML R76-1:2006",
            effective_from=datetime(2006, 1, 1),
            status="ACTIVE",
            checksum="sha256:76f9d261e4a1a382c7a9b09f7a5b3a4e"
        )
        db.add(ruleset_r76)
        db.commit()
        db.refresh(ruleset_r76)

        # 4. Seed Test Definitions
        test_defs = [
            {"code": "ADM-01", "name": "Administrative & Markings Examination", "description": "Verification of markings, class oval, serial and software version per Clause 3.1 & 7.1", "category": "Administrative"},
            {"code": "ZT-01", "name": "Zero-Setting & Zero-Tracking", "description": "Verification of zero-setting range per Clause 4.5 & A.4.1.2", "category": "Zero Operations"},
            {"code": "WP-01", "name": "Weighing Performance at Min", "description": "Indication error at Minimum Capacity (Min) per Clause 3.5.1", "category": "Weighing Performance"},
            {"code": "WP-02", "name": "Weighing Performance at 500e", "description": "Indication error at 500e boundary per Table 6", "category": "Weighing Performance"},
            {"code": "WP-03", "name": "Weighing Performance at 2000e", "description": "Indication error at 2000e boundary per Table 6", "category": "Weighing Performance"},
            {"code": "WP-04", "name": "Weighing Performance at Max", "description": "Indication error at Maximum Capacity (Max) per Clause 3.5.1", "category": "Weighing Performance"},
            {"code": "RP-01", "name": "Repeatability at 0.5 Max", "description": "Spread of 3 successive weighings at half capacity per Clause 3.6.1", "category": "Repeatability"},
            {"code": "RP-02", "name": "Repeatability at Max", "description": "Spread of 3 successive weighings at full capacity per Clause 3.6.1", "category": "Repeatability"},
            {"code": "EC-01", "name": "Eccentricity Test (1/3 Max)", "description": "Error in 4 quadrants and center of load receiver per Clause 3.6.2", "category": "Eccentricity"},
            {"code": "TR-01", "name": "Tare Balancing & Tare Weighing", "description": "Verification of tare operation per Clause 4.6", "category": "Tare Operation"}
        ]
        def_map = {}
        for td in test_defs:
            obj = models.TestDefinition(**td)
            db.add(obj)
            db.flush()
            def_map[td["code"]] = obj
        db.commit()

        # 5. Seed Instruments
        # Instrument 1: Class III Commercial Scale (Delhi, gravity sensitive, no internal cal)
        inst1 = models.Instrument(
            manufacturer="Mettler Toledo",
            model="bC-U2 Commercial Scale",
            serial_number="MT-2026-30K-01",
            instrument_type="NAWI",
            accuracy_class="III",
            min_capacity=0.2, # 200g
            max_capacity=30.0, # 30kg
            verification_interval_e=10.0, # 10g
            scale_interval_d=10.0,
            number_of_intervals=3000,
            load_receiver="Platform (300 x 400 mm)",
            indication_type="Digital Dual-Display",
            software_version="v2.4.1",
            has_internal_calibration=False,
            is_gravity_sensitive=True,
            test_location="New Delhi Central Laboratory",
            intended_location="New Delhi Central Laboratory",
            configuration_json={"e_unit": "g", "max_unit": "kg", "min_unit": "kg"},
            status="ACTIVE"
        )
        db.add(inst1)

        # Instrument 2: Class II Analytical Precision Balance (Zurich, automatic internal calibration)
        inst2 = models.Instrument(
            manufacturer="Sartorius AG",
            model="Secura 225D-1S Micro-Analytical",
            serial_number="SAR-2026-ANA-901",
            instrument_type="NAWI",
            accuracy_class="II",
            min_capacity=0.02, # 20g
            max_capacity=0.22, # 220g
            verification_interval_e=0.01, # 0.01g = 10mg
            scale_interval_d=0.001,
            number_of_intervals=22000,
            load_receiver="Pan (diameter 90 mm) with Draft Shield",
            indication_type="Digital Touchscreen",
            software_version="v3.1.0-iso",
            has_internal_calibration=True, # Self-calibrating!
            is_gravity_sensitive=False,
            test_location="METAS Bern / Zurich Reference Facility",
            intended_location="New Delhi Central Laboratory",
            configuration_json={"e_unit": "g", "max_unit": "kg", "min_unit": "kg"},
            status="ACTIVE"
        )
        db.add(inst2)

        # Instrument 3: Class IIII Heavy Vehicle Weighbridge (Mumbai)
        inst3 = models.Instrument(
            manufacturer="Avery Weigh-Tronix",
            model="BridgeMont Heavy Heavy Duty 50T",
            serial_number="AWT-50T-WB-04",
            instrument_type="NAWI",
            accuracy_class="IIII",
            min_capacity=400.0, # 400kg
            max_capacity=50000.0, # 50,000kg (50t)
            verification_interval_e=20.0, # 20kg (20000g)
            scale_interval_d=20.0,
            number_of_intervals=2500,
            load_receiver="Steel Deck (18 x 3 m)",
            indication_type="Remote Digital Terminal",
            software_version="v1.0.8",
            has_internal_calibration=False,
            is_gravity_sensitive=True,
            test_location="Mumbai Coastal Verification Station",
            intended_location="Mumbai Coastal Verification Station",
            configuration_json={"e_unit": "kg", "max_unit": "kg", "min_unit": "kg"},
            status="ACTIVE"
        )
        db.add(inst3)
        db.commit()

        # 6. Seed Test Session 1 (Instrument 1 - PASS case)
        session1 = models.TestSession(
            instrument_id=inst1.id,
            ruleset_id=ruleset_r76.id,
            started_by="Senior Inspector Verma",
            verification_type="INITIAL",
            status="COMPLETED"
        )
        db.add(session1)
        db.commit()
        db.refresh(session1)

        # Seed ComplianceContext for Session 1
        ctx1 = models.ComplianceContext(
            instrument_id=inst1.id,
            test_session_id=session1.id,
            test_location="New Delhi Central Laboratory",
            intended_location="New Delhi Central Laboratory",
            latitude=28.6139,
            longitude=77.2090,
            elevation=216.0,
            local_gravity=9.7912,
            gravity_source="DECLARED",
            temperature_c=21.5,
            humidity_pct=52.0,
            equipment_calibration_status="VALID",
            is_transferable=True,
            transferability_status="TRANSFERABLE",
            transferability_reason="Test and intended location are identical (New Delhi Central Laboratory).",
            rule_set_version="OIML R76-1:2006"
        )
        db.add(ctx1)
        db.commit()

        # Observations & Evaluations for Session 1:
        # Test 1: WP-01 (Min = 0.2 kg = 200g, Indication = 0.200 kg)
        test_cases_s1 = [
            ("WP-01", 0.2, "kg", 0.200, "kg", None, None), # Load 200g, Ind 200g, Error 0g, MPE 5g -> PASS
            ("WP-02", 5.0, "kg", 5.002, "kg", 4.0, 1.0),   # Load 5kg (500e), delta_L 4g, e0 1g -> Ec = +2g, MPE 5g -> PASS
            ("WP-03", 20.0, "kg", 20.005, "kg", None, None), # Load 20kg (2000e), Ind 20.005kg, Error +5g, MPE 10g -> PASS
            ("WP-04", 30.0, "kg", 30.008, "kg", None, None), # Load 30kg (Max), Ind 30.008kg, Error +8g, MPE 15g -> PASS
        ]

        results_s1 = []
        for code, load_val, load_u, ind_val, ind_u, delta_l, e0 in test_cases_s1:
            t_def = def_map[code]
            meta = {"indication": ind_val, "indication_unit": ind_u}
            if delta_l is not None:
                meta["delta_l"] = delta_l
                meta["delta_l_unit"] = "g"
            if e0 is not None:
                meta["e0"] = e0
                meta["e0_unit"] = "g"

            obs = models.Observation(
                test_session_id=session1.id,
                test_definition_id=t_def.id,
                raw_value=load_val,
                raw_unit=load_u,
                sequence_no=1,
                metadata_json=meta
            )
            db.add(obs)
            db.flush()

            trace = CalculationEngine.process_observation(
                raw_load=load_val,
                load_unit=load_u,
                raw_indication=ind_val,
                ind_unit=ind_u,
                raw_e=inst1.verification_interval_e,
                e_unit="g",
                raw_delta_l=delta_l,
                delta_l_unit="g" if delta_l else None,
                raw_e0=e0,
                e0_unit="g" if e0 else None,
                base_unit="g"
            )

            load_g = trace["_internal_decimals"]["norm_load"]
            e_g = trace["_internal_decimals"]["norm_e"]
            err_g = trace["_internal_decimals"]["corrected_error"]
            clean_trace = {k: v for k, v in trace.items() if k != "_internal_decimals"}

            eval_res = RuleEngine.evaluate_mpe_rule(
                accuracy_class=inst1.accuracy_class,
                load_norm=load_g,
                e_norm=e_g,
                error_norm=err_g,
                max_norm=CalculationEngine.normalize(inst1.max_capacity, "kg", "g"),
                min_norm=CalculationEngine.normalize(inst1.min_capacity, "kg", "g"),
                verification_type="INITIAL"
            )

            ev_data = EvidenceBuilder.build_evidence(
                instrument=inst1,
                observation=obs,
                trace=clean_trace,
                evaluation=eval_res,
                verification_type="INITIAL"
            )

            db_ev = models.Evidence(
                input_snapshot_json=ev_data["raw_input"],
                normalization_json=ev_data["normalization"],
                calculation_trace_json=ev_data["calculation"],
                rule_snapshot_json=ev_data["rule"],
                decision_snapshot_json=ev_data["decision"]
            )
            db.add(db_ev)
            db.flush()

            res = models.TestResult(
                test_session_id=session1.id,
                test_definition_id=t_def.id,
                status="PASS",
                calculated_values_json=clean_trace,
                decision_reason=ev_data["decision"]["explanation"],
                evidence_id=db_ev.id
            )
            db.add(res)
            db.flush()
            results_s1.append(res)

        db.commit()

        # 7. Generate Seed PDF Report for Session 1
        reports_dir = "./reports_out"
        os.makedirs(reports_dir, exist_ok=True)
        rep_file = os.path.join(reports_dir, "CALIBRA_Report_Session_1_Rev1.pdf")
        
        all_eq = db.query(models.TestEquipment).all()
        ReportGenerator.generate_pdf_report(
            session=session1,
            results=results_s1,
            filepath=rep_file,
            context=ctx1,
            equipment_list=all_eq
        )

        with open(rep_file, "rb") as f:
            pdf_hash = hashlib.sha256(f.read()).hexdigest()

        rep_record = models.Report(
            session_id=session1.id,
            report_number="CALIBRA-R76-0001-REV1",
            revision=1,
            ruleset_version="OIML R76-1:2006",
            calculation_version="v1.0-decimal34",
            status="FINAL",
            checksum_sha256=pdf_hash,
            generated_by="Senior Inspector Verma",
            pdf_path=rep_file,
            summary_json={
                "coverage_percentage": 100.0,
                "total_tests": len(results_s1),
                "passed_tests": len(results_s1),
                "failed_tests": 0,
                "is_transferable": True
            }
        )
        db.add(rep_record)

        # 8. Seed Session 2 (FAIL Demo Case)
        session2 = models.TestSession(
            instrument_id=inst1.id,
            ruleset_id=ruleset_r76.id,
            started_by="Inspector Sharma",
            verification_type="INITIAL",
            status="IN_PROGRESS"
        )
        db.add(session2)
        db.commit()
        db.refresh(session2)

        # Deliberate FAIL test on Session 2: Load 10kg, Indication 10.018kg, turning point delta_L = 4g, zero error E0 = 2g
        # P = 10.018 + 5 - 4 = 10.019 kg => Raw E = +19g, Ec = +17g > MPE ±10g => FAIL!
        t_wp = def_map["WP-03"]
        obs_fail = models.Observation(
            test_session_id=session2.id,
            test_definition_id=t_wp.id,
            raw_value=10.0,
            raw_unit="kg",
            sequence_no=1,
            metadata_json={"indication": 10.018, "indication_unit": "kg", "delta_l": 4.0, "delta_l_unit": "g", "e0": 2.0, "e0_unit": "g"}
        )
        db.add(obs_fail)
        db.flush()

        trace_fail = CalculationEngine.process_observation(
            raw_load=10.0,
            load_unit="kg",
            raw_indication=10.018,
            ind_unit="kg",
            raw_e=inst1.verification_interval_e,
            e_unit="g",
            raw_delta_l=4.0,
            delta_l_unit="g",
            raw_e0=2.0,
            e0_unit="g",
            base_unit="g"
        )
        clean_fail_trace = {k: v for k, v in trace_fail.items() if k != "_internal_decimals"}

        eval_fail = RuleEngine.evaluate_mpe_rule(
            accuracy_class=inst1.accuracy_class,
            load_norm=trace_fail["_internal_decimals"]["norm_load"],
            e_norm=trace_fail["_internal_decimals"]["norm_e"],
            error_norm=trace_fail["_internal_decimals"]["corrected_error"],
            max_norm=CalculationEngine.normalize(inst1.max_capacity, "kg", "g"),
            min_norm=CalculationEngine.normalize(inst1.min_capacity, "kg", "g"),
            verification_type="INITIAL"
        )

        ev_fail = EvidenceBuilder.build_evidence(
            instrument=inst1,
            observation=obs_fail,
            trace=clean_fail_trace,
            evaluation=eval_fail,
            verification_type="INITIAL"
        )

        db_ev_fail = models.Evidence(
            input_snapshot_json=ev_fail["raw_input"],
            normalization_json=ev_fail["normalization"],
            calculation_trace_json=ev_fail["calculation"],
            rule_snapshot_json=ev_fail["rule"],
            decision_snapshot_json=ev_fail["decision"]
        )
        db.add(db_ev_fail)
        db.flush()

        res_fail = models.TestResult(
            test_session_id=session2.id,
            test_definition_id=t_wp.id,
            status="FAIL",
            calculated_values_json=clean_fail_trace,
            decision_reason=ev_fail["decision"]["explanation"],
            evidence_id=db_ev_fail.id
        )
        db.add(res_fail)

        # 9. Seed Audit Trail Event
        audit = models.AuditEvent(
            actor_id="Senior Inspector Verma",
            action="REPORT_ISSUANCE",
            entity_type="Report",
            entity_id=1,
            before_json={"status": "IN_PROGRESS"},
            after_json={"status": "FINAL", "report_number": "CALIBRA-R76-0001-REV1", "checksum": pdf_hash},
            metadata_json={"verification_type": "INITIAL", "ruleset": "OIML R76-1:2006"}
        )
        db.add(audit)

        db.commit()
        print("CALIBRA seeding completed successfully.")
        print(f"• Seeded 5 reference testing locations (Delhi, Leh, Mumbai, Zurich, Singapore)")
        print(f"• Seeded 4 test equipment standards (including EQ-EXP-004 expired standard)")
        print(f"• Seeded 3 multi-class instruments (Class III, Class II, Class IIII)")
        print(f"• Seeded 10 OIML R76 test definitions")
        print(f"• Seeded Session 1 (PASS verified, Report #CALIBRA-R76-0001-REV1 generated)")
        print(f"• Seeded Session 2 (FAIL demo case with turning point derivation)")

    finally:
        db.close()

if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    seed(force=force_flag)
