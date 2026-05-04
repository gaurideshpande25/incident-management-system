from abc import ABC, abstractmethod
from app.models.schemas import Severity

class AlertStrategy(ABC):
    @abstractmethod
    async def send(self, component_id: str, message: str):
        pass

class P0AlertStrategy(AlertStrategy):
    async def send(self, component_id: str, message: str):
        print(f"🚨 [P0 CRITICAL] PagerDuty alert for {component_id}: {message}")

class P1AlertStrategy(AlertStrategy):
    async def send(self, component_id: str, message: str):
        print(f"🔴 [P1 HIGH] Slack alert for {component_id}: {message}")

class P2AlertStrategy(AlertStrategy):
    async def send(self, component_id: str, message: str):
        print(f"🟡 [P2 MEDIUM] Email alert for {component_id}: {message}")

class P3AlertStrategy(AlertStrategy):
    async def send(self, component_id: str, message: str):
        print(f"🟢 [P3 LOW] Log only for {component_id}: {message}")

ALERT_STRATEGIES = {
    Severity.P0: P0AlertStrategy(),
    Severity.P1: P1AlertStrategy(),
    Severity.P2: P2AlertStrategy(),
    Severity.P3: P3AlertStrategy(),
}

def get_alert_strategy(severity: Severity) -> AlertStrategy:
    return ALERT_STRATEGIES[severity]
