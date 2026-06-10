"""
Take Observation and a VitalMembershipFunctions objects and returns the degree of membership for every vital across every fuzzy set.
"""
from fews.domain import Observation, VitalMembershipFunctions

def fuzzifier(observation: Observation, membership_function: VitalMembershipFunctions) -> dict[str, dict[str, float]]:

    result = {}

    for key, value in observation.model_dump().items():
        result[key] = membership_function.degree_of_membership(key, value)


    return result
