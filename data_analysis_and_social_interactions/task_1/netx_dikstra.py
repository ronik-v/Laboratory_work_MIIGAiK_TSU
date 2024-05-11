import networkx as nx
import heapq

__author__ = "Андроник Вадим 1 курс исит 4-см"


def dijkstra_algorithm(graph: nx.Graph, start_node: int) -> tuple[dict[int, int], dict[int, list[int]]]:
    """
    implementation of Dijkstra algorithm to find shortest paths in a graph

    :param graph: NetworkX graph
    :param start_node: starting node
    :return: a dictionary containing shortest paths to each node
    """
    if not isinstance(graph, nx.Graph):
        raise TypeError(f"The type of variable graph should be nx.Graph, not {type(graph)}")
    if not isinstance(start_node, int):
        raise TypeError(f"The type of variable start_node should be int, not {type(start_node)}")
    
    distances = {node: float("inf") for node in graph.nodes}
    shortest_paths = {node: [] for node in graph.nodes}
    distances[start_node] = 0
    priority_queue = [(0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Check all adjacent nodes
        for neighbor in graph.neighbors(current_node):
            # Calculate the distance to the adjacent node through the current node
            distance = current_distance + graph[current_node][neighbor]["weight"]

            if distance < distances[neighbor]:
                # Update the distance to the adjacent node
                distances[neighbor] = distance
                # Update the shortest path to the adjacent node
                shortest_paths[neighbor] = shortest_paths[current_node] + [neighbor]
                # Add the adjacent node to the priority queue
                heapq.heappush(priority_queue, (distance, neighbor))
    return distances, shortest_paths


if __name__ == "__main__":
    graph = nx.Graph()
    graph.add_nodes_from(range(1, 6))
    edges = [(1, 2, 5), (1, 3, 3), (2, 3, 2), (2, 4, 6), (3, 4, 7), (3, 5, 4), (4, 5, 1)]
    graph.add_weighted_edges_from(edges)

    start_node = 1
    distances, shortest_paths = dijkstra_algorithm(graph, start_node)

    print(f"Shortest distances to each node - {distances}")
    print(f"Shortest paths to each node - {shortest_paths}")
