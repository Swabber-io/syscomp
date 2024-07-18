from . import Bacteria, Virus, Parasite, Infection
from datetime import datetime
from impl_config import State, AgeGroup, Gender, SexualOrientation, PairingType, PartnerCount, PairOnSystem
import mesa
from typing import List, Optional, Any

class UserAgent(mesa.Agent):
    """
    Individual Agent definition and its properties/interaction methods
    """

    def __init__(
        self,
        agent_id: int,
        age_group: AgeGroup,
        gender: Gender,
        sexual_preference: SexualOrientation,
        last_sti_test_date: datetime,
        sti_status: State,
        partnering_type: PairingType,
        partner_count: PartnerCount,
        location: str,
        pair_on_system: PairOnSystem,
        model: mesa.Model,
        score : int = 700,
        infections: Optional[List[Infection]] = None,
    ) -> None:
        
        super().__init__(agent_id, model)
        self.agent_id = agent_id
        self.age_group = age_group
        self.gender = gender
        self.sexual_preference = sexual_preference
        self.last_sti_test_date = last_sti_test_date
        self.sti_status = sti_status
        self.partnering_type = partnering_type
        self.partner_count = partner_count
        self.location = location
        self.pair_on_system = pair_on_system
        self.model = model
        self.score = score
        self.infections = infections if infections is not None else []
        

    def __str__(self) -> str:
        return f"UserAgent {self.unique_id}"

    def determine_state(self) -> State:
        return self.sti_status

    def step(self) -> None:
        for infection in self.infections[:]:
            self.sti_status = infection.step(self.sti_status, self.model, self.pos)
            if self.sti_status in {State.SUSCEPTIBLE, State.RESISTANT}:
                self.infections.remove(infection)