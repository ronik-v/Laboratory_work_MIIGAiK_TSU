import networkx as nx

# Task parametrs n = VERTEKS_NUM \ p = PROBABILITY_RANDOM_EDGE
VERTEKS_NUM: int = 11
PROBABILITY_RANDOM_EDGE: float = 0.15


def main():
    round_val: int = 1
    # Create Erdos Renyi graph with given parametrs - n, p
    graph = nx.erdos_renyi_graph(VERTEKS_NUM, PROBABILITY_RANDOM_EDGE)
    # Mean peack degree
    average_degree = round(sum(dict(graph.degree()).values()) / VERTEKS_NUM, round_val)
    # Basic given formyla to calc mean peack degree
    theoretical_average_degree = round((VERTEKS_NUM - 1) * PROBABILITY_RANDOM_EDGE, round_val)
    print(f"average_degree = {average_degree}\t theoretical_average_degree = {theoretical_average_degree}")
    print(
        "Average degree of a vertex in the graph corresponds to the theoretical value" 
        if abs(average_degree - theoretical_average_degree) < 1e-6 else 
        "Average degree of a vertex in the graph does not match the theoretical value"
    )




if __name__ == "__main__":
    main()
