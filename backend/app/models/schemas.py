from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class WorkItemStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class RootCauseCategory(str, Enum):
    INFRASTRUCTURE = "INFRASTRUCTURE"
    APPLICATION = "APPLICATION"
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    HUMAN_ERROR = "HUMAN_ERROR"

class SignalIn(BaseModel):
    component_id: str
    error_code: str
    message: str
    severity: Severity
    metadata: dict = {}

class RCAModel(BaseModel):
    incident_start: datetime
    incident_end: datetime
    root_cause_category: RootCauseCategory
    fix_applied: str
    prevention_steps: str

class WorkItemUpdate(BaseModel):
    status: WorkItemStatus
    rca: Optional[RCAModel] = None
