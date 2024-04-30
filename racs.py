from config import filename, iterations, num_ants, alpha, beta, rho, q
import random
import math

class City:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

class Ant:
    def __init__(self, cities):
        self.cities = cities
        self.start_city = random.choice(cities)
        self.current_city = self.start_city
        self.visited = set()
        self.visited.add(self.start_city)
        self.tour = [self.start_city]
        self.total_distance = 0.0

    def move_to_next_city(self):
        next_city = random.choice(list(set(self.cities) - self.visited))
        return next_city

    def make_tour(self):
        while len(self.visited) < len(self.cities):
            next_city = self.move_to_next_city()
            self.visited.add(next_city)
            self.tour.append(next_city)
            self.total_distance += self.current_city.distance(next_city)
            self.current_city = next_city
        self.tour.append(self.start_city)
        self.total_distance += self.current_city.distance(self.start_city)


class RACS:
    def __init__(self, cities, num_ants, alpha, beta, rho, q):
        self.cities = cities
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.pheromone = [[1.0 for _ in range(len(cities))] for _ in range(len(cities))]

    def update_pheromone(self, tours):
        pass

    def run(self, iterations):
        best_tour = None
        best_distance = float('inf')

        for _ in range(iterations):
            ants = [Ant(self.cities) for _ in range(self.num_ants)]
            for ant in ants:
                ant.make_tour()

            ants.sort(key=lambda x: x.total_distance)
            elite_ants = ants[:int(self.q * self.num_ants)]
            
            if elite_ants:
                current_best_tour = min(elite_ants, key=lambda x: x.total_distance).tour
                current_best_distance = min(elite_ants, key=lambda x: x.total_distance).total_distance

                if current_best_distance < best_distance:
                    best_tour = current_best_tour
                    best_distance = current_best_distance

            self.update_pheromone([ant.tour for ant in elite_ants])

        if best_tour is None:
            raise ValueError("No elite ants found during the optimization process.")

        return best_tour, best_distance

def parse_tsp_file(filename):
    cities = []
    dimension = None
    with open(filename, 'r') as file:
        lines = file.readlines()
        section_found = False
        for line in lines:
            if line.startswith('NODE_COORD_SECTION'):
                section_found = True
                break
            elif line.startswith('COMMENT :'):
                print(f"COMMENT : {line.strip().split(':')[1].strip()}")
            elif line.startswith('NAME :'):
                print(f"NAME : {line.strip().split(':')[1].strip()}")
            elif line.startswith('DIMENSION :'):
                dimension = int(line.strip().split(':')[1].strip())
                print(f"DIMENSION : {dimension}")

        if not section_found:
            raise ValueError("NODE_COORD_SECTION not found in the TSP file.")

        for line in lines:
            if line.strip() == 'EOF':
                break
            city_info = line.split()
            if len(city_info) != 3:
                continue
            try:
                city_id = int(city_info[0])
                x_coord = float(city_info[1])
                y_coord = float(city_info[2])
                cities.append(City(city_id, x_coord, y_coord))
            except ValueError:
                continue
        if dimension is not None and len(cities) != dimension:
            print(f"Warning: Number of cities ({len(cities)}) does not match dimension ({dimension})")
    return cities


def run_racs_from_file(cities, iterations, num_ants, alpha, beta, rho, q):
    racs = RACS(cities, num_ants, alpha, beta, rho, q)
    best_tour, best_distance = racs.run(iterations)
    return best_tour, best_distance

cities = parse_tsp_file(filename)
best_tour, best_distance = run_racs_from_file(cities, iterations, num_ants, alpha, beta, rho, q)
best_tour_ids = [city.id for city in best_tour]
print(f"Best tour: {best_tour_ids}")
print(f"Best distance: {best_distance}")
