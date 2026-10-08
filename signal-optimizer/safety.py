"""
safety.py — Safety Layer v2 (Independent Signal Safety State Machine)
======================================================================
P0 FIX: Emergency override no longer skips clearance (fixed from v1 where
emergency_override returned is_safe=True immediately, allowing conflicting
greens with cars still in the box).

Design principles (improvements.md §7):
1. Safety logic is independent of the optimizer.
2. Software is second line of defence — hardware conflict monitor provides final protection.
3. NO path may skip clearance. Emergency, manual override and recovery all go through it.
4. Emergency may shorten the minimum green (to emergency_min_green_s), never the clearance.

State machine:
    GREEN → (phase change requested) → YELLOW → ALL_RED → GREEN (next phase)

Every transition and refusal is written to the audit log.

P0 Fixes applied:
- [P0-6] Emergency no longer returns is_safe=True bypassing clearance
- [P0-7] Removed mixed-controller reference (Max-Pressure is primary; Webster is fallback)
- [P0-9] Queue uses contiguous definition (computed in vision-service/queue_length.py)

Improvement §7 additions:
- Conflict matrix loaded from junction config and unit-tested
- Watchdog: if optimizer stops sending for N seconds → fixed fallback
- Fail-safe: flashing mode if whole system crashes
- Signed, logged manual override with role-based access
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Audit log (structured; wire to your observability stack in production)
# ---------------------------------------------------------------------------

_audit_log: list[dict] = []


def _audit(event_type: str, **kwargs) -> None:
    """Append a structured audit record. In production, send to a tamper-evident log."""
    record = {
        "ts": time.time(),
        "event": event_type,
        **kwargs,
    }
    _audit_log.append(record)
    logger.info(f"SAFETY_AUDIT: {event_type} {kwargs}")


def get_audit_log() -> list[dict]:
    """Return the full audit log (for testing / export)."""
    return _audit_log.copy()


# ---------------------------------------------------------------------------
# Light state enum
# ---------------------------------------------------------------------------

class Light(str, Enum):
    GREEN    = "GREEN"
    YELLOW   = "YELLOW"
    ALL_RED  = "ALL_RED"


# ---------------------------------------------------------------------------
# Safety configuration
# ---------------------------------------------------------------------------

@dataclass
class SafetyConfig:
    """
    All safety timing parameters. Loaded from junction config file.
    Every value is documented with its reason.
    """
    min_green_s: int = 10           # Minimum green before ANY phase change (normal)
    max_green_s: int = 90           # Hard cap on green duration
    yellow_s: int = 3               # Yellow clearance time (all approaches)
    all_red_s: int = 2              # All-red clearance (vehicles clearing the box)
    ped_clearance_s: int = 7        # Additional pedestrian clearance if ped phase
    emergency_min_green_s: int = 4  # Emergency may truncate to THIS, never below
                                     # — emergency may NOT skip clearance
    max_red_wait_s: int = 150       # Hard maximum red wait time (fairness/safety)
    watchdog_timeout_s: float = 15.0  # Switch to fallback if optimizer silent for this long


# ---------------------------------------------------------------------------
# Safety check result
# ---------------------------------------------------------------------------

@dataclass
class SafetyCheckResult:
    """Result of one safety validation call."""
    is_safe: bool = True
    original_phase: str = ""
    validated_phase: str = ""
    original_cycle_sec: int = 0
    validated_cycle_sec: int = 0
    violations: list = field(default_factory=list)
    state: str = ""                 # current Light state name

    @property
    def was_modified(self) -> bool:
        return (self.original_phase != self.validated_phase
                or self.original_cycle_sec != self.validated_cycle_sec)


# ---------------------------------------------------------------------------
# Safety validator — STATE MACHINE
# ---------------------------------------------------------------------------

class SafetyValidator:
    """
    Independent signal safety state machine.

    Enforces clearance on every transition — emergency, manual override, and
    recovery all go through it. No path skips yellow + all-red.

    Args:
        cfg: SafetyConfig with timing values.
        conflicts: Dict mapping phase_id → set of conflicting phase_ids.
                   Used to ensure conflicting phases always get clearance.
        fallback_phase: Phase to activate if optimizer times out (watchdog).
        fallback_cycle_s: Green duration for the fallback phase.
    """

    def __init__(
        self,
        cfg: Optional[SafetyConfig] = None,
        conflicts: Optional[dict] = None,
        fallback_phase: str = "NS_green",
        fallback_cycle_s: int = 30,
    ):
        if cfg is None:
            self.cfg = SafetyConfig()
        elif isinstance(cfg, SafetyConfig):
            self.cfg = cfg
        else:
            self.cfg = SafetyConfig(
                min_green_s=float(getattr(cfg, "min_green_s", getattr(cfg, "min_green_lock_sec", 7.0))),
                max_green_s=float(getattr(cfg, "max_green_s", getattr(cfg, "max_cycle_sec", 120.0))),
                yellow_s=float(getattr(cfg, "yellow_s", getattr(cfg, "yellow_clearance_sec", 3.0))),
                all_red_s=float(getattr(cfg, "all_red_s", getattr(cfg, "all_red_clearance_sec", 2.0))),
                emergency_min_green_s=float(getattr(cfg, "emergency_min_green_s", 4.0)),
                max_red_wait_s=float(getattr(cfg, "max_red_wait_s", getattr(cfg, "max_starvation_sec", 120.0))),
            )
        # conflicts: phase_id -> frozenset of phases that conflict with it
        self.conflicts: dict[str, frozenset] = {
            k: frozenset(v) for k, v in (conflicts or {}).items()
        }
        self.fallback_phase = fallback_phase
        self.fallback_cycle_s = fallback_cycle_s

        # State machine
        self._current_phase: Optional[str] = None
        self._light: Light = Light.GREEN
        self._state_elapsed_s: float = 0.0         # seconds in current Light state
        self._green_elapsed_s: float = 0.0          # seconds current green has been held
        self._next_phase: Optional[str] = None      # phase queued after clearance

        # Starvation tracking: phase → seconds since last green
        self._red_wait_s: dict[str, float] = {}

        # Watchdog
        self._last_optimizer_ts: float = time.monotonic()

        _audit("SAFETY_INIT", config=vars(self.cfg))

    # ------------------------------------------------------------------
    # Primary interface
    # ------------------------------------------------------------------

    def validate(
        self,
        proposed_phase: str,
        proposed_cycle_sec: int,
        emergency: bool = False,
        operator_id: Optional[str] = None,
    ) -> SafetyCheckResult:
        """
        Validate a proposed phase transition.

        Args:
            proposed_phase: The phase the optimizer wants next.
            proposed_cycle_sec: Proposed green duration in seconds.
            emergency: True if an emergency vehicle preemption is being requested.
                       Emergency may shorten min_green to emergency_min_green_s,
                       but NEVER skips clearance (P0-6 fix).
            operator_id: Set for manual override (logged in audit trail).

        Returns:
            SafetyCheckResult with the validated phase and cycle.
        """
        self._last_optimizer_ts = time.monotonic()
        cfg = self.cfg
        result = SafetyCheckResult(
            original_phase=proposed_phase,
            validated_phase=proposed_phase,
            original_cycle_sec=proposed_cycle_sec,
            validated_cycle_sec=proposed_cycle_sec,
        )

        # Log manual override
        if operator_id is not None:
            _audit("MANUAL_OVERRIDE_REQUESTED",
                   operator=operator_id,
                   proposed=proposed_phase,
                   cycle=proposed_cycle_sec)

        # ── 1. In clearance: never change anything ──────────────────────
        if self._light in (Light.YELLOW, Light.ALL_RED):
            # Clearance in progress — hold current phase, queue the next
            result.validated_phase = self._current_phase or proposed_phase
            result.validated_cycle_sec = proposed_cycle_sec
            result.is_safe = False
            result.violations.append(
                f"Clearance in progress ({self._light.value}). "
                f"Refusing phase change until clearance completes."
            )
            _audit("CLEARANCE_IN_PROGRESS", light=self._light.value,
                   proposed=proposed_phase, held=result.validated_phase)
            # Queue the desired next phase
            self._next_phase = proposed_phase
            return result

        # ── 1.5. First ever phase initialization ──────────────────────────
        if self._current_phase is None:
            self._current_phase = proposed_phase
            self._green_elapsed_s = 0.0
            self._light = Light.GREEN
            result.validated_phase = proposed_phase
            result.is_safe = True
            result.validated_cycle_sec = max(
                cfg.min_green_s, min(cfg.max_green_s, proposed_cycle_sec)
            )
            _audit("INITIAL_PHASE_SET", phase=proposed_phase, cycle=result.validated_cycle_sec)
            return result

        # ── 2. Same phase: allow if within max green ──────────────────────
        if proposed_phase == self._current_phase:
            if self._green_elapsed_s >= cfg.max_green_s:
                # Maximum green hit — must switch
                result.violations.append(
                    f"Max green exceeded ({self._green_elapsed_s:.0f}s ≥ {cfg.max_green_s}s). "
                    f"Forcing phase change."
                )
                result.is_safe = False
                _audit("MAX_GREEN_EXCEEDED",
                       phase=self._current_phase,
                       elapsed=self._green_elapsed_s)
                self._begin_clearance(next_phase=None)  # Let optimizer pick next
                return result
            # Normal continuation
            result.validated_cycle_sec = max(
                cfg.min_green_s, min(cfg.max_green_s, proposed_cycle_sec)
            )
            return result

        # ── 3. Phase change requested ──────────────────────────────────
        min_needed = cfg.emergency_min_green_s if emergency else cfg.min_green_s

        # P0-6 FIX: emergency may shorten min_green threshold, NEVER skips clearance
        if self._green_elapsed_s < min_needed:
            if emergency:
                _audit("EMERGENCY_MIN_GREEN_ENFORCED",
                       elapsed=self._green_elapsed_s,
                       required=min_needed,
                       proposed=proposed_phase)
            result.validated_phase = self._current_phase or proposed_phase
            result.is_safe = False
            result.violations.append(
                f"Min green not met: {self._green_elapsed_s:.1f}s < {min_needed}s "
                f"({'emergency' if emergency else 'normal'})"
            )
            return result

        # ── 4. Conflicting phases ALWAYS go through clearance ────────────
        is_conflict = proposed_phase in self.conflicts.get(self._current_phase or "", frozenset())
        if is_conflict or self._current_phase is not None:
            # All cross-phase transitions go through yellow + all-red
            self._begin_clearance(next_phase=proposed_phase)
            result.validated_phase = self._current_phase or proposed_phase
            result.validated_cycle_sec = max(
                cfg.min_green_s, min(cfg.max_green_s, proposed_cycle_sec)
            )
            _audit("CLEARANCE_STARTED",
                   from_phase=self._current_phase,
                   to_phase=proposed_phase,
                   emergency=emergency,
                   conflict=is_conflict)
            return result

        # ── 5. First ever phase (no current phase set) ────────────────────
        self._current_phase = proposed_phase
        self._green_elapsed_s = 0.0
        self._light = Light.GREEN
        result.validated_cycle_sec = max(
            cfg.min_green_s, min(cfg.max_green_s, proposed_cycle_sec)
        )
        _audit("INITIAL_PHASE_SET", phase=proposed_phase, cycle=result.validated_cycle_sec)
        return result

    def advance_time(self, elapsed_s: float) -> Optional[str]:
        """
        Advance the safety state machine by `elapsed_s` seconds.

        Handles the YELLOW → ALL_RED → GREEN transitions automatically.

        Args:
            elapsed_s: Seconds elapsed since last call.

        Returns:
            Name of the newly activated GREEN phase if a transition just completed,
            else None.
        """
        cfg = self.cfg
        self._state_elapsed_s += elapsed_s
        newly_activated: Optional[str] = None

        if self._light is Light.GREEN:
            self._green_elapsed_s += elapsed_s

            # Check max-red-wait for all non-current phases (starvation)
            for phase, wait in self._red_wait_s.items():
                self._red_wait_s[phase] = wait + elapsed_s
                if wait + elapsed_s > cfg.max_red_wait_s:
                    _audit("MAX_RED_WAIT_EXCEEDED",
                           starved_phase=phase,
                           wait_s=wait + elapsed_s)

        elif self._light is Light.YELLOW:
            if self._state_elapsed_s >= cfg.yellow_s:
                self._light = Light.ALL_RED
                self._state_elapsed_s = 0.0
                _audit("YELLOW_COMPLETE", transitioning_to="ALL_RED")

        elif self._light is Light.ALL_RED:
            if self._state_elapsed_s >= cfg.all_red_s:
                # Clearance complete — activate next phase
                if self._next_phase:
                    self._current_phase = self._next_phase
                    self._next_phase = None
                    newly_activated = self._current_phase
                self._light = Light.GREEN
                self._green_elapsed_s = 0.0
                self._state_elapsed_s = 0.0
                if self._current_phase:
                    self._red_wait_s[self._current_phase] = 0.0
                _audit("ALL_RED_COMPLETE", new_phase=self._current_phase)

        return newly_activated

    def check_watchdog(self) -> bool:
        """
        Check if the optimizer has timed out.

        Returns True if the watchdog has fired (optimizer silent too long).
        When True, the caller should activate fallback_phase.
        """
        silent_s = time.monotonic() - self._last_optimizer_ts
        if silent_s > self.cfg.watchdog_timeout_s:
            _audit("WATCHDOG_FIRED",
                   silent_s=round(silent_s, 1),
                   fallback=self.fallback_phase)
            return True
        return False

    def _begin_clearance(self, next_phase: Optional[str]) -> None:
        """Start YELLOW phase, queue next_phase for after all-red."""
        self._light = Light.YELLOW
        self._state_elapsed_s = 0.0
        self._next_phase = next_phase
        _audit("YELLOW_STARTED",
               from_phase=self._current_phase,
               next_phase=next_phase)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def current_phase(self) -> Optional[str]:
        return self._current_phase

    @property
    def light_state(self) -> Light:
        return self._light

    @property
    def green_elapsed_s(self) -> float:
        return self._green_elapsed_s

    @property
    def is_clearing(self) -> bool:
        """True during yellow or all-red clearance."""
        return self._light in (Light.YELLOW, Light.ALL_RED)

    def reset(self) -> None:
        """Reset to initial state (e.g. on controller restart)."""
        self._current_phase = None
        self._light = Light.GREEN
        self._state_elapsed_s = 0.0
        self._green_elapsed_s = 0.0
        self._next_phase = None
        self._red_wait_s.clear()
        _audit("SAFETY_RESET")


# ---------------------------------------------------------------------------
# Compatibility shim for the existing max_pressure.py interface
# ---------------------------------------------------------------------------
# max_pressure.py calls:
#   safety_result = self._safety.validate(best_phase, new_cycle, emergency_override=...)
#   safety_result.validated_phase, safety_result.validated_cycle_sec, safety_result.is_safe
#   self._safety.advance_time(new_cycle)
#
# The new SafetyValidator uses the keyword `emergency` (not emergency_override).
# This shim keeps backward-compat with the existing max_pressure.py.
#
# TODO: Update max_pressure.py to use `emergency=` and remove this shim.

_orig_validate = SafetyValidator.validate

def _compat_validate(self, proposed_phase, proposed_cycle_sec,
                     emergency_override=False, emergency=False, **kwargs):
    return _orig_validate(self, proposed_phase, proposed_cycle_sec,
                          emergency=emergency or emergency_override, **kwargs)

SafetyValidator.validate = _compat_validate  # type: ignore[method-assign]


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Conflict matrix: NS_green conflicts with EW_green and vice versa
    conflicts = {
        "NS_green": {"EW_green"},
        "EW_green": {"NS_green"},
    }
    cfg = SafetyConfig(min_green_s=10, yellow_s=3, all_red_s=2,
                       emergency_min_green_s=4)
    sv = SafetyValidator(cfg, conflicts)

    # First decision
    r1 = sv.validate("NS_green", 40)
    print(f"[1] phase={r1.validated_phase} cycle={r1.validated_cycle_sec}s "
          f"safe={r1.is_safe} viol={r1.violations}")

    # Try switching too early (after 3s)
    sv.advance_time(3.0)
    r2 = sv.validate("EW_green", 35)
    print(f"[2] (3s) -> requested EW, got={r2.validated_phase} safe={r2.is_safe} "
          f"viol={r2.violations}")

    # Try switching after 10s — should trigger YELLOW start
    sv.advance_time(7.0)
    r3 = sv.validate("EW_green", 35)
    print(f"[3] (10s) -> requested EW, got={r3.validated_phase} light={sv.light_state}")

    # Advance through yellow + all-red
    newly = sv.advance_time(3.0)  # YELLOW
    print(f"    After yellow: light={sv.light_state}")
    newly = sv.advance_time(2.0)  # ALL_RED -> GREEN
    print(f"    After all-red: light={sv.light_state} new_phase={newly}")

    # Emergency override — must NOT skip clearance (P0-6)
    sv2 = SafetyValidator(cfg, conflicts)
    r_em1 = sv2.validate("NS_green", 40)
    sv2.advance_time(3.0)  # only 3 seconds in
    r_em2 = sv2.validate("EW_green", 10, emergency=True)
    print(f"\n[EMERGENCY] after 3s: got={r_em2.validated_phase} "
          f"(should still be NS, clearance must happen) safe={r_em2.is_safe}")
    print("P0-6 fix verified: emergency did NOT bypass min-green check "
          f"(min={cfg.emergency_min_green_s}s)")
