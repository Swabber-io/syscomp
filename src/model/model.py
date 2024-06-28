import mesa
import networkx as nx
from sti import Virus, UserAgent
from impl_config import State, VirusParams, AgeGroup, Gender

class SwabberModel(mesa.Model):
    """
    Swabber Model for the spread of multiple bacteria and viruses on a network.
    Currently only supports one virus.
    Uses Erdős-Rényi random graph for the network.
    """

    def __init__(
        self,
        num_nodes: int = 10,
        avg_node_degree: int = 3,
        initial_outbreak_size: int = 1,
        virus_spread_chance: float = 0.4,
        virus_check_frequency: float = 0.4,
        recovery_chance: float = 0.3,
        gain_resistance_chance: float = 0.5,
    ) -> None:
        super().__init__()
        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes

        # Probability of edge creation is avg_node_degree / num_nodes (3/10 = 0.3).
        # Erdős-Rényi graph. Random graph with n nodes and probability p for edge creation.
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = mesa.space.NetworkGrid(self.G)
        self.schedule = mesa.time.RandomActivation(self)
        self.initial_outbreak_size = min(initial_outbreak_size, num_nodes)

        # Virus parameters
        #self.virus_spread_chance = VirusParams.spread_chance
        #self.virus_check_frequency = VirusParams.check_frequency
        #self.recovery_chance = VirusParams.recovery_chance
        #self.gain_resistance_chance = VirusParams.gain_resistance_chance

        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Infected": self.number_infected,
                "Susceptible": self.number_susceptible,
                "Resistant": self.number_resistant,
                "Resistant/Susceptible Ratio": self.resistant_susceptible_ratio,
            }
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            agent = UserAgent(
                unique_id=i,
                model=self,
                age_group=AgeGroup.YOUNG,
                gender=Gender.MALE,
                score=700,
                infections=[],
            )
            self.schedule.add(agent)
            # Add the agent to the node
            self.grid.place_agent(agent, node)

        # Infect some nodes
        infected_nodes = self.random.sample(list(self.G), self.initial_outbreak_size)
        for agent in self.grid.get_cell_list_contents(infected_nodes):
            agent.infections.append(Virus(
                self.virus_spread_chance,
                self.virus_check_frequency,
                self.recovery_chance,
                self.gain_resistance_chance,
            ))
            agent.user_state = State.INFECTED

        self.running = True
        self.datacollector.collect(self)

    def number_state(self, state: State) -> int:
        """Returns the number of agents in a given state."""
        return sum(1 for agent in self.grid.get_all_cell_contents() if agent.user_state is state)
    
    def resistant_susceptible_ratio(self) -> float:
        """Returns the ratio of resistant to susceptible agents."""
        try:
            return self.number_state(State.RESISTANT) / self.number_state(State.SUSCEPTIBLE)
        except ZeroDivisionError:
            return float('inf')

    def number_infected(self) -> int:
        """Returns the number of infected agents."""
        return self.number_state(State.INFECTED)

    def number_susceptible(self) -> int:
        """Returns the number of susceptible agents."""
        return self.number_state(State.SUSCEPTIBLE)

    def number_resistant(self) -> int:
        """Returns the number of resistant agents."""
        return self.number_state(State.RESISTANT)

    def step(self) -> None:
        """Advance the model by one step."""
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n: int) -> None:
        """Run the model for n steps."""
        for _ in range(n):
            self.step()
