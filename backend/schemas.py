from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class InstrumentBase(BaseModel):
    manufacturer: str
    model: str
    serial_number: Optional[str] = "SN-2026-001"
    instrument_type: str = "NAWI"
    accuracy_class: str = "III"
    min_capacity: float
    max_capacity: float
    verification_interval_e: float
    scale_interval_d: Optional[float] = None
    number_of_intervals: Optional[int] = None
    load_receiver: Optional[str] = "Platform"
    indication_type: Optional[str] = "Digital"
    software_version: Optional[str] = "v1.0.0"
    has_internal_calibration: Optional[bool] = False
    is_gravity_sensitive: Optional[bool] = True
    test_location: Optional[str] = "New Delhi Laboratory"
    intended_location: Optional[str] = "New Delhi Laboratory"
    configuration_json: Optional[Dict[str, Any]] = None
    status: str = "ACTIVE"

class InstrumentCreate(InstrumentBase):
    pass

class Instrument(InstrumentBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ComplianceContextBase(BaseModel):
    instrument_id: Optional[int] = None
    test_session_id: Optional[int] = None
    test_location: str
    intended_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[float] = None
    local_gravity: float
    gravity_source: str = "DECLARED" # DECLARED, MEASURED, ESTIMATED
    temperature_c: Optional[float] = 20.0
    humidity_pct: Optional[float] = 50.0
    equipment_calibration_status: Optional[str] = "VALID"
    is_transferable: Optional[bool] = True
    transferability_status: Optional[str] = "TRANSFERABLE"
    transferability_reason: Optional[str] = None
    rule_set_version: Optional[str] = "OIML R76-1:2006"

class ComplianceContextCreate(ComplianceContextBase):
    pass

class ComplianceContext(ComplianceContextBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LocationBase(BaseModel):
    name: str
    country: str = "India"
    latitude: float
    longitude: float
    elevation: float
    declared_gravity: float
    description: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TestEquipmentBase(BaseModel):
    equipment_id: str
    name: str
    equipment_type: str
    class_standard: Optional[str] = "M1"
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    calibration_date: Optional[datetime] = None
    calibration_expiry: Optional[datetime] = None
    certificate_number: Optional[str] = None
    traceability_reference: Optional[str] = None
    status: str = "VALID"

class TestEquipmentCreate(TestEquipmentBase):
    pass

class TestEquipment(TestEquipmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TestSessionCreate(BaseModel):
    instrument_id: int
    ruleset_id: int = 1
    started_by: str = "Operator"
    verification_type: str = "INITIAL"

class TestSession(BaseModel):
    id: int
    instrument_id: int
    ruleset_id: int
    started_by: str
    reviewer_id: Optional[str] = None
    status: str
    verification_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ObservationCreate(BaseModel):
    test_definition_id: int
    raw_value: float
    raw_unit: str
    sequence_no: int = 1
    metadata_json: Optional[Dict[str, Any]] = None

class Observation(ObservationCreate):
    id: int
    test_session_id: int
    normalized_value: Optional[float] = None
    normalized_unit: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportBase(BaseModel):
    session_id: int
    report_number: str
    revision: int = 1
    ruleset_version: str = "OIML R76-1:2006"
    calculation_version: str = "v1.0-decimal34"
    status: str = "FINAL"
    checksum_sha256: str
    generated_by: str
    reviewer_id: Optional[str] = None
    pdf_path: str
    summary_json: Optional[Dict[str, Any]] = None

class Report(ReportBase):
    id: int
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
