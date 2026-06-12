"""
This module defines the membership functions based on the CSV files provided.
Provides utilities to generate the MF look up tables from the CSV files and derive the degree of memberships.
Typical usage::
    csv_files = MembershipCsvFiles()
    mf = load_membership_functions(csv_files)
    mf.degree_of_membership('hr', 90)
"""
from pathlib import Path
from fews.config import MembershipCsvFiles
import csv


class VitalMembershipFunctions:
    """
    Holds the membership functions from read_csv and returns the degree of membership as a dict per fuzzy set for the specified vital sign.
    The input to this class is the lookup table dict generated from the load_membership_functions() function.
    """
    def __init__(self, lookup_table: dict[str, dict[str, dict[float, float]]]) -> None:
        self.lookup_table = lookup_table

    def degree_of_membership(self, vital_sign: str, value: float) -> dict[str, float]:
        if vital_sign not in self.lookup_table:
            raise KeyError(f"Vital sign '{vital_sign}' not found.")
        result = {}
        for fuzzy_set, members in self.lookup_table[vital_sign].items():
            if value not in members:
                raise KeyError(f"Value {value} not found")
            result[fuzzy_set] = members[value]
        return result


type MembershipFunctions = dict[str, VitalMembershipFunctions]


def load_membership_functions(csv_files: MembershipCsvFiles) -> VitalMembershipFunctions:
    """
    Creates a dict of dict of dict that holds all membership functions based on the provided CSV files.
    """
    vital_sign_paths = {
        "hr": csv_files.hr,
        "sbp": csv_files.sbp,
        "rr": csv_files.rr,
        "temp": csv_files.temp,
        "spo2": csv_files.spo2,
        "fio2": csv_files.fio2,
    }

    def read_csv(path: Path) -> dict:
        """
        lookup -> fuzzy_set_name -> (value, membership degree)
        """
        lookup = {}
        with open(path, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                value = float(row['Value'])
                for col, membership in row.items():
                    if col == 'Value':
                        continue
                    if col not in lookup:
                        lookup[col] = {}
                    lookup[col][value] = float(membership)
        return lookup

    all_vital_lookup = {}
    for key, path in vital_sign_paths.items():
        all_vital_lookup[key] = read_csv(path)

    return VitalMembershipFunctions(all_vital_lookup)
