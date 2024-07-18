from enum import Enum
from dataclasses import dataclass

class State(Enum):
    SUSCEPTIBLE = "negative"
    INFECTED = "positive"
    RESISTANT = "resistant"
    EXPOSED = "exposed"

class AgeGroup(Enum):
    YOUNG = 0
    ADULT = 1
    SENIOR = 2

class PartnerCount(Enum):
    LOW = "1 to 3"
    MEDIUM = "4 to 6"
    HIGH = "7 to 10"
    EXTREME = "11+"

class Gender(Enum):
    MALE = "M"
    FEMALE = "F"

class SexualOrientation(Enum):
    STRAIGHT = "straight"
    GAY = "gay"
    BISEXUAL = "bisexual"
    LESBIAN = "lesbian"

class PairingType(Enum):
    SEQUENTIAL = "sequential"
    CONCURRENT = "concurrent"

class PairOnSystem(Enum):
    ON = "TRUE"
    OFF = "FALSE"

@dataclass
class VirusParams:
    spread_chance: float = 0.4
    check_frequency: float = 0.4
    recovery_chance: float = 0.3
    gain_resistance_chance: float = 0.5

