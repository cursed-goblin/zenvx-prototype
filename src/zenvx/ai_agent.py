from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AgentAction:
    action: str
    requires_confirmation: bool
    risk: str
    explanation: str
    command: Optional[list[str]] = None
    dependency: Optional[str] = None


class MockAgent:
    name = "MockAgent"

    def answer(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        q = question.lower()
        actions: list[Dict[str, Any]] = []

        missing = context.get("missing_dependencies", [])
        if missing:
            dep = missing[0]
            actions.append(AgentAction("install_missing_dependency", True, "low", f"{dep} appears missing", ["sudo", "apt", "install", dep], dep).__dict__)

        if "waydroid" in q:
            actions.append(AgentAction("start_waydroid_session", True, "medium", "Waydroid session may be required", ["sudo", "systemctl", "start", "waydroid-container"]).__dict__)

        if "appimage" in q:
            actions.append(AgentAction("enable_appimage_extract_mode", False, "low", "Try APPIMAGE_EXTRACT_AND_RUN=1").__dict__)

        return {"backend": self.name, "answer": "Offline prototype agent; suggestions are advisory.", "actions": actions}


agent = MockAgent()
