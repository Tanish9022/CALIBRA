from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="TECHNICIAN") # TECHNICIAN, REVIEWER, ADMINISTRATOR, AUDITOR
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String, index=True)
    model = Column(String, index=True)
    serial_number = Column(String, index=True, nullable=True)
    instrument_type = Column(String, default="NAWI")
    accuracy_class = Column(String) # I, II, III, IIII
    min_capacity = Column(Float)
    max_capacity = Column(Float)
    verification_interval_e = Column(Float)
    scale_interval_d = Column(Float, nullable=True)
    number_of_intervals = Column(Integer, nullable=True)
    load_receiver = Column(String, default="Platform")
    indication_type = Column(String, default="Digital")
    software_version = Column(String, default="v1.0.0")
    has_internal_calibration = Column(Boolean, default=False)
    is_gravity_sensitive = Column(Boolean, default=True)
    test_location = Column(String, default="New Delhi Laboratory")
    intended_location = Column(String, default="New Delhi Laboratory")
    configuration_json = Column(JSON, nullable=True)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("TestSession", back_populates="instrument")
    contexts = relationship("ComplianceContext", back_populates="instrument")

class ComplianceContext(Base):
    __tablename__ = "compliance_contexts"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=True)
    test_location = Column(String)
    intended_location = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    elevation = Column(Float, nullable=True)
    local_gravity = Column(Float)
    gravity_source = Column(String, default="DECLARED") # DECLARED, MEASURED, ESTIMATED
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    equipment_calibration_status = Column(String, default="VALID") # VALID, EXPIRED
    is_transferable = Column(Boolean, default=True)
    transferability_status = Column(String, default="TRANSFERABLE") # TRANSFERABLE, CONDITIONAL, RE_TEST_REQUIRED
    transferability_reason = Column(Text, nullable=True)
    rule_set_version = Column(String, default="OIML R76-1:2006")
    created_at = Column(DateTime, default=datetime.utcnow)

    instrument = relationship("Instrument", back_populates="contexts")
    session = relationship("TestSession", back_populates="context")

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    country = Column(String, default="India")
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    declared_gravity = Column(Float)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TestEquipment(Base):
    __tablename__ = "test_equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String, unique=True, index=True)
    name = Column(String)
    equipment_type = Column(String) # STANDARD_WEIGHTS, CLIMATE_CHAMBER, MULTIMETER
    class_standard = Column(String, nullable=True) # E2, F1, F2, M1
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    calibration_date = Column(DateTime, nullable=True)
    calibration_expiry = Column(DateTime, nullable=True)
    certificate_number = Column(String, nullable=True)
    traceability_reference = Column(String, nullable=True)
    status = Column(String, default="VALID") # VALID, EXPIRED, MAINTENANCE
    created_at = Column(DateTime, default=datetime.utcnow)

class TestSession(Base):
    __tablename__ = "test_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"))
    ruleset_id = Column(Integer, ForeignKey("rulesets.id"))
    started_by = Column(String)
    reviewer_id = Column(String, nullable=True)
    status = Column(String, default="DRAFT") # DRAFT, IN_PROGRESS, REVIEW, COMPLETED
    verification_type = Column(String, default="INITIAL") # INITIAL, IN_SERVICE
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    instrument = relationship("Instrument", back_populates="sessions")
    observations = relationship("Observation", back_populates="session")
    results = relationship("TestResult", back_populates="session")
    ruleset = relationship("RuleSet")
    context = relationship("ComplianceContext", back_populates="session", uselist=False)
    reports = relationship("Report", back_populates="session")

class TestDefinition(Base):
    __tablename__ = "test_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)
    applicability_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    input_schema = Column(JSON, nullable=True)
    calculation_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    decision_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)

class Observation(Base):
    __tablename__ = "observations"
    
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"))
    test_definition_id = Column(Integer, ForeignKey("test_definitions.id"))
    raw_value = Column(Float)
    raw_unit = Column(String)
    normalized_value = Column(Float)
    normalized_unit = Column(String)
    sequence_no = Column(Integer, default=1)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("TestSession", back_populates="observations")
    test_definition = relationship("TestDefinition")

class RuleSet(Base):
    __tablename__ = "rulesets"
    
    id = Column(Integer, primary_key=True, index=True)
    standard = Column(String)
    edition = Column(String)
    version = Column(String)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)
    status = Column(String, default="ACTIVE") # DRAFT, VALIDATED, ACTIVE, RETIRED
    checksum = Column(String, nullable=True)
    
    rules = relationship("Rule", back_populates="ruleset")

class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    ruleset_id = Column(Integer, ForeignKey("rulesets.id"))
    code = Column(String, index=True)
    name = Column(String)
    conditions_json = Column(JSON, nullable=True)
    formula_definition = Column(JSON, nullable=True)
    decision_definition = Column(JSON, nullable=True)
    references_json = Column(JSON, nullable=True)
    
    ruleset = relationship("RuleSet", back_populates="rules")

class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"))
    test_definition_id = Column(Integer, ForeignKey("test_definitions.id"))
    status = Column(String) # PASS, FAIL, REVIEW, INVALID, NOT_APPLICABLE
    calculated_values_json = Column(JSON, nullable=True)
    decision_reason = Column(Text, nullable=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=True)
    
    session = relationship("TestSession", back_populates="results")
    test_definition = relationship("TestDefinition")
    evidence = relationship("Evidence")

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    input_snapshot_json = Column(JSON)
    normalization_json = Column(JSON)
    calculation_trace_json = Column(JSON)
    rule_snapshot_json = Column(JSON)
    decision_snapshot_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id"))
    report_number = Column(String, unique=True, index=True)
    revision = Column(Integer, default=1)
    ruleset_version = Column(String, default="OIML R76-1:2006")
    calculation_version = Column(String, default="v1.0-decimal34")
    status = Column(String, default="FINAL") # DRAFT, FINAL, AMENDED
    checksum_sha256 = Column(String)
    generated_by = Column(String)
    reviewer_id = Column(String, nullable=True)
    pdf_path = Column(String)
    summary_json = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("TestSession", back_populates="reports")

class ContextChangeRecord(Base):
    __tablename__ = "context_change_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id"))
    change_type = Column(String) # LOCATION_GRAVITY, ENVIRONMENT, EQUIPMENT, RULESET
    old_context_json = Column(JSON)
    new_context_json = Column(JSON)
    affected_tests_json = Column(JSON)
    recommended_action = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(String)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    before_json = Column(JSON, nullable=True)
    after_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
