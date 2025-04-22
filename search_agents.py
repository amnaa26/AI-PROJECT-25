from collections import deque
import heapq
import random

# --- BFS Algorithm ---
def bfs(start, goal, maze):
    queue = deque([(start, [])])
    visited = set([start])
    
    while queue:
        (x, y), path = queue.popleft()
        
        if (x, y) == goal:
            return path
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))
    
    return []

# --- A* Algorithm ---
class Node:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def astar(start, goal, maze):
    open_list = []
    closed_set = set()

    start_node = Node(*start)
    goal_node = Node(*goal)
    heapq.heappush(open_list, start_node)

    while open_list:
        current = heapq.heappop(open_list)
        if (current.x, current.y) == (goal_node.x, goal_node.y):
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        closed_set.add((current.x, current.y))

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = current.x + dx, current.y + dy
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0 and (nx, ny) not in closed_set:
                neighbor = Node(nx, ny, current)
                neighbor.g = current.g + 1
                neighbor.h = abs(goal_node.x - nx) + abs(goal_node.y - ny)
                neighbor.f = neighbor.g + neighbor.h
                heapq.heappush(open_list, neighbor)

    return []

# --- Minimax Ghost Logic ---
def minimax_get_possible_moves(pos, maze):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    moves = []
    for dx, dy in directions:
        nx, ny = pos[0] + dx, pos[1] + dy
        if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] == 0:
            moves.append((nx, ny))
    return moves

def minimax_evaluate(ghost_pos, pacman_pos):
    # Evaluate based on Manhattan distance
    return -(abs(ghost_pos[0] - pacman_pos[0]) + abs(ghost_pos[1] - pacman_pos[1]))

def minimax_search(ghost_pos, pacman_pos, maze, depth, alpha, beta, maximizing):
    if depth == 0:
        return minimax_evaluate(ghost_pos, pacman_pos)

    if maximizing:
        max_eval = -float('inf')
        for move in minimax_get_possible_moves(ghost_pos, maze):
            eval = minimax_search(move, pacman_pos, maze, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in minimax_get_possible_moves(pacman_pos, maze):
            eval = minimax_search(ghost_pos, move, maze, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def minimax_choose_move(current_pos, pacman_pos, maze, depth=2):
    best_score = -float('inf')
    best_move = current_pos
    for move in minimax_get_possible_moves(current_pos, maze):
        score = minimax_search(move, pacman_pos, maze, depth - 1, -float('inf'), float('inf'), False)
        if score > best_score:
            best_score = score
            best_move = move
    return best_move

# --- Genetic Algorithm for Inky ---
DIRECTIONS = ['up', 'down', 'left', 'right']

class GhostDNA:
    def __init__(self, gene_length=10):
        self.genes = [random.choice(DIRECTIONS) for _ in range(gene_length)]
        self.fitness = 0

    def crossover(self, partner):
        child = GhostDNA(len(self.genes))
        midpoint = random.randint(0, len(self.genes) - 1)
        child.genes = self.genes[:midpoint] + partner.genes[midpoint:]
        return child

    def mutate(self, mutation_rate=0.1):
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                self.genes[i] = random.choice(DIRECTIONS)

class GeneticGhostAI:
    def __init__(self, population_size=20, gene_length=10):
        self.population = [GhostDNA(gene_length) for _ in range(population_size)]
        self.generation = 0
        self.best = None

    def evaluate(self, evaluate_fn):
        for dna in self.population:
            dna.fitness = evaluate_fn(dna.genes)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self.best = self.population[0]

    def evolve(self, mutation_rate=0.1):
        new_population = [self.best]  # Keep the best one
        while len(new_population) < len(self.population):
            parent1 = self.select()
            parent2 = self.select()
            child = parent1.crossover(parent2)
            child.mutate(mutation_rate)
            new_population.append(child)
        self.population = new_population
        self.generation += 1

    def select(self):
        total_fitness = sum(dna.fitness for dna in self.population)
        if total_fitness == 0:
            return random.choice(self.population)
        pick = random.uniform(0, total_fitness)
        current = 0
        for dna in self.population:
            current += dna.fitness
            if current > pick:
                return dna

# Fitness function for Inky
def calculate_fitness(path, ghost_pos, pacman_pos, maze):
    score = 0
    x, y = ghost_pos
    for direction in path:
        if direction == 'up' and y > 0 and maze[y - 1][x] == 0:
            y -= 1
        elif direction == 'down' and y < len(maze) - 1 and maze[y + 1][x] == 0:
            y += 1
        elif direction == 'left' and x > 0 and maze[y][x - 1] == 0:
            x -= 1
        elif direction == 'right' and x < len(maze[0]) - 1 and maze[y][x + 1] == 0:
            x += 1
        # Reward approaching Pac-Man
        distance = abs(x - pacman_pos[0]) + abs(y - pacman_pos[1])
        score += 1 / (distance + 1)
    return score