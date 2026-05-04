from abc import ABC, abstractmethod
from app.models.schemas import WorkItemStatus, RCAModel
from typing import Optional

class StateError(Exception):
    pass

class WorkItemState(ABC):
    @abstractmethod
    def next_state(self) -> WorkItemStatus:
        pass

    def validate_transition(self, rca: Optional[RCAModel] = None):
        pass

class OpenState(WorkItemState):
    def next_state(self): return WorkItemStatus.INVESTIGATING

class InvestigatingState(WorkItemState):
    def next_state(self): return WorkItemStatus.RESOLVED

class ResolvedState(WorkItemState):
    def next_state(self): return WorkItemStatus.CLOSED

    def validate_transition(self, rca: Optional[RCAModel] = None):
        if not rca:
            raise StateError("RCA is required to move to CLOSED")
        if not rca.fix_applied or not rca.prevention_steps:
            raise StateError("RCA must have fix_applied and prevention_steps")

STATE_MAP = {
    WorkItemStatus.OPEN: OpenState(),
    WorkItemStatus.INVESTIGATING: InvestigatingState(),
    WorkItemStatus.RESOLVED: ResolvedState(),
}

def get_state(status: WorkItemStatus) -> WorkItemState:
    return STATE_MAP.get(status)
