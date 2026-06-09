from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HyperParams(BaseSettings):
    """
    alpha -> the degree of previous per-vital fuzzy scores retained each step by the ewma
    beta -> a scalar that controls the steepness of the trend factor sigmoidal transformation curve
    gamma -> a blending paramter that moves from an additive system (1) to a single-vital dominated final score (0)
    lookback_window -> the number of hours worth of data to include in the temporal engine 
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    alpha: float = Field(default=0.3, ge=0.0, le=1.0)
    beta: float = Field(default=1, ge=0.1, le=10.0)
    gamma: float = Field(default=1, ge=0.0, le=1.0)
    lookback_window: int = Field(default=24, ge=1, le=72)



