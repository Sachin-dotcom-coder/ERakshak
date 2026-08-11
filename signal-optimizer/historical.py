"""
historical.py — Historical Traffic Profiles & Anomaly Detection
================================================================
Stores and retrieves historical traffic baselines keyed by:

    (junction, lane, day_of_week, time_slot_5min, mode)

Detects anomalies via z-score comparison of live vs. historical averages.
Uses JSON file persistence so profiles are portable and inspectable.

Improvements #8, #9 from new_instruct.md.
"""

from __future__ import annotations

import datetime
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Literal, Optional, Tuple

from controller_config import ControllerConfig, get_config

AnomalyLevel = Literal["normal", "elevated", "high_anomaly", "extreme_anomaly"]


# ---------------------------------------------------------------------------
# Historical record for one time slot
# ---------------------------------------------------------------------------

@dataclass
class HistoricalBucket:
    """Running statistics for one (junction, lane, day, slot, mode) bucket."""
    count: int = 0
    sum_queue: float = 0.0
    sum_queue_sq: float = 0.0
    sum_speed: float = 0.0
    sum_speed_sq: float = 0.0
    sum_density: float = 0.0
    sum_growth: float = 0.0

    @property
    def mean_queue(self) -> float:
        return self.sum_queue / self.count if self.count > 0 else 0.0

    @property
    def std_queue(self) -> float:
        if self.count < 2:
            return 1.0  # avoid division by zero; assume unit variance
        mean = self.mean_queue
        variance = (self.sum_queue_sq / self.count) - (mean * mean)
        return max(math.sqrt(max(0.0, variance)), 0.1)  # floor at 0.1

    @property
    def mean_speed(self) -> float:
        return self.sum_speed / self.count if self.count > 0 else 0.0

    @property
    def mean_density(self) -> float:
        return self.sum_density / self.count if self.count > 0 else 0.0

    @property
    def mean_growth(self) -> float:
        return self.sum_growth / self.count if self.count > 0 else 0.0

    def update(
        self,
        queue: float,
        speed: float = 0.0,
        density: float = 0.0,
        growth: float = 0.0,
    ) -> None:
        """Add one observation to the running statistics."""
        self.count += 1
        self.sum_queue += queue
        self.sum_queue_sq += queue * queue
        self.sum_speed += speed
        self.sum_speed_sq += speed * speed
        self.sum_density += density
        self.sum_growth += growth

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "sum_queue": self.sum_queue,
            "sum_queue_sq": self.sum_queue_sq,
            "sum_speed": self.sum_speed,
            "sum_speed_sq": self.sum_speed_sq,
            "sum_density": self.sum_density,
            "sum_growth": self.sum_growth,
        }

    @staticmethod
    def from_dict(d: dict) -> "HistoricalBucket":
        return HistoricalBucket(**d)


# ---------------------------------------------------------------------------
# Profile store
# ---------------------------------------------------------------------------

def _make_key(
    junction_id: str,
    lane_id: str,
    day_of_week: int,
    time_slot: int,
    mode: str = "default",
) -> str:
    """Create a hashable key string for a bucket."""
    return f"{junction_id}|{lane_id}|{day_of_week}|{time_slot}|{mode}"


def _time_slot(dt: datetime.datetime, slot_minutes: int = 5) -> int:
    """Return a time-slot index for the given datetime."""
    return (dt.hour * 60 + dt.minute) // slot_minutes


