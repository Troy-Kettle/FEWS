"""
fews.ingestion.parser.py
~~~~~~~~~~~~~~~~

This is the module that takes in the raw clinical observations as a list from CLI
then returns an Observation object. 
"""


from fews.domain import Observation

def parse_obs(cli_input: list[int | float]) -> Observation:
    """
    Takes in a list of user inputs from CLI and returns an Observation object.
    Type safety is handled by Observation itself.
    """

    validation_input = dict(zip(Observation.model_fields, cli_input))

    return Observation.model_validate(validation_input)
