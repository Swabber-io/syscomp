from enum import Enum
from dataclasses import dataclass

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2
    EXPOSED = 3
    OFF = 4

class AgeGroup(Enum):
    YOUNG = 0
    ADULT = 1
    SENIOR = 2

class Gender(Enum):
    MALE = 0
    FEMALE = 1

class SexualPreference(Enum):
    HETEROSEXUAL = 0
    HOMOSEXUAL = 1
    BISEXUAL = 2

class PairingType(Enum):
    SEQUENTIAL = 0
    RANDOM = 1

class SystemPairing(Enum):
    ON = 0
    OFF = 1
    BOTH = 2

@dataclass
class VirusParams:
    spread_chance: float = 0.4
    check_frequency: float = 0.4
    recovery_chance: float = 0.3
    gain_resistance_chance: float = 0.5

