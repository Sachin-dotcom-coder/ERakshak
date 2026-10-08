"""incidents — Incident detection modules for E-Rakshak vision service."""
from pathlib import Path
import importlib.util

from incidents.emergency import EmergencyVehicleDetector
from incidents.brts import BRTSViolationDetector
from incidents.wrong_way import WrongWayDetector
from incidents.breakdown import BreakdownDetector

# Backward compatibility for legacy IncidentDetector and StallAlert
_root_incidents_file = Path(__file__).resolve().parent.parent / "incidents.py"
if _root_incidents_file.exists():
    _spec = importlib.util.spec_from_file_location("_legacy_incidents", _root_incidents_file)
    if _spec and _spec.loader:
        _legacy_mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_legacy_mod)
        IncidentDetector = getattr(_legacy_mod, "IncidentDetector", None)
        StallAlert = getattr(_legacy_mod, "StallAlert", None)

__all__ = [
    "EmergencyVehicleDetector",
    "BRTSViolationDetector",
    "WrongWayDetector",
    "BreakdownDetector",
    "IncidentDetector",
    "StallAlert",
]
