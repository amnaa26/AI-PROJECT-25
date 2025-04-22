import random
from search_agents import GeneticGhostAI, calculate_fitness

# Maze dimensions and layout (replace with your actual maze)
ROWS, COLS = 21, 21
maze = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # Example maze

# Ghost and Pac-Man positions
ghost_pos = (10, 10)  # Replace with actual ghost position
pacman_pos = (5, 5)   # Replace with actual Pac-Man position

# Initialize GA
genetic_ai = GeneticGhostAI(population_size=50, gene_length=20)

# Train the GA
for generation in range(100):  # Number of generations
    def evaluate_fn(genes):
        return calculate_fitness(genes, ghost_pos, pacman_pos, maze)

    genetic_ai.evaluate(evaluate_fn)
    genetic_ai.evolve(mutation_rate=0.1)

    print(f"Generation {generation + 1}: Best Fitness = {genetic_ai.best.fitness}")

# Save the best path
best_path = []
current_pos = ghost_pos
for direction in genetic_ai.best.genes:
    if direction == 'up' and current_pos[1] > 0 and maze[current_pos[1] - 1][current_pos[0]] == 0:
        current_pos = (current_pos[0], current_pos[1] - 1)
    elif direction == 'down' and current_pos[1] < len(maze) - 1 and maze[current_pos[1] + 1][current_pos[0]] == 0:
        current_pos = (current_pos[0], current_pos[1] + 1)
    elif direction == 'left' and current_pos[0] > 0 and maze[current_pos[1]][current_pos[0] - 1] == 0:
        current_pos = (current_pos[0] - 1, current_pos[1])
    elif direction == 'right' and current_pos[0] < len(maze[0]) - 1 and maze[current_pos[1]][current_pos[0] + 1] == 0:
        current_pos = (current_pos[0] + 1, current_pos[1])
    best_path.append(current_pos)

# Save the trained path to a file
with open("trained_clyde_path.txt", "w") as f:
    f.write(str(best_path))