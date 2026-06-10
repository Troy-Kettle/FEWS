"""
fews.config.data_config.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
This module loads the CSV files from data folder into a pydantic BaseSettings model
"""


from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, FilePath
from pathlib import Path


def get_root_dir():
    """
    Finds the data folder -> concats the data folder root and file name -> populates the default values with the new paths
    """
    current = Path(__file__).resolve()

    for parent in current.parents:
        if (parent / "poetry.lock").exists():
            return parent

    return current.parent

ROOT_DIR = get_root_dir()
path_suffix = [Path('data/heart_rate_membership_functions.csv'), Path('data/systolic_blood_pressure_membership_functions.csv'),
                Path('data/respiratory_rate_membership_functions.csv'), Path('data/temperature_membership_functions.csv'),
                Path('data/inspired_oxygen_concentration_membership_functions.csv'), Path('data/supplementary_oxygen_lmin_membership_functions.csv')]
default_paths = [Path(ROOT_DIR) / path for path in path_suffix]



class MembershipCsvFiles(BaseSettings):
    """
    This class is a configuration class that contains the paths to the CSV files required to make the memberhsip functions.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    hr: FilePath = Field(default= default_paths[0])
    sbp: FilePath = Field(default= default_paths[1])
    rr: FilePath = Field(default= default_paths[2])
    temp: FilePath = Field(default= default_paths[3])
    fio2: FilePath = Field(default= default_paths[4])
    spo2: FilePath = Field(default= default_paths[5])
