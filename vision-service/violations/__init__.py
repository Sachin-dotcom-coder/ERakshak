"""
violations package — Violation detection modules for E-Rakshak
==============================================================
Provides both the legacy ViolationDetector (for backward compatibility)
and the upgraded state-machine engines:
- RLVEngine (Red-Light Violation state machine)
- BRTSEngine (BRTS corridor episode & intrusion state machine)
- StopLine utilities
"""

from .legacy import ViolationDetector, LaneViolation, BRTSIntrusion
BRTSViolation = BRTSIntrusion

from .stopline import StopLine, signed_dist, within_segment, crossing_time
from .rlv_engine import RLVEngine, TrackRLV, RLVConfig, S
from .brts_engine import BRTSEngine, BRTSEpisode, BRTSConfig
from .common import IDSwitchProtector, DedupManager, ExemptionChecker

__all__ = [
    "ViolationDetector",
    "LaneViolation",
    "BRTSIntrusion",
    "BRTSViolation",
    "StopLine",
    "signed_dist",
    "within_segment",
    "crossing_time",
    "RLVEngine",
    "TrackRLV",
    "RLVConfig",
    "S",
    "BRTSEngine",
    "BRTSEpisode",
    "BRTSConfig",
    "IDSwitchProtector",
    "DedupManager",
    "ExemptionChecker",
]
