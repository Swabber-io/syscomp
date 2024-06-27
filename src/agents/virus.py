import mesa
from abc import abstractmethod

class Virus(mesa.Agent):

    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)

    @abstractmethod
    def step(self) -> None:
        return super().step()

    @abstractmethod
    def advance(self) -> None:
        return super().advance()
    
    @abstractmethod
    def remove(self) -> None:
        return super().remove()

