from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String, index=True)
    model = Column(String, index=True)
    instrument_type = Column(String)
    accuracy_class = Column(String)
    min_capacity = Column(Float)
    max_capacity = Column(Float)
    verification_interval_e = Column(Float)
    number_of_intervals = Column(Integer)
    configuration_json = Column(JSON)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("TestSession", back_populates="instrument")

class TestSession(Base):
    __tablename__ = "test_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"))
    ruleset_id = Column(Integer, ForeignKey("rulesets.id"))
    started_by = Column(String)
    reviewer_id = Column(String, nullable=True)
    status = Column(String, default="DRAFT") # DRAFT, IN_PROGRESS, REVIEW, COMPLETED
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    instrument = relationship("Instrument", back_populates="sessions")
    observations = relationship("Observation", back_populates="session")
    results = relationship("TestResult", back_populates="session")
    ruleset = relationship("RuleSet")

class TestDefinition(Base):
    __tablename__ = "test_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)
    applicability_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    input_schema = Column(JSON)
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
    sequence_no = Column(Integer)
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
    effective_from = Column(DateTime)
    effective_to = Column(DateTime, nullable=True)
    status = Column(String) # DRAFT, VALIDATED, PUBLISHED, RETIRED
    checksum = Column(String)
    
    rules = relationship("Rule", back_populates="ruleset")

class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    ruleset_id = Column(Integer, ForeignKey("rulesets.id"))
    code = Column(String, index=True)
    name = Column(String)
    conditions_json = Column(JSON)
    formula_definition = Column(JSON)
    decision_definition = Column(JSON)
    references_json = Column(JSON)
    
    ruleset = relationship("RuleSet", back_populates="rules")

class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_session_id = Column(Integer, ForeignKey("test_sessions.id"))
    test_definition_id = Column(Integer, ForeignKey("test_definitions.id"))
    status = Column(String) # PASS, FAIL, REVIEW, NOT_APPLICABLE
    calculated_values_json = Column(JSON)
    decision_reason = Column(Text)
    evidence_id = Column(Integer, ForeignKey("evidence.id"))
    
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
