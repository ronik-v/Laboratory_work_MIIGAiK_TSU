import networkx as nx
import matplotlib.pyplot as plt

from typing import Optional

__author__ = "Андроник Вадим 1 курс исит 4-см"


class Graph:
    def __init__(self, nodes: list[tuple[int, int]], edges: list[tuple[int, int]]) -> None:
        self.nodes = nodes
        self.edges = edges
        self.graph: Optional[nx.DiGraph] = None

    def create(self) -> None:
        """
        Function that create graph[nx]
        Function need call before called other class methods

        :return:
        """
        self.graph = nx.DiGraph() # init graph
        # List generator expression that create graph
        _ = [
            self.graph.add_node(i, pos=(x, y), value=y) for i, (x, y) in enumerate(self.nodes)
        ]
        self.graph.add_edges_from(self.edges)
    

    def graph_centrality(self, round_val: int) -> dict[int, float]:
        """
        :param round_val: Value that rounding centrality graph values
        :return: centrality graph values between graphs nodes
        """
        centrality_values: dict[int, float] = nx.degree_centrality(self.graph)
        for key, value in centrality_values.items():
            centrality_values[key] = round(value, round_val)
        return centrality_values

    def plot(self) -> None:
        """
        Plotting graph
        :return:
        """
        if self.graph is None:
            raise TypeError("Graph need to be created for plotting")
        
        pos = nx.get_node_attributes(self.graph, "pos")
        plt.figure(figsize=(10, 5))
        nx.draw(self.graph, pos, node_size=500, node_color="skyblue", font_size=10, font_color="black", font_weight="bold", edge_color="gray")
        node_labels = nx.get_node_attributes(self.graph, "value")
        custom_labels = {k: f"{k}\n({v})" for k, v in node_labels.items()}
        nx.draw_networkx_labels(self.graph, pos, labels=custom_labels, font_color="red")
        
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels={(u, v): f"{u}->{v}" for u, v in self.graph.edges()})
        plt.show()



def main() -> None:
    nodes = [(0, 3), (1, 1), (2, 0), (3, 5), (4, 0), (5, 1), (6, 3)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
    graph = Graph(nodes, edges)
    graph.create()
    centrality_graph_values: dict[int, float] = graph.graph_centrality(round_val=3)
    print(f"Calculation of centrality measures for a given graph = {centrality_graph_values}")
    graph.plot()    



if __name__ == "__main__":
    main()