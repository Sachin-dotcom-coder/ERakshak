"""
confidence/calibration.py — Confidence Calibration Framework (Section 53)
===========================================================================
Calibrates raw neural network confidence to true probabilities using
a held-out validation set.

Supported methods:
- Temperature scaling
- Isotonic regression
- Platt-style calibration

Also generates reliability diagrams for evaluation.
"""

import logging
import json
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """Calibrate raw model confidence to true probability.

    Raw NN confidence is not necessarily a calibrated probability.
    This module learns a calibration mapping from validation data.

    Args:
        method: Calibration method ('temperature', 'isotonic', 'platt').
        calibration_data_path: Path to saved calibration parameters.
    """

    def __init__(
        self,
        method: str = "temperature",
        calibration_data_path: Optional[str] = None,
    ) -> None:
        self._method = method
        self._temperature: float = 1.0
        self._isotonic_bins: Optional[np.ndarray] = None
        self._isotonic_values: Optional[np.ndarray] = None
        self._platt_a: float = 1.0
        self._platt_b: float = 0.0
        self._is_fitted: bool = False

        if calibration_data_path:
            self._load_calibration(calibration_data_path)

    def calibrate(self, raw_confidence: float) -> float:
        """Calibrate a raw confidence score.

        Args:
            raw_confidence: Raw model confidence (0-1).

        Returns:
            Calibrated confidence (0-1).
        """
        if not self._is_fitted:
            return raw_confidence

        if self._method == "temperature":
            return self._temperature_scale(raw_confidence)
        elif self._method == "isotonic":
            return self._isotonic_transform(raw_confidence)
        elif self._method == "platt":
            return self._platt_transform(raw_confidence)
        return raw_confidence

    def fit(
        self,
        predicted_confidences: np.ndarray,
        actual_correct: np.ndarray,
    ) -> dict:
        """Fit the calibration model on validation data.

        Args:
            predicted_confidences: Array of raw model confidences.
            actual_correct: Boolean array — whether each prediction was correct.

        Returns:
            Dict with calibration results and ECE metric.
        """
        if len(predicted_confidences) == 0:
            logger.warning("No calibration data provided")
            return {"ece": 1.0, "fitted": False}

        predicted_confidences = np.asarray(predicted_confidences, dtype=np.float64)
        actual_correct = np.asarray(actual_correct, dtype=np.float64)

        if self._method == "temperature":
            self._fit_temperature(predicted_confidences, actual_correct)
        elif self._method == "isotonic":
            self._fit_isotonic(predicted_confidences, actual_correct)
        elif self._method == "platt":
            self._fit_platt(predicted_confidences, actual_correct)

        self._is_fitted = True

        # Compute ECE
        ece = self._compute_ece(predicted_confidences, actual_correct)

        logger.info(
            f"Confidence calibration fitted ({self._method}): ECE={ece:.4f}"
        )

        return {
            "method": self._method,
            "ece_before": round(ece, 4),
            "fitted": True,
        }

    def _fit_temperature(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
    ) -> None:
        """Fit temperature scaling: calibrated = σ(logit(p) / T)."""
        # Grid search for optimal temperature
        best_t = 1.0
        best_ece = float("inf")

        for t in np.arange(0.5, 3.0, 0.05):
            calibrated = self._apply_temp(confidences, t)
            ece = self._compute_ece(calibrated, correct)
            if ece < best_ece:
                best_ece = ece
                best_t = t

        self._temperature = best_t
        logger.info(f"Temperature scaling: T={best_t:.2f}, ECE={best_ece:.4f}")

    def _apply_temp(self, confidences: np.ndarray, temperature: float) -> np.ndarray:
        """Apply temperature scaling."""
        # Clip to avoid log(0)
        p = np.clip(confidences, 1e-7, 1 - 1e-7)
        logits = np.log(p / (1 - p))
        scaled_logits = logits / temperature
        return 1.0 / (1.0 + np.exp(-scaled_logits))

    def _temperature_scale(self, conf: float) -> float:
        p = np.clip(conf, 1e-7, 1 - 1e-7)
        logit = np.log(p / (1 - p))
        scaled = logit / self._temperature
        return float(1.0 / (1.0 + np.exp(-scaled)))

    def _fit_isotonic(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
    ) -> None:
        """Fit isotonic regression (bin-based)."""
        n_bins = 15
        bin_edges = np.linspace(0, 1, n_bins + 1)
        bin_centers = []
        bin_accuracies = []

        for i in range(n_bins):
            mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i + 1])
            if np.sum(mask) > 0:
                bin_centers.append(float(np.mean(confidences[mask])))
                bin_accuracies.append(float(np.mean(correct[mask])))

        if bin_centers:
            self._isotonic_bins = np.array(bin_centers)
            self._isotonic_values = np.array(bin_accuracies)

    def _isotonic_transform(self, conf: float) -> float:
        if self._isotonic_bins is None or len(self._isotonic_bins) == 0:
            return conf
        return float(np.interp(conf, self._isotonic_bins, self._isotonic_values))

    def _fit_platt(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
    ) -> None:
        """Fit Platt scaling: calibrated = σ(a * logit(p) + b)."""
        p = np.clip(confidences, 1e-7, 1 - 1e-7)
        logits = np.log(p / (1 - p))

        # Simple least-squares fit
        A = np.vstack([logits, np.ones_like(logits)]).T
        try:
            result = np.linalg.lstsq(A, correct, rcond=None)
            self._platt_a = float(result[0][0])
            self._platt_b = float(result[0][1])
        except Exception:
            self._platt_a = 1.0
            self._platt_b = 0.0

    def _platt_transform(self, conf: float) -> float:
        p = np.clip(conf, 1e-7, 1 - 1e-7)
        logit = np.log(p / (1 - p))
        scaled = self._platt_a * logit + self._platt_b
        return float(1.0 / (1.0 + np.exp(-scaled)))

    def _compute_ece(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
        n_bins: int = 10,
    ) -> float:
        """Compute Expected Calibration Error."""
        bin_edges = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        total = len(confidences)

        for i in range(n_bins):
            mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i + 1])
            n_bin = np.sum(mask)
            if n_bin > 0:
                avg_conf = float(np.mean(confidences[mask]))
                avg_acc = float(np.mean(correct[mask]))
                ece += (n_bin / total) * abs(avg_conf - avg_acc)

        return ece

    def generate_reliability_diagram(
        self,
        confidences: np.ndarray,
        correct: np.ndarray,
        n_bins: int = 10,
    ) -> dict:
        """Generate data for a reliability diagram.

        Args:
            confidences: Predicted confidences.
            correct: Ground truth correctness.
            n_bins: Number of bins.

        Returns:
            Dict with bin_centers, accuracies, counts.
        """
        bin_edges = np.linspace(0, 1, n_bins + 1)
        centers = []
        accuracies = []
        counts = []

        for i in range(n_bins):
            mask = (confidences >= bin_edges[i]) & (confidences < bin_edges[i + 1])
            n = int(np.sum(mask))
            counts.append(n)
            if n > 0:
                centers.append(float(np.mean(confidences[mask])))
                accuracies.append(float(np.mean(correct[mask])))
            else:
                centers.append(float((bin_edges[i] + bin_edges[i + 1]) / 2))
                accuracies.append(0.0)

        return {
            "bin_centers": centers,
            "accuracies": accuracies,
            "counts": counts,
            "ece": round(self._compute_ece(confidences, correct, n_bins), 4),
        }

    def save_calibration(self, path: str) -> None:
        """Save calibration parameters to file."""
        data = {
            "method": self._method,
            "temperature": self._temperature,
            "platt_a": self._platt_a,
            "platt_b": self._platt_b,
            "is_fitted": self._is_fitted,
        }
        if self._isotonic_bins is not None:
            data["isotonic_bins"] = self._isotonic_bins.tolist()
            data["isotonic_values"] = self._isotonic_values.tolist()

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_calibration(self, path: str) -> None:
        """Load saved calibration parameters."""
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self._method = data.get("method", "temperature")
            self._temperature = data.get("temperature", 1.0)
            self._platt_a = data.get("platt_a", 1.0)
            self._platt_b = data.get("platt_b", 0.0)
            self._is_fitted = data.get("is_fitted", False)
            if "isotonic_bins" in data:
                self._isotonic_bins = np.array(data["isotonic_bins"])
                self._isotonic_values = np.array(data["isotonic_values"])
            logger.info(f"Loaded calibration ({self._method}) from {path}")
        except Exception as e:
            logger.warning(f"Failed to load calibration: {e}")
