import mesa
import random
from abc import abstractmethod, ABC
from utils.impl_config import State
from typing import Any

class Infection(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def try_to_infect_neighbors(self, model: mesa.Model, pos: Any) -> None:
        pass

    @abstractmethod
    def try_gain_resistance(self, state: State) -> State:
        pass

    @abstractmethod
    def try_remove_infection(self, state: State) -> State:
        pass

    @abstractmethod
    def try_check_situation(self, state: State) -> State:
        pass

    @abstractmethod
    def step(self, state: State, model: mesa.Model, pos: Any) -> State:
        pass

class Virus(Infection):
    """
    Represents a virus infection with specific probabilities for spreading,
    recovery, and gaining resistance.
    """

    def __init__(self, spread_chance: float, check_frequency: float, recovery_chance: float, gain_resistance_chance: float) -> None:
        super().__init__()
        self.virus_spread_chance = spread_chance
        self.virus_check_frequency = check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

    def try_to_infect_neighbors(self, model: mesa.Model, pos: Any) -> None:
        neighbors_nodes = model.grid.get_neighborhood(pos, include_center=False)
        susceptible_neighbors = [
            agent for agent in model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.sti_status == State.SUSCEPTIBLE
        ]
        for neighbor in susceptible_neighbors:
            if random.random() < self.virus_spread_chance:
                neighbor.sti_status = State.INFECTED
                neighbor.infections.append(Virus(
                    self.virus_spread_chance,
                    self.virus_check_frequency,
                    self.recovery_chance,
                    self.gain_resistance_chance,
                ))

    def try_gain_resistance(self, state: State) -> State:
        if random.random() < self.gain_resistance_chance:
            state = State.RESISTANT
        return state

    def try_remove_infection(self, state: State) -> State:
        if random.random() < self.recovery_chance:
            state = State.SUSCEPTIBLE
            state = self.try_gain_resistance(state)
        else:
            state = State.INFECTED
        return state

    def try_check_situation(self, state: State) -> State:
        if random.random() < self.virus_check_frequency and state == State.INFECTED:
            state = self.try_remove_infection(state)
        return state

    def step(self, state: State, model: mesa.Model, pos: Any) -> State:
        if state == State.INFECTED:
            self.try_to_infect_neighbors(model, pos)
        state = self.try_check_situation(state)
        return state
    
    def __str__(self) -> str:
        return f"VIRUS"
    
    def __repr__(self) -> str:
        return self.__str__()

class Bacteria(Infection):
    def __init__(self) -> None:
        super().__init__()

    def try_to_infect_neighbors(self, model: mesa.Model, pos: Any) -> None:
        pass  # Bacteria-specific infection logic

    def try_gain_resistance(self, state: State) -> State:
        pass  # Bacteria-specific resistance logic

    def try_remove_infection(self, state: State) -> State:
        pass  # Bacteria-specific infection removal logic

    def try_check_situation(self, state: State) -> State:
        pass  # Bacteria-specific situation checking

    def step(self, state: State, model: mesa.Model, pos: Any) -> State:
        pass  # Bacteria-specific step logic

class Parasite(Infection):
    def __init__(self) -> None:
        super().__init__()

    def try_to_infect_neighbors(self, model: mesa.Model, pos: Any) -> None:
        pass  # Parasite-specific infection logic

    def try_gain_resistance(self, state: State) -> State:
        pass  # Parasite-specific resistance logic

    def try_remove_infection(self, state: State) -> State:
        pass  # Parasite-specific infection removal logic

    def try_check_situation(self, state: State) -> State:
        pass  # Parasite-specific situation checking

    def step(self, state: State, model: mesa.Model, pos: Any) -> State:
        pass  # Parasite-specific step logic