import math
import mesa
import networkx as nx
from enum import Enum

from agents import Virus


class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2


def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)


def number_infected(model):
    return number_state(model, State.INFECTED)


def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, State.RESISTANT)


class SwabberModel(mesa.Model):
    """
    Swabber Model for the spread of multiple bacteria and viruses on a network.
    Currently only supports one virus.
    Uses Rényi random graph for the network.
    """

    def __init__(
        self,
        num_nodes=10,
        avg_node_degree=3,
        initial_outbreak_size=1,
        virus_spread_chance=0.4,
        virus_check_frequency=0.4,
        recovery_chance=0.3,
        gain_resistance_chance=0.5,
    ):
        super().__init__()
        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes

        # Probablity of edge creation is avg_node_degree / num_nodes (3/10 = 0.3).
        # Erdős-Rényi graph. Random graph with n nodes and probability p for edge creation.
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)

        # Create a grid of the network. Each node can contain multiple agents. (Not necessary in this model)
        self.grid = mesa.space.NetworkGrid(self.G)

        # Agents step in a random order.
        self.schedule = mesa.time.RandomActivation(self)

        # Set model parameters. Outbreak size is the number of infected agents at start.
        self.initial_outbreak_size = (initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes)

        # Spread chance is the probability that a susceptible neighbor will be infected.
        self.virus_spread_chance = virus_spread_chance

        # Virus check frequency is the frequency the nodes check whether they are infected by a virus.
        self.virus_check_frequency = virus_check_frequency

        # Recovery chance is the probability that the virus will be removed.
        self.recovery_chance = recovery_chance

        # Gain resistance chance is the probability that a recovered agent will become resistant to this virus in the future.
        self.gain_resistance_chance = gain_resistance_chance

        self.datacollector = mesa.DataCollector(
            model_reporters=
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Resistant": number_resistant,
                "Resistant/Susceptible Ratio": "resistant_susceptible_ratio"
            }
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = Infection(
                i,
                self,
                State.SUSCEPTIBLE,
                self.virus_spread_chance,
                self.virus_check_frequency,
                self.recovery_chance,
                self.gain_resistance_chance,
            )
            self.schedule.add(a)
            # Add the agent to the node
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = self.random.sample(list(self.G), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state = State.INFECTED

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(
                self, State.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


class Infection(Virus):
    """
    Individual Agent definition and its properties/interaction methods
    """

    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        virus_spread_chance,
        virus_check_frequency,
        recovery_chance,
        gain_resistance_chance,
    ):
        super().__init__(unique_id, model)
        
        # Whether the agent is susceptible, infected, or resistant to the virus.
        self.state = initial_state
        
        # Parameters for the agent's interaction with the virus.
        self.virus_spread_chance = virus_spread_chance

        # The frequency the agent checks whether they are infected by the virus.
        self.virus_check_frequency = virus_check_frequency

        # The probability that the agent will recover from the virus.
        self.recovery_chance = recovery_chance

        # The probability that the agent will become resistant to the virus in the future.
        self.gain_resistance_chance = gain_resistance_chance

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighborhood(
            self.pos, include_center=False
        )
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.SUSCEPTIBLE
        ]
        for a in susceptible_neighbors:
            if self.random.random() < self.virus_spread_chance:
                a.state = State.INFECTED

    def try_gain_resistance(self):
        if self.random.random() < self.gain_resistance_chance:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        if self.random.random() < self.recovery_chance:
            # Success
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def try_check_situation(self):
        # If check is successful and infected, try to remove the infection.
        if (self.random.random() < self.virus_check_frequency) and (self.state is State.INFECTED):
            self.try_remove_infection()

    def step(self):

        # If the agent is infected, try to infect neighbors.
        if self.state is State.INFECTED:
            self.try_to_infect_neighbors()
        
        # Try to check the whether the agent is infected.
        self.try_check_situation()