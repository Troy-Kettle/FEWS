"""
Creates the output membership functions.
Fuzzifies the degrees of membership for each vital.
Aggregates and then calculates the centroid.

Takes in the dict from fews.engine.fuzzifier and returns the overall fuzzy concern score.
"""

import numpy as np

set_weights_7 = {
    "Below normal - severe concern": 0.0,
    "Below normal - moderate concern": 0.5,
    "Below normal - mild concern": 1.0,
    "No concern": 1.5,
    "Above normal - mild concern": 2.0,
    "Above normal - moderate concern": 2.5,
    "Above normal - severe concern": 3.0,
}

set_weights_4 = {
    "No concern": 0.0,
    "Above normal - mild concern": 1.0,
    "Above normal - moderate concern": 2.0,
    "Above normal - severe concern": 3.0,
}

def defuzzifier(degrees_of_membership: dict[str, dict[str, float]]) -> float:

    def output_mf_array(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
        left  = np.where(a == b, (x <= a).astype(float), (x - a) / (b - a))
        right = np.where(b == c, (x >= c).astype(float), (c - x) / (c - b))
        return np.maximum(0, np.minimum(left, right))

    def fuzzify_outputs(x: float) -> float:
        def output_membership_function(x: float, a: float, b: float, c: float) -> float:
            left  = 1.0 if a == b else (x - a) / (b - a)
            right = 1.0 if b == c else (c - x) / (c - b)
            return max(0.0, min(left, right))
        memberships = {
            "low":         output_membership_function(x, 0.0, 0.0, 1.0),
            "medium_low":  output_membership_function(x, 0.0, 1.0, 2.0),
            "medium_high": output_membership_function(x, 1.0, 2.0, 3.0),
            "high":        output_membership_function(x, 2.0, 3.0, 3.0),
        }
        domain = np.linspace(0, 3, 300)
        aggregated = np.maximum.reduce([
            memberships["low"]         * output_mf_array(domain, 0.0, 0.0, 1.0),
            memberships["medium_low"]  * output_mf_array(domain, 0.0, 1.0, 2.0),
            memberships["medium_high"] * output_mf_array(domain, 1.0, 2.0, 3.0),
            memberships["high"]        * output_mf_array(domain, 2.0, 3.0, 3.0),
        ])
        denominator = float(np.sum(aggregated))
        numerator   = float(np.sum(domain * aggregated))
        return numerator / denominator if denominator != 0.0 else 0.0

    def vital_score(vital: str, memberships: dict[str, float]) -> float:
        weights = set_weights_4 if vital in ("sp02", "fi02") else set_weights_7
        return sum(memberships[k] * weights[k] for k in memberships)

    results_dict = {
        key: fuzzify_outputs(vital_score(key, value))
        for key, value in degrees_of_membership.items()
    }

    return float(sum(results_dict.values()))
