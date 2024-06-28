from enum import Enum
from dataclasses import dataclass

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2

class AgeGroup(Enum):
    YOUNG = 0
    ADULT = 1
    SENIOR = 2

class Gender(Enum):
    MALE = 0
    FEMALE = 1

@dataclass
class VirusParams:
    spread_chance: float = 0.4
    check_frequency: float = 0.4
    recovery_chance: float = 0.3
    gain_resistance_chance: float = 0.5