from fews.domain import ObservationMatrix, Observation, VitalMembershipFunctions
from fews.config import HyperParams
from fews.engine import fuzzifier
from fews.engine.defuzzifier import _fuzzify_outputs, _map_to_concern_levels, _apply_threshold

import statsmodels.api as sm
from datetime import timedelta
from math import exp


MIN_OBSERVATIONS = 3

def temporal_filtering(obs_matrix: ObservationMatrix, params: HyperParams) -> list[Observation]:
    latest = max(obs_matrix.obs, key=lambda obs: obs.time_of_obs)
    filtered = [
    obs for obs in obs_matrix.obs
    if latest.time_of_obs - obs.time_of_obs <= timedelta(hours= params.lookback_window)
    ]

    return filtered

def min_num_of_obs(obs_matrix_filtered: list[Observation]) -> bool:
    num_of_obs = len(obs_matrix_filtered)

    return num_of_obs >= MIN_OBSERVATIONS 


def fuzzify_filtered(obs_matrix_filtered: list[Observation], membership_function: VitalMembershipFunctions) -> list[dict[str, dict[str, float]]]:
    return [fuzzifier(obs, membership_function) for obs in obs_matrix_filtered]

def score_filtered(fuzzified_filtered: list[dict[str, dict[str, float]]]) -> list[dict[str, float]]:
    return [
        {vital: _fuzzify_outputs(_apply_threshold(_map_to_concern_levels(memberships)))
         for vital, memberships in obs.items()}
        for obs in fuzzified_filtered
    ]

def ewma_per_vital(score_filtered: list[dict[str, float]], params: HyperParams) -> dict[str, list[float]]:
    ewma_values = {}
    for vital in score_filtered: 
        for vital_name, score in vital.items():

            if not vital_name in ewma_values:
                ewma = score
                ewma_values[vital_name] = [ewma]
            else:
                ewma = params.alpha * score + (1 - params.alpha) * ewma
                ewma_values[vital_name].append(ewma) 

    return ewma_values

def ewma_slopes(ewma_values: dict[str, list[float]], obs_matrix_filtered: list[Observation]) -> dict[str, float]:

    slopes = {} 

    for vital_name, ewma_scores in ewma_values.items():
        time_of_first_obs = obs_matrix_filtered[0].time_of_obs

        timestamp_list = sm.add_constant([(obs.time_of_obs - time_of_first_obs).total_seconds() / 3600 for obs in obs_matrix_filtered])

        ols_model = sm.OLS(ewma_scores, timestamp_list).fit()

        slopes[vital_name] = ols_model.params[1]



    return slopes 


def trend_factor(slopes: dict[str, float], params: HyperParams) -> dict[str, float]:

    trend_factors = {}

    for vital_name, slope in slopes.items():
        trend_factors[vital_name] = max(0.0, 2 / (1 + exp(-params.beta * slope)) - 1)

    return trend_factors


def adjusted_scores(ewma_values: dict[str, list[float]], trend_factors: dict[str, float]) -> dict[str, float]: 
    return {vital_name: ewma_values[vital_name][-1] + trend_factor * (3 - ewma_values[vital_name][-1]) for vital_name, trend_factor in trend_factors.items()}

    
def gamma_blending(params: HyperParams, adjusted_scores: dict[str, float]) -> float:
    max_based_total = 18 * (max(adjusted_scores.values()) / 3)
    additive_total = sum(adjusted_scores.values())
    return (1 - params.gamma) * max_based_total + params.gamma * additive_total


def temporal_engine(obs_matrix: ObservationMatrix, params: HyperParams, membership_function: VitalMembershipFunctions) -> float:

    filtered = temporal_filtering(obs_matrix, params)
    
    if  not min_num_of_obs(filtered):
        return 0.0

    filtered_fuzzified = fuzzify_filtered(filtered, membership_function)

    filtered_score = score_filtered(filtered_fuzzified)

    per_vital_ewma = ewma_per_vital(filtered_score, params)

    slopes_of_ewmas = ewma_slopes(per_vital_ewma, filtered)
    
    trend_factors = trend_factor(slopes_of_ewmas, params)

    scores_adjusted = adjusted_scores(per_vital_ewma, trend_factors)

    return gamma_blending(params, scores_adjusted)

