from pydantic import BaseModel, ConfigDict, Field, computed_field
from datetime import datetime
from typing import Self

class Observation(BaseModel):
    """A singular set of observations -> To be assigned to a patient"""
    hr: float = Field(ge=10, le=240, description='BPM')
    sbp: float = Field(ge=20, le=240, description='mmHg')
    rr: float = Field(ge=10, le=55, description='Breaths per min')
    temp: float = Field(ge=30, le=44, description='Degrees C')
    sp02: float = Field(ge=70, le=100, description='%')
    fio2: float = Field(ge=20, le=90, description='Fraction of inspired oxygen (%)')
    time_of_obs:  datetime = Field(default_factory= datetime.now, description="Time of observation")






class ObservationMatrix(BaseModel):
    """
    A matrix of observations for a single patient, patients must have a unqiue patient ID.
    The temporal engine requires a min of 3 observations in the matrix, it validates the min number of obs itself. 
    """
    model_config = ConfigDict(frozen=False)

    patient_id: int
    obs: list[Observation] = Field(min_length=1)

    @classmethod
    def from_first_observation(cls, patient_id: int, first_obs: Observation) -> Self:
        return cls(patient_id = patient_id, obs = [first_obs])

    def add_observation(self, obs: Observation) -> None:
        self.obs.append(obs)
    
