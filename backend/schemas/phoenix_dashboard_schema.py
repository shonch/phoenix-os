from typing import List, Dict, Any
from pydantic import BaseModel


class WeatherModel(BaseModel):
    emotion: str
    frisson: str
    grief: str
    overall: str


class IdentityModel(BaseModel):
    mirror: str
    archetypes: List[str]


class ThresholdModel(BaseModel):
    status: str
    details: List[str]


class FatigueModel(BaseModel):
    grind_state: str
    signals: List[str]


class ResonanceModel(BaseModel):
    top_tags: List[str]
    constellations: List[Dict[str, Any]]


class DetectiveModel(BaseModel):
    clues: List[str]


class PhoenixDashboard(BaseModel):
    summary: str
    weather: WeatherModel
    identity: IdentityModel
    thresholds: ThresholdModel
    fatigue: FatigueModel
    resonance: ResonanceModel
    detective: DetectiveModel

