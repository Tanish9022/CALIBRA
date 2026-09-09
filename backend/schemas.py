from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class InstrumentBase(BaseModel):
    manufacturer: str
    model: str
    instrument_type: str
    accuracy_class: str
    min_capacity: float
    max_capacity: float
    verification_interval_e: float
    number_of_intervals: int
    configuration_json: Dict[str, Any]
    status: str = "ACTIVE"

class InstrumentCreate(InstrumentBase):
    pass

class Instrument(InstrumentBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TestSessionCreate(BaseModel):
    instrument_id: int
    ruleset_id: int
    started_by: str = "Demo User"

class TestSession(BaseModel):
    id: int
    instrument_id: int
    ruleset_id: int
    started_by: str
    status: str
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
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
