"""
Defuzzifies the per-vital degrees of membership into a single scalar concern score.

Per vital:
- Calculate a weigthted scalar score from the membership functions 
- Map the scalar in the [0,3] output membership functions then use centroid defuzzification to get the overall score per vital.

Defuzzifier sums the per-vital conern scores in [0,3] into one float.
"""

import numpy as np

CONCERN_WEIGHTS_7: dict[str, float] = {
    "Below normal - severe concern":   0.0,
    "Below normal - moderate concern": 0.5,
    "Below normal - mild concern":     1.0,
    "No concern":                      1.5,
    "Above normal - mild concern":     2.0,
    "Above normal - moderate concern": 2.5,
    "Above normal - severe concern":   3.0,
}

CONCERN_WEIGHTS_4_ABOVE: dict[str, float] = {
    "No concern":                      0.0,
    "Above normal - mild concern":     1.0,
    "Above normal - moderate concern": 2.0,
    "Above normal - severe concern":   3.0,
}

CONCERN_WEIGHTS_4_BELOW: dict[str, float] = {
    "Below normal - severe concern":   3.0,
    "Below normal - moderate concern": 2.0,
    "Below normal - mild concern":     1.0,
    "No concern":                      0.0,
}

_OUTPUT_MF_PARAMS: dict[str, tuple[float, float, float]] = {
    "low":         (0.0, 0.0, 1.0),
    "medium_low":  (0.0, 1.0, 2.0),
    "medium_high": (1.0, 2.0, 3.0),
    "high":        (2.0, 3.0, 3.0),
}

_DOMAIN: np.ndarray = np.linspace(0, 3, 300)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _select_weights(vital: str) -> dict[str, float]:
    if vital == "spo2":
        return CONCERN_WEIGHTS_4_BELOW
    if vital == "fio2":
        return CONCERN_WEIGHTS_4_ABOVE
    return CONCERN_WEIGHTS_7

def _vital_score(vital: str, memberships: dict[str, float]) -> float:
    """Computes a single weighted scalar score for one vital sign."""
    weights = _select_weights(vital)
    return sum(memberships[k] * weights[k] for k in memberships)


def _triangular_mf(x: float, a: float, b: float, c: float) -> float:
    """Returns a triangular membership function at a scalar point x."""
    left  = 1.0 if a == b else (x - a) / (b - a)
    right = 1.0 if b == c else (c - x) / (c - b)
    return max(0.0, min(left, right))


def _triangular_mf_array(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Returns a triangular membership function across a numpy domain array."""
    left  = np.where(a == b, (x <= a).astype(float), (x - a) / (b - a))
    right = np.where(b == c, (x >= c).astype(float), (c - x) / (c - b))
    return np.maximum(0, np.minimum(left, right))


def _fuzzify_outputs(score: float) -> float:
    """
    Calculate and returns the output concern per vital
    """
    activations = {
        name: _triangular_mf(score, a, b, c)
        for name, (a, b, c) in _OUTPUT_MF_PARAMS.items()
    }

    aggregated = np.maximum.reduce([
        activations[name] * _triangular_mf_array(_DOMAIN, a, b, c)
        for name, (a, b, c) in _OUTPUT_MF_PARAMS.items()
    ])

    denominator = float(np.sum(aggregated))
    numerator   = float(np.sum(_DOMAIN * aggregated))

    return numerator / denominator if denominator != 0.0 else 0.0


def defuzzifier(degrees_of_membership: dict[str, dict[str, float]]) -> float:
    """
    Defuzzifies and aggregates across each vital to a single concern score.
    """
    return float(sum(
        _fuzzify_outputs(_vital_score(vital, memberships))
        for vital, memberships in degrees_of_membership.items()
    ))
