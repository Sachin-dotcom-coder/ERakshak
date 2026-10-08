"""
evidence package — Evidence collection, RingBuffer, ANPR, and packet building
=============================================================================
"""

from .ring_buffer import RingBuffer
from .builder import EvidenceBuilder
from .anpr import (
    validate_plate,
    PlateCropSelector,
    ANPRPipeline,
    PlateReading,
)

__all__ = [
    "RingBuffer",
    "EvidenceBuilder",
    "validate_plate",
    "PlateCropSelector",
    "ANPRPipeline",
    "PlateReading",
]