class HistoricalProfileStore:
    """Manages historical traffic profiles for all junctions / lanes."""

    def __init__(self, config: Optional[ControllerConfig] = None) -> None:
        self._cfg = config or get_config()
        self._buckets: Dict[str, HistoricalBucket] = {}

    # --- Recording -----------------------------------------------------------

    def record(
        self,
        junction_id: str,
        lane_id: str,
        queue: float,
        speed: float = 0.0,
        density: float = 0.0,
        growth: float = 0.0,
        mode: str = "default",
        now: Optional[datetime.datetime] = None,
    ) -> None:
        """Record one observation into the matching historical bucket."""
        if now is None:
            now = datetime.datetime.now()
        day = now.weekday()
        slot = _time_slot(now, self._cfg.historical_time_slot_min)
        key = _make_key(junction_id, lane_id, day, slot, mode)

        if key not in self._buckets:
            self._buckets[key] = HistoricalBucket()
        self._buckets[key].update(queue, speed, density, growth)

    # --- Querying ------------------------------------------------------------

    def get_baseline(
        self,
        junction_id: str,
        lane_id: str,
        mode: str = "default",
        now: Optional[datetime.datetime] = None,
    ) -> Optional[HistoricalBucket]:
        """Return the historical bucket for current time, or ``None``."""
        if now is None:
            now = datetime.datetime.now()
        day = now.weekday()
        slot = _time_slot(now, self._cfg.historical_time_slot_min)
        key = _make_key(junction_id, lane_id, day, slot, mode)
        return self._buckets.get(key)

    def get_historical_queue(
        self,
        junction_id: str,
        lane_id: str,
        mode: str = "default",
        now: Optional[datetime.datetime] = None,
    ) -> float:
        """Return the historical mean queue, or 0 if no data."""
        bucket = self.get_baseline(junction_id, lane_id, mode, now)
        return bucket.mean_queue if bucket else 0.0

    # --- Anomaly detection (Improvement #9) ----------------------------------

    def detect_anomaly(
        self,
        junction_id: str,
        lane_id: str,
        current_queue: float,
        mode: str = "default",
        now: Optional[datetime.datetime] = None,
    ) -> Tuple[AnomalyLevel, float]:
        """Classify the current reading against historical baseline.

        Returns
        -------
        (anomaly_level, z_score)
        """
        bucket = self.get_baseline(junction_id, lane_id, mode, now)
        if bucket is None or bucket.count < 3:
            return "normal", 0.0

        z = (current_queue - bucket.mean_queue) / bucket.std_queue
        cfg = self._cfg

        if abs(z) >= cfg.anomaly_z_extreme:
            return "extreme_anomaly", z
        elif abs(z) >= cfg.anomaly_z_high:
            return "high_anomaly", z
        elif abs(z) >= cfg.anomaly_z_elevated:
            return "elevated", z
        else:
            return "normal", z

    # --- Persistence ---------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save all historical profiles to a JSON file."""
        data = {key: bucket.to_dict() for key, bucket in self._buckets.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str | Path) -> None:
        """Load historical profiles from a JSON file."""
        p = Path(path)
        if not p.exists():
            return
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, bucket_data in data.items():
            self._buckets[key] = HistoricalBucket.from_dict(bucket_data)

    @property
    def bucket_count(self) -> int:
        return len(self._buckets)

    def summary(self) -> dict:
        """Return a summary of stored profiles."""
        total_obs = sum(b.count for b in self._buckets.values())
        return {
            "buckets": self.bucket_count,
            "total_observations": total_obs,
        }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    store = HistoricalProfileStore()

    # Simulate a week of Monday 8:00 AM traffic
    for week in range(4):
        now = datetime.datetime(2026, 8, 4 + 7 * week, 8, 0)  # Mondays
        store.record("junction_01", "lane_NS_1", queue=12 + week, speed=4.0,
                      density=15 + week, growth=0.5, now=now)

    # Check baseline
    test_now = datetime.datetime(2026, 9, 1, 8, 0)  # a Monday
    baseline = store.get_baseline("junction_01", "lane_NS_1", now=test_now)
    if baseline:
        print(f"Historical mean queue: {baseline.mean_queue:.1f}")
        print(f"Historical std queue:  {baseline.std_queue:.2f}")
        print(f"Historical mean speed: {baseline.mean_speed:.1f}")

    # Anomaly detection
    level, z = store.detect_anomaly(
        "junction_01", "lane_NS_1", current_queue=25, now=test_now
    )
    print(f"\nCurrent queue=25 -> anomaly={level}, z-score={z:.2f}")

    level2, z2 = store.detect_anomaly(
        "junction_01", "lane_NS_1", current_queue=14, now=test_now
    )
    print(f"Current queue=14 -> anomaly={level2}, z-score={z2:.2f}")

    print(f"\nStore: {store.summary()}")
