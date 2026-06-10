"""
This module defines the membership functions based on the CSV files provided.
"""

from pathlib import Path
from fews.config import MembershipCsvFiles
import csv


class VitalMembershipFunctions:
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


def load_membership_functions() -> dict: 

    config = MembershipCsvFiles()

    vital_sign_paths = {
        "hr": config.hr,
        "sbp": config.sbp,
        "rr": config.rr,
        "temp": config.temp,
        "sp02": config.spo2,
        "fi02": config.fio2,
    }

    all_vital_lookup = {}

    def read_csv(path: Path) -> dict:
        """
        lookup -> fuzzy_set_name ->  (value, membeship degree)
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



    for key, path in vital_sign_paths.items():
        all_vital_lookup[key] = read_csv(path)
    

    return all_vital_lookup

mf = VitalMembershipFunctions(load_membership_functions())

print(mf.degree_of_membership('hr', 90))
