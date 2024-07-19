import mesa
import networkx as nx
import numpy as np
from utils import fetch_csv_data
from sti import Virus, UserAgent
from utils.impl_config import State, VirusParams, AgeGroup, Gender, SexualOrientation, PairingType, PairOnSystem

class SwabberModel(mesa.Model):
    """
    Swabber Model for the spread of multiple bacteria and viruses on a network.
    Currently only supports one virus.
    Uses a custom dynamic network where edges form probabilistically.
    """

    def __init__(
        self,
        num_nodes: int = 1000,
        initial_outbreak_size: int = 1,
        virus_spread_chance: float = 0.4,
        virus_check_frequency: float = 0.4,
        recovery_chance: float = 0.2,
        gain_resistance_chance: float = 0.5,
    ) -> None:
        """
        Create a new Swabber model.

        Args:
            num_nodes: Number of nodes in the network.
            avg_node_degree: Average degree of nodes.
            initial_outbreak_size: Initial number of infected nodes.
            virus_spread_chance: Probability of virus spreading to a connected node.
            virus_check_frequency: Frequency of checking for virus spread.
            recovery_chance: Probability of an infected node recovering.
            gain_resistance_chance: Probability of gaining resistance after recovery.
        """
        super().__init__()
        self.num_nodes = num_nodes
        self.current_step = 0

        # Initialize an empty graph with nodes
        self.G = nx.Graph()
        self.G.add_nodes_from(range(self.num_nodes))

        # Initialize the likelihood matrix with values between 0.01 and 0.1
        self.likelihood_matrix = np.zeros((self.num_nodes, self.num_nodes))
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                self.likelihood_matrix[i, j] = self.likelihood_matrix[j, i] = 0.001 + (0.01 - 0.001) * np.random.rand()

        self.grid = mesa.space.NetworkGrid(self.G)
        self.schedule = mesa.time.RandomActivation(self)
        self.initial_outbreak_size = min(initial_outbreak_size, num_nodes)

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

        # Dictionary to track when each edge was created
        self.edge_creation_times = {}

        agents = fetch_csv_data('../db/csv/user_list.csv', self.num_nodes)
        # Create agents
        for i, node in enumerate(self.G.nodes):
            agent_data = agents[i]
            agent = UserAgent(
                agent_id=agent_data['agent_id'],
                age_group=agent_data['age_group'],
                gender=agent_data['gender'],
                sexual_preference=agent_data['sexual_orientation'],
                last_sti_test_date=agent_data['last_sti_test_date'],
                sti_status=agent_data['sti_status'],
                partnering_type=agent_data['partnering_type'],
                partner_count=agent_data['partner_count'],
                location=agent_data['loc'],
                pair_on_system=agent_data['pair_on_system'],
                model=self,
            )
            if agent_data['sti_status'] == State.INFECTED:
                agent.infections.append(Virus(
                    self.virus_spread_chance,
                    self.virus_check_frequency,
                    self.recovery_chance,
                    self.gain_resistance_chance,
                ))

            self.schedule.add(agent)
            self.grid.place_agent(agent, node)

        self.running = True
        self.datacollector.collect(self)

    def number_state(self, state: State) -> int:
        """Returns the number of agents in a given state."""
        return sum(1 for agent in self.grid.get_all_cell_contents() if agent.sti_status is state)
    
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

    def update_edges(self):
        """Update edges probabilistically based on the likelihood matrix."""
        triu_indices = np.triu_indices(self.num_nodes, 1)
        probabilities = self.likelihood_matrix[triu_indices]
        rand_values = np.random.rand(len(probabilities))

        new_edges = np.where(rand_values < probabilities)
        edge_list = list(zip(triu_indices[0][new_edges], triu_indices[1][new_edges]))

        edge_list = [(int(u), int(v)) for u, v in edge_list]

        self.G.add_edges_from(edge_list)

        for edge in edge_list:
            self.edge_creation_times[edge] = self.current_step

        self.likelihood_matrix[triu_indices[0][new_edges], triu_indices[1][new_edges]] = 0
        self.likelihood_matrix[triu_indices[1][new_edges], triu_indices[0][new_edges]] = 0
        edges_to_remove = [edge for edge, creation_time in self.edge_creation_times.items()
                           if self.current_step - creation_time >= 30]

        for edge in edges_to_remove:
            self.G.remove_edge(*edge)
            del self.edge_creation_times[edge]

    def step(self) -> None:
        """Advance the model by one step."""
        self.current_step += 1
        self.update_edges()
        # 
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n: int) -> None:
        """Run the model for n steps."""
        for _ in range(n):
            self.step()
