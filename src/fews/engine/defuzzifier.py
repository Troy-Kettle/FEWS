"""
Defuzzifies the per-vital degrees of membership into a single scalar concern score.
Per vital:
- Calculate a weigthted scalar score from the membership functions 
- Map the scalar in the [0,3] output membership functions then use centroid defuzzification to get the overall score per vital.
Defuzzifier sums the per-vital conern scores in [0,3] into one float.
"""
import numpy as np

MIN_FIRING: float = 0.05

_OUTPUT_MF_PARAMS: dict[str, tuple[float, float, float, float]] = {
    "No concern":       (-0.5, 0.0, 0.0, 0.75),
    "Mild concern":     (0.25, 1.0, 1.0, 1.75),
    "Moderate concern": (1.25, 2.0, 2.0, 2.75),
    "Severe concern":   (2.25, 3.0, 3.0, 3.5),
}

_DOMAIN: np.ndarray = np.linspace(0, 3, 301)

def _map_to_concern_levels(memberships: dict[str, float]) -> dict[str, float]:
    concern: dict[str, float] = {
        "No concern":       0.0,
        "Mild concern":     0.0,
        "Moderate concern": 0.0,
        "Severe concern":   0.0,
    }
    for label, value in memberships.items():
        label_lower = label.lower()
        if "severe" in label_lower:
            concern["Severe concern"] = max(concern["Severe concern"], value)
        elif "moderate" in label_lower:
            concern["Moderate concern"] = max(concern["Moderate concern"], value)
        elif "mild" in label_lower:
            concern["Mild concern"] = max(concern["Mild concern"], value)
        elif "no concern" in label_lower:
            concern["No concern"] = max(concern["No concern"], value)
    return concern

def _apply_threshold(concern: dict[str, float]) -> dict[str, float]:
    return {k: (v if v >= MIN_FIRING else 0.0) for k, v in concern.items()}

def _only_no_concern_active(concern: dict[str, float]) -> bool:
    return concern.get("No concern", 0.0) > 0.0 and all(
        level == "No concern" or firing == 0.0
        for level, firing in concern.items()
    )

def _trapezoidal_mf_array(x: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        left  = np.where(a == b, (x >= b).astype(float), (x - a) / (b - a))
        right = np.where(c == d, (x <= c).astype(float), (d - x) / (d - c))
        plateau = ((x >= b) & (x <= c)).astype(float)
    result = np.where(
        (x <= a) | (x >= d), 0.0,
        np.where(plateau, 1.0,
        np.where(x < b, left, right))
    )
    return np.maximum(0.0, np.minimum(1.0, result))

def _fuzzify_outputs(concern: dict[str, float]) -> float:
    """
    Calculate and returns the output concern per vital
    """
    if _only_no_concern_active(concern):
        return 0.0

    aggregated = np.zeros_like(_DOMAIN)
    for level, firing in concern.items():
        if firing > 0.0:
            a, b, c, d = _OUTPUT_MF_PARAMS[level]
            clipped = np.minimum(firing, _trapezoidal_mf_array(_DOMAIN, a, b, c, d))
            aggregated = np.maximum(aggregated, clipped)

    denominator = float(np.sum(aggregated))
    numerator   = float(np.sum(_DOMAIN * aggregated))
    return numerator / denominator if denominator != 0.0 else 0.0

def defuzzifier(degrees_of_membership: dict[str, dict[str, float]]) -> float:
    """
    Defuzzifies and aggregates across each vital to a single concern score.
    """
    return float(sum(
        _fuzzify_outputs(_apply_threshold(_map_to_concern_levels(memberships)))
        for memberships in degrees_of_membership.values()
    ))
