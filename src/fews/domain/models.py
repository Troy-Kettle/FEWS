from pydantic import BaseModel, Field, computed_field
from datetime import datetime

class Observation(BaseModel):
    """A singular set of observations -> To be assigned to a patient"""
    hr: int = Field(ge=10, le=240, description='BPM')
    sbp: int = Field(ge=20, le=240, description='mmHg')
    rr: int = Field(ge=10, le=55, description='Breaths per min')
    temp: float = Field(ge=30, le=44, description='Degrees C')
    sp02: int = Field(ge=70, le=100, description='%')
    fio2: int = Field(ge=20, le=90, description='Fraction of inspired oxygen (%)')
    time_of_obs:  datetime = Field(default_factory= datetime.now, description="Time of observation")






class ObservationMatrix(BaseModel):
    """
    A matrix of observations for a single patient, patients must have a unqiue patient ID.
    The temporal engine requires a min of 3 observations in the matrix, it validates the min number of obs itself. 
    """
    patient_id: int
    obs: list[Observation] = Field(min_length=1)

    
