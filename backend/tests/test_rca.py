import pytest
from app.services.work_item_state import ResolvedState, StateError
from app.models.schemas import RCAModel, RootCauseCategory
from datetime import datetime

def test_rca_required_for_close():
    state = ResolvedState()
    with pytest.raises(StateError):
        state.validate_transition(rca=None)

def test_rca_incomplete_raises():
    state = ResolvedState()
    rca = RCAModel(
        incident_start=datetime(2024,1,1,10,0),
        incident_end=datetime(2024,1,1,12,0),
        root_cause_category=RootCauseCategory.DATABASE,
        fix_applied="",
        prevention_steps=""
    )
    with pytest.raises(StateError):
        state.validate_transition(rca=rca)

def test_valid_rca_passes():
    state = ResolvedState()
    rca = RCAModel(
        incident_start=datetime(2024,1,1,10,0),
        incident_end=datetime(2024,1,1,12,0),
        root_cause_category=RootCauseCategory.DATABASE,
        fix_applied="Restarted DB replica",
        prevention_steps="Added read replica health checks"
    )
    state.validate_transition(rca=rca)  # Should not raise
