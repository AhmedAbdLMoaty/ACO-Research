import numpy as np
from config import iterations, num_ants, alpha, beta, rho, q, evaporation_rate
import sys

class MMAS_ACO:
    def __init__(self, filename):
        self.filename = filename
        self.graph = self.load_graph()
        self.search_tsp_info()

    def search_tsp_info(self):
        with open(self.filename, 'r') as file:
            for line in file:
                line = line.strip()
                line_lower = line.lower()  # Convert to lowercase for case-insensitive matching
                if line_lower.startswith(("name :", "comment :", "dimension :")):
                    line_parts = line.split(":")
                    if len(line_parts) > 1:
                        print(f"{line_parts[0].strip()} : {line_parts[1].strip()}")
                    else:
                        print(line)
                elif line_lower.startswith(("name:", "comment:", "dimension:")):
                    line_parts = line.split(":")
                    if len(line_parts) > 1:
                        print(f"{line_parts[0].strip()} : {line_parts[1].strip()}")
                    else:
                        print(line)

    def load_graph(self):
        # Load the benchmark data from the file
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        try:
            start_index = lines.index("NODE_COORD_SECTION\n")
        except ValueError:
            raise ValueError("Missing 'NODE_COORD_SECTION' marker in the file.")

        lines = lines[start_index + 1:]

        num_nodes = 0
        node_coords = {}
        for line in lines:
            if not line.strip():  # Check for empty line
                break
            parts = line.split()
            if len(parts) < 3:  # Skip lines without coordinates
                continue
            node_index = int(parts[0]) - 1  # Adjust for 0-based indexing
            x_coord = float(parts[1])
            y_coord = float(parts[2])
            node_coords[node_index] = (x_coord, y_coord)
            num_nodes += 1

        graph = np.zeros((num_nodes, num_nodes))
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:
                    x1, y1 = node_coords[i]
                    x2, y2 = node_coords[j]
                    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                    graph[i][j] = distance
                    graph[j][i] = distance  # Assuming symmetric TSP

        return graph


    def max_min_ant_system(self, num_ants=num_ants, max_iterations=iterations, evaporation_rate=evaporation_rate, alpha=alpha, beta=beta):
        num_nodes = len(self.graph)
        pheromones = np.ones((num_nodes, num_nodes))  # Initial pheromone levels
        min_pheromone = 1.0
        max_pheromone = 1.0 / (num_nodes * np.mean(self.graph))

        best_tour = None
        best_distance = float('inf')

        for iteration in range(max_iterations):
            ant_tours = []
            ant_distances = []

            for ant in range(num_ants):
                current_node = np.random.randint(num_nodes)
                visited_nodes = [current_node]
                tour_distance = 0.0

                while len(visited_nodes) < num_nodes:
                    unvisited_nodes = [node for node in range(num_nodes) if node not in visited_nodes]
                    probabilities = []
                    for next_node in unvisited_nodes:
                        distance = self.graph[current_node][next_node]
                        if distance == 0:
                            probabilities.append(0)  # Assign zero probability if distance is zero
                        else:
                            probabilities.append(((pheromones[current_node][next_node] ** alpha) * (1.0 / distance) ** beta))

                    # Check if all probabilities are zero
                    if all(p == 0 for p in probabilities):
                        selected_node = np.random.choice(unvisited_nodes)
                    else:
                        total_probability = np.sum(probabilities)
                        probabilities /= total_probability
                        selected_node = np.random.choice(unvisited_nodes, p=probabilities)


                    visited_nodes.append(selected_node)
                    tour_distance += self.graph[current_node][selected_node]
                    current_node = selected_node

                tour_distance += self.graph[visited_nodes[-1]][visited_nodes[0]]  # Return to start node
                ant_tours.append(visited_nodes)
                ant_distances.append(tour_distance)

                if tour_distance < best_distance:
                    best_tour = visited_nodes
                    best_distance = tour_distance

            # Update pheromone levels
            for i in range(num_nodes):
                for j in range(num_nodes):
                    pheromones[i][j] *= (1 - evaporation_rate)
                    pheromones[i][j] = max(min_pheromone, min(max_pheromone, pheromones[i][j]))

            for ant, tour in enumerate(ant_tours):
                for i in range(len(tour) - 1):
                    pheromones[tour[i]][tour[i + 1]] += 1.0 / ant_distances[ant]
                    pheromones[tour[i]][tour[i + 1]] = max(min_pheromone, min(max_pheromone, pheromones[tour[i]][tour[i + 1]]))
                pheromones[tour[-1]][tour[0]] += 1.0 / ant_distances[ant]
                pheromones[tour[-1]][tour[0]] = max(min_pheromone, min(max_pheromone, pheromones[tour[-1]][tour[0]]))

        return best_tour, best_distance

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pacs.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    mmas_solver = MMAS_ACO(filename)
    best_tour, best_distance = mmas_solver.max_min_ant_system()
    print("Best tour:", best_tour)
    print("Best distance:", best_distance)
