from database import SessionLocal, engine
import models
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(models.Instrument).first():
            print("Database already seeded.")
            return

        print("Seeding database...")
        
        # 1. Add Instrument
        instrument = models.Instrument(
            manufacturer="Mettler Toledo",
            model="MS205DU",
            instrument_type="NAWI",
            accuracy_class="III",
            min_capacity=0.2,
            max_capacity=30,
            verification_interval_e=0.01, # 10g in kg
            number_of_intervals=3000,
            configuration_json={"platform_size": "200x200mm"}
        )
        db.add(instrument)
        db.commit()
        db.refresh(instrument)

        # 2. Add RuleSet & Rules
        ruleset = models.RuleSet(
            standard="OIML R76",
            edition="2006",
            version="1.0",
            effective_from=datetime.utcnow(),
            status="PUBLISHED",
            checksum="abc123hash"
        )
        db.add(ruleset)
        db.commit()
        db.refresh(ruleset)

        rule_mpe = models.Rule(
            ruleset_id=ruleset.id,
            code="R76-1 3.5.1",
            name="Maximum Permissible Errors",
            conditions_json={"class": "III"},
            formula_definition={"type": "step_function"},
            decision_definition={"operator": "<=", "target": "mpe"},
            references_json={"section": "3.5.1"}
        )
        db.add(rule_mpe)
        db.commit()
        db.refresh(rule_mpe)

        # 3. Add Test Definition
        test_weighing = models.TestDefinition(
            code="WP-01",
            name="Weighing Performance",
            description="Determination of errors of indication",
            category="Metrological",
            input_schema={"load": "float", "indication": "float"},
            calculation_rule_id=rule_mpe.id,
            decision_rule_id=rule_mpe.id
        )
        db.add(test_weighing)
        db.commit()
        db.refresh(test_weighing)

        # 4. Add Test Session for the instrument
        session = models.TestSession(
            instrument_id=instrument.id,
            ruleset_id=ruleset.id,
            started_by="Demo Tech",
            status="IN_PROGRESS"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # 5. Add an Observation placeholder
        observation = models.Observation(
            test_session_id=session.id,
            test_definition_id=test_weighing.id,
            raw_value=10.0,
            raw_unit="kg",
            sequence_no=1,
            metadata_json={"indication": 10.008, "indication_unit": "kg"}
        )
        db.add(observation)
        db.commit()

        print("Seeding complete.")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
