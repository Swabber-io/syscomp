from . import Bacteria, Virus, Parasite, Infection
from impl_config import State, AgeGroup, Gender, SexualPreference, PairingType, SystemPairing
import mesa
from typing import List, Optional, Any

class UserAgent(mesa.Agent):
    """
    Individual Agent definition and its properties/interaction methods
    """

    def __init__(
        self,
        unique_id: int,
        model: mesa.Model,
        age_group: AgeGroup,
        gender: Gender,
        sexual_preference: SexualPreference,
        pair_type: PairingType,
        system_pairing: SystemPairing,
        partner_preference: State,
        score : int = 700,
        number_of_sexual_partners: int = 1,
        infections: Optional[List[Infection]] = None,
    ) -> None:
        
        super().__init__(unique_id, model)
        self.user_ID = unique_id
        self.infections = infections if infections is not None else []
        self.user_state = self.determine_state()
        self.age_group = age_group
        self.sexual_preference = sexual_preference
        self.pair_type = pair_type
        self.system_pairing = system_pairing
        self.partner_preference = partner_preference
        self.gender = gender
        self.score = score
        self.number_of_sexual_partners = number_of_sexual_partners

    def __str__(self) -> str:
        return f"UserAgent {self.unique_id}"

    def determine_state(self) -> bool:
        return State.INFECTED if self.infections else State.SUSCEPTIBLE

    def step(self) -> None:
        for infection in self.infections[:]:
            self.user_state = infection.step(self.user_state, self.model, self.pos)
            if self.user_state in {State.SUSCEPTIBLE, State.RESISTANT}:
                self.infections.remove(infection)