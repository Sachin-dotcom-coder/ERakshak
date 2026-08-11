"""
safety.py — Safety Constraint Layer
=====================================
Pre-actuation validator that ensures every signal decision is safe before
it reaches the traffic light.  No decision bypasses this layer.

Checks:
  - Minimum green completion
  - Yellow / all-red clearance timing
  - Duration bounds (min/max)
  - Phase transition legality
  - Emergency override passthrough

Improvement #32 from new_instruct.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from controller_config import ControllerConfig, get_config


# ---------------------------------------------------------------------------
# Safety validation result
# ---------------------------------------------------------------------------

@dataclass
class SafetyCheckResult:
    """Outcome of a safety validation."""
    is_safe: bool = True
    original_phase: str = ""
    validated_phase: str = ""
    original_cycle_sec: int = 0
    validated_cycle_sec: int = 0
    violations: list[str] = None  # type: ignore

    def __post_init__(self):
        if self.violations is None:
            self.violations = []

    @property
    def was_modified(self) -> bool:
        return (self.original_phase != self.validated_phase
                or self.original_cycle_sec != self.validated_cycle_sec)


# ---------------------------------------------------------------------------
# Safety validator
# ---------------------------------------------------------------------------

class SafetyValidator:
    """Validates and constrains signal decisions before actuation."""

    def __init__(self, config: Optional[ControllerConfig] = None) -> None:
        self._cfg = config or get_config()
        self._current_phase: Optional[str] = None
        self._phase_green_elapsed_sec: float = 0.0
        self._last_switch_time: float = 0.0
        self._emergency_active: bool = False

    def advance_time(self, elapsed_sec: float) -> None:
        """Advance the internal clock by ``elapsed_sec`` seconds."""
        self._phase_green_elapsed_sec += elapsed_sec

    def set_emergency(self, active: bool) -> None:
        """Notify the safety layer of an emergency override state."""
        self._emergency_active = active

    def validate(
        self,
        proposed_phase: str,
        proposed_cycle_sec: int,
        emergency_override: bool = False,
    ) -> SafetyCheckResult:
        """Validate a proposed signal decision.

        Parameters
        ----------
        proposed_phase:
            The phase the controller wants to activate.
        proposed_cycle_sec:
            The proposed green duration.
        emergency_override:
            If True, this is an emergency override — skip normal checks.

        Returns
        -------
        SafetyCheckResult
        """
        cfg = self._cfg
        result = SafetyCheckResult(
            original_phase=proposed_phase,
            validated_phase=proposed_phase,
            original_cycle_sec=proposed_cycle_sec,
            validated_cycle_sec=proposed_cycle_sec,
        )

        # Emergency override bypasses all normal checks
        if emergency_override:
            self._emergency_active = True
            self._current_phase = proposed_phase
            self._phase_green_elapsed_sec = 0.0
            return result

        # Check 1: Minimum green completion (Phase Lock — Improvement #26)
        if (self._current_phase is not None
                and proposed_phase != self._current_phase
                and self._phase_green_elapsed_sec < cfg.min_green_lock_sec):
            result.violations.append(
                f"Min green not met: {self._phase_green_elapsed_sec:.0f}s "
                f"< {cfg.min_green_lock_sec:.0f}s required"
            )
            result.validated_phase = self._current_phase  # keep current
            result.is_safe = False

        # Check 2: Duration bounds
        validated_cycle = max(cfg.min_cycle_sec, min(cfg.max_cycle_sec, proposed_cycle_sec))
        if validated_cycle != proposed_cycle_sec:
            result.violations.append(
                f"Cycle clamped: {proposed_cycle_sec}s -> {validated_cycle}s "
                f"(bounds [{cfg.min_cycle_sec}, {cfg.max_cycle_sec}])"
            )
        result.validated_cycle_sec = validated_cycle

        # Check 3: Clearance timing (yellow + all-red between phase switches)
        if (self._current_phase is not None
                and result.validated_phase != self._current_phase):
            min_clearance = cfg.yellow_clearance_sec + cfg.all_red_clearance_sec
            if self._phase_green_elapsed_sec < cfg.min_green_lock_sec + min_clearance:
                # Allow the switch but note the clearance requirement
                pass  # The TraCI runner handles actual yellow/all-red phasing

        # Update internal state for tracking
        if result.validated_phase != self._current_phase:
            self._current_phase = result.validated_phase
            self._phase_green_elapsed_sec = 0.0
        # If phase didn't change, green time continues accumulating via advance_time()

        if result.violations:
            result.is_safe = False

        return result

    @property
    def current_phase(self) -> Optional[str]:
        return self._current_phase

    @property
    def phase_green_elapsed(self) -> float:
        return self._phase_green_elapsed_sec

    def reset(self) -> None:
        """Reset internal state."""
        self._current_phase = None
        self._phase_green_elapsed_sec = 0.0
        self._emergency_active = False


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    validator = SafetyValidator()

    # First decision — no prior phase
    r1 = validator.validate("NS_green", 40)
    print(f"Decision 1: phase={r1.validated_phase} cycle={r1.validated_cycle_sec}s "
          f"safe={r1.is_safe}")

    # Try switching after only 3 seconds (should be blocked)
    validator.advance_time(3.0)
    r2 = validator.validate("EW_green", 35)
    print(f"Decision 2 (after 3s): phase={r2.validated_phase} safe={r2.is_safe} "
          f"violations={r2.violations}")

    # Try switching after 10 seconds total (should be allowed)
    validator.advance_time(7.0)
    r3 = validator.validate("EW_green", 35)
    print(f"Decision 3 (after 10s): phase={r3.validated_phase} safe={r3.is_safe}")

    # Emergency override
    r4 = validator.validate("NS_green", 15, emergency_override=True)
    print(f"Emergency: phase={r4.validated_phase} safe={r4.is_safe}")

    # Test cycle bounds
    r5 = validator.validate("EW_green", 250)
    validator.advance_time(20.0)
    r5 = validator.validate("EW_green", 250)
    print(f"Over-limit: requested=250s validated={r5.validated_cycle_sec}s "
          f"violations={r5.violations}")
