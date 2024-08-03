import mesa
import networkx as nx
import numpy as np
from utils import fetch_csv_data
from sti import Virus, UserAgent
from utils.impl_config import State

INIT_DATA_PATH = "../db/csv/user_list.csv"

class SwabberModel(mesa.Model):
    """
    Swabber Model for the spread of multiple bacteria and viruses on a network.
    Currently only supports one virus.
    Uses a custom dynamic network where edges form probabilistically.
    """

    def __init__(
        self,
        num_nodes: int = 250,
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

        # Initialize mesa objects
        self.grid = mesa.space.NetworkGrid(self.G)
        self.schedule = mesa.time.RandomActivation(self)
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Infected": self.number_infected,
                "Susceptible": self.number_susceptible,
                "Resistant": self.number_resistant,
                "Resistant/Susceptible Ratio": self.infected_susceptible_ratio,
            }
        )

        # Dictionary to track when each edge was created
        self.edge_creation_times = {}

        # Load agents from CSV
        self._setup_initial_agents()
        
        # Initialize the likelihood matrix
        self._setup_initial_likelihood_matrix()

        # Collect data
        self.running = True
        self.datacollector.collect(self)

    def _setup_initial_agents(self) -> None:
        """Load agents from CSV and place them on the grid."""
        agents = fetch_csv_data(INIT_DATA_PATH, self.num_nodes)
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
                # Go trough Infection DB
                # TODO
                agent.infections.append(Virus())

            self.schedule.add(agent)
            self.grid.place_agent(agent, node)

    def _setup_initial_likelihood_matrix(self) -> None:
        """Initialize the likelihood matrix."""

        self.likelihood_matrix = np.zeros((self.num_nodes, self.num_nodes))
        self.likelihood_matrix[np.triu_indices(self.num_nodes, 1)] = 0
        self.likelihood_matrix[np.tril_indices(self.num_nodes, -1)] = 1 / (self.num_nodes - 1)
        self.likelihood_matrix[np.diag_indices(self.num_nodes)] = 0

        agent_ids = [agent.unique_id for agent in self.schedule.agents]
        self.agent_id_mapping = {index: agent_id for index, agent_id in enumerate(agent_ids)}

        x, y = np.tril_indices(self.num_nodes, -1)
        for id_1, id_2 in zip(x, y):
            agent_1 = self.schedule.agents[id_1]
            agent_2 = self.schedule.agents[id_2]
            if agent_1.location != agent_2.location:
                self.likelihood_matrix[id_1, id_2] = self.likelihood_matrix[id_1, id_2]
            
            elif agent_1.sexual_preference != agent_2.sexual_preference:
                self.likelihood_matrix[id_1, id_2] = 0

            elif agent_1.age_group != agent_2.age_group:
                self.likelihood_matrix[id_1, id_2] = 0

            elif agent_1.partnering_type != agent_2.partnering_type:
                self.likelihood_matrix[id_1, id_2] = 0

        self.recalculate_probabilities()

        
    def recalculate_probabilities(self):
        """Renormalize the likelihood matrix."""
        for i in range(self.num_nodes):
            sum_of_row_idx = np.sum(self.likelihood_matrix, axis=0)
            sum_of_col_idx = np.sum(self.likelihood_matrix, axis=1)
            self.likelihood_matrix[i: ] = self.likelihood_matrix[i: ] / (sum_of_row_idx[i] + sum_of_col_idx[i])
            self.likelihood_matrix[ :i] = self.likelihood_matrix[ :i] / (sum_of_row_idx[i] + sum_of_col_idx[i])

    def number_state(self, state: State) -> int:
        """Returns the number of agents in a given state."""
        return sum(1 for agent in self.grid.get_all_cell_contents() if agent.sti_status is state)
    
    def agent_scores(self) -> dict:
        """Returns a dictionary of agent scores."""
        return {agent.unique_id: agent.score for agent in self.grid.get_all_cell_contents()}
    
    def infected_susceptible_ratio(self) -> float:
        """Returns the ratio of infected to susceptible agents."""
        try:
            return self.number_state(State.INFECTED) / self.number_state(State.SUSCEPTIBLE)
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
        self.current_step += 1

        # 1. update preferences
        # 2. update likelihood matrix
        # 3. update edges
        self.update_edges()
        # 4. update scores
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n: int) -> None:
        """Run the model for n steps."""
        for _ in range(n):
            self.step()
        
    def update_edges(self):
        """Update edges probabilistically based on the likelihood matrix."""
        triu_indices = np.triu_indices(self.num_nodes, -1)
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
                           if self.current_step - creation_time >= 2000]

        for edge in edges_to_remove:
            self.G.remove_edge(*edge)
            del self.edge_creation_times[edge]
