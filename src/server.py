import mesa
from utils.impl_config import State
from model import SwabberModel

def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        return {State.INFECTED: "#B94848", State.SUSCEPTIBLE: "#0ABFB3"}.get(
            agent.sti_status, "#808080"
        )

    def edge_color(agent1, agent2):
        if State.RESISTANT in (agent1.sti_status, agent2.sti_status):
            return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        if State.RESISTANT in (agent1.sti_status, agent2.sti_status):
            return 2
        return 1

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    def format_virus_list(viruses):
        if not viruses:
            return "None"
        return "<br>".join(str(virus) for virus in viruses)

    portrayal = {}
    portrayal["nodes"] = [
        {
            "shape": "rect",
            "filled": "true",
            "size": 25,
            "color": node_color(agents[0]),
            "text": agents[0].score,
            "text_color": "white",
            "tooltip": (
                f"id: {agents[0].agent_id}<br>"
                f"state: {agents[0].sti_status.name} <br>"
                f"score: {agents[0].score} <br>"
                f"age_group: {agents[0].age_group.name} <br>"
                f"gender: {agents[0].gender.name} <br>"
                f"sexual_preference: {agents[0].sexual_preference.name} <br>"
                f"pair_type: {agents[0].partnering_type.name} <br>"
                f"system_pairing: {agents[0].pair_on_system.name} <br>"
                f"infections: {format_virus_list(agents[0].infections)}"
            ),
            
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


network = mesa.visualization.NetworkModule(
    portrayal_method=network_portrayal,
    canvas_height=500,
    canvas_width=500,
)

chart = mesa.visualization.ChartModule(
    [
        {"Label": "Infected", "Color": "#B94848"},
        {"Label": "Susceptible", "Color": "#0ABFB3"},
        {"Label": "Resistant", "Color": "#808080"},
    ]
)

degree_dist_chart = mesa.visualization.ChartModule(
    [{"Label": "Degree Distribution", "Color": "#1f77b4"}],
    canvas_height=300,
    canvas_width=600
)

clustering_coeff_chart = mesa.visualization.ChartModule(
    [{"Label": "Clustering Coefficient", "Color": "#ff7f0e"}],
    canvas_height=300,
    canvas_width=600
)

avg_path_length_chart = mesa.visualization.ChartModule(
    [{"Label": "Average Path Length", "Color": "#2ca02c"}],
    canvas_height=300,
    canvas_width=600
)

def get_infected_susceptible_ratio(model):
    ratio = model.infected_susceptible_ratio()
    ratio_text = "&infin;" if ratio is float('inf') else f"{ratio:.2f}"
    infected_text = model.number_infected()
    return f"Resistant/Susceptible Ratio: {ratio_text}<br>Infected Remaining: {infected_text}"


model_params = {
    "num_nodes": mesa.visualization.Slider(
        name="Number of agents",
        value=100,
        min_value=10,
        max_value=1000,
        step=1,
        description="Choose how many agents to include in the model",
    )}

server = mesa.visualization.ModularServer(
    model_cls=SwabberModel,
    visualization_elements=[
        network,
        get_infected_susceptible_ratio,
        chart,
        degree_dist_chart,
        clustering_coeff_chart,
    ],
    name="Virus on Network Model",
    model_params=model_params,
)
server.port = 8521