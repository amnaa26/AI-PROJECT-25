import pygame
import random
from player import Player
from ghosts2 import Ghost  # Updated import to match the new ghosts.py file
from gate import Gate
from collections import deque

# Cage settings
CAGE_COLOR = (0, 200, 255)  # Light blue for boundaries
GATE_COLOR = (255, 255, 255)
CAGE_RECT = pygame.Rect(180, 220, 160, 100)  # x, y, width, height
GATE_Y = CAGE_RECT.y + CAGE_RECT.height - 2
GATE_HIT_LIMIT = 4
gate_hits = 0
gate_broken = False
gate_disturb_timer = 0
ghosts_escaped = 0
consumed_pellets = set()


TELEPORTERS = {  # Define teleporter pairs (x1, y1): (x2, y2)
    (2, 2): (18, 18),
    (18, 2): (2, 18)
}

def handle_teleporters(entity):
    for (x1, y1), (x2, y2) in TELEPORTERS.items():
        if entity.x == x1 and entity.y == y1:
            entity.x, entity.y = x2, y2
        elif entity.x == x2 and entity.y == y2:
            entity.x, entity.y = x1, y1


def draw_scoreboard(surface, score, pellets_left, escaped_ghosts):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    pellets_text = font.render(f"Pellets Left: {len(pellets_left)}", True, (255, 255, 255))
    ghosts_text = font.render(f"Escaped Ghosts: {escaped_ghosts}", True, (255, 255, 255))
    surface.blit(score_text, (10, 10))
    surface.blit(pellets_text, (10, 50))
    surface.blit(ghosts_text, (10, 90))

def reserve_ghost_box():
    # Calculating the center of the maze to place the ghost cage
    mid_r, mid_c = ROWS // 2, COLS // 2
    for r in range(mid_r - 1, mid_r + 2):
        for c in range(mid_c - 2, mid_c + 3):
            maze[r][c] = 0  # Make it a path (not wall)

def draw_ghost_cage():
    # Coordinates
    mid_r, mid_c = ROWS // 2, COLS // 2
    top = (mid_r - 1) * TILE
    bottom = (mid_r + 2) * TILE
    left = (mid_c - 2) * TILE
    right = (mid_c + 3) * TILE

    
    # Mark cage walls as impassable (maze[y][x] = 2 for walls)
    for r in range(mid_r - 1, mid_r + 3):  # Top and Bottom walls
        maze[r][mid_c - 2] = 2  # Left wall
        maze[r][mid_c + 3] = 2  # Right wall
    for c in range(mid_c - 2, mid_c + 4):  # Left and Right walls
        maze[mid_r - 1][c] = 2  # Top wall
        maze[mid_r + 2][c] = 2  # Bottom wall
    

    # Cage boundaries (visual representation)
    pygame.draw.line(win, CAGE_COLOR, (left, top), (right, top), 2)    # Top
    pygame.draw.line(win, CAGE_COLOR, (left, bottom), (right, bottom), 2)  # Bottom
    pygame.draw.line(win, CAGE_COLOR, (left, top), (left, bottom), 2)   # Left
    pygame.draw.line(win, CAGE_COLOR, (right, top), (right, bottom), 2) # Right

    # Draw gate only if not broken and tile is a path
    gate_tile_r, gate_tile_c = GATE_TILE
    if maze[gate_tile_r][gate_tile_c] == 0:  # Gate is walkable
        gate_x = gate_tile_c * TILE
        gate_y = gate_tile_r * TILE
        flicker_color = GATE_COLOR
        pygame.draw.line(win, flicker_color, (gate_x, gate_y), (gate_x + TILE, gate_y), 2)

def remove_dead_ends(iterations=30):
    for _ in range(iterations):
        for r in range(1, ROWS-1):
            for c in range(1, COLS-1):
                if maze[r][c] == 0:
                    neighbors = [(r+1, c), (r-1, c), (r, c+1), (r, c-1)]
                    walls = [maze[nr][nc] for nr, nc in neighbors]
                    if walls.count(1) == 3:  # It's a dead end
                        random.shuffle(neighbors)
                        for nr, nc in neighbors:
                            if maze[nr][nc] == 1:
                                maze[nr][nc] = 0
                                break


def generate_maze(r, c):
    maze[r][c] = 0
    dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
    random.shuffle(dirs)

    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 1:
            maze[r + dr // 2][c + dc // 2] = 0
            generate_maze(nr, nc)



def regenerate_maze():
    mid_r, mid_c = ROWS // 2, COLS // 2
    global maze, pellets
    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    generate_maze(1, 1)
    reserve_ghost_box()
    remove_dead_ends(50)

    '''
    # Preserve cage walls
    for r in range(mid_r - 1, mid_r + 3):
        maze[r][mid_c - 2] = 2  # Left wall
        maze[r][mid_c + 3] = 2  # Right wall
    for c in range(mid_c - 2, mid_c + 4):
        maze[mid_r - 1][c] = 2  # Top wall
        maze[mid_r + 2][c] = 2  # Bottom wall
    '''
        
    pellets = set((r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == 0)
    pellets -= consumed_pellets
    for r, c in CAGE_TILES:
        pellets.discard((r, c))
    pellets.discard(GATE_TILE)


def find_nearest_valid_position(maze, start_x, start_y):
    """Find the nearest valid position in the maze."""
    queue = deque([(start_x, start_y)])
    visited = set([(start_x, start_y)])

    while queue:
        x, y = queue.popleft()

        # Check if the current tile is walkable
        if maze[y][x] == 0:
            return (x, y)

        # Explore neighboring tiles
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))

    # Fallback: If no valid position is found, return the start position
    return (start_x, start_y)



def draw_pellets():
    for r, c in pellets:
        pygame.draw.circle(win, (255, 255, 255), (c * TILE + TILE // 2, r * TILE + TILE // 2), 3)

# Main function:
ROWS, COLS = 21, 21  # Must be odd to have walls surrounding paths
TILE = 25
WIDTH, HEIGHT = COLS * TILE, ROWS * TILE
CAGE_MID_ROW = ROWS // 2
CAGE_MID_COL = COLS // 2
CAGE_WIDTH = 5
CAGE_HEIGHT = 3
CAGE_TILES = [
    (r, c)
    for r in range(CAGE_MID_ROW - 1, CAGE_MID_ROW + 2)
    for c in range(CAGE_MID_COL - 2, CAGE_MID_COL + 3)
]


FOG_COLOR = (0, 0, 0, 150)  # Semi-transparent black
VISION_RADIUS = 5 * TILE  # Radius of visible area

def draw_fog_of_vision():
    fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fog_surface.fill(FOG_COLOR)

    # Clear a circle around Player 1
    pygame.draw.circle(fog_surface, (0, 0, 0, 0), (player1.x * TILE + TILE // 2, player1.y * TILE + TILE // 2), VISION_RADIUS)

    # Clear a circle around Player 2
    pygame.draw.circle(fog_surface, (0, 0, 0, 0), (player2.x * TILE + TILE // 2, player2.y * TILE + TILE // 2), VISION_RADIUS)

    win.blit(fog_surface, (0, 0))

gate_tile_x = WIDTH // 2
gate_tile_y = HEIGHT // 2 + 2  # Example
#gate = Gate(gate_tile_x, gate_tile_y, TILE)
# Create a pygame.Rect object for the gate's position and size
gate_rect = pygame.Rect(gate_tile_x, gate_tile_y, TILE, TILE)


import pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
from sprite import load_sprite_sheet
pacman_right, pacman2_right, ghost_frames = load_sprite_sheet()

# Initialize all walls
maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]


# Start maze generation from (1, 1)
generate_maze(1, 1)
reserve_ghost_box()
remove_dead_ends(50)  # You can tweak the number for more/less loops

gate = Gate(gate_rect, win, maze, TILE)
GATE_TILE = (CAGE_MID_ROW + 2, CAGE_MID_COL)
maze[GATE_TILE[0]][GATE_TILE[1]] = 0  # Make sure it's path

# Initialize pellets
pellets = set((r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == 0)
# Exclude ghost cage and gate tiles
for r, c in CAGE_TILES:
    pellets.discard((r, c))
pellets.discard(GATE_TILE)

# Players
player1 = Player(1, 1, pacman_right, maze, TILE, {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT
}, pellets)

player2 = Player(COLS - 2, ROWS - 2, pacman2_right, maze, TILE, {
    'up': pygame.K_w,
    'down': pygame.K_s,
    'left': pygame.K_a,
    'right': pygame.K_d
}, pellets)

cage_barrier_broken = {
    "broken": False,
    "hits": 0,
    "escaped_count": 0,
    "escape_cooldown": 0  # frames before next ghost escapes
}


# Initialize ghosts with updated Ghost class
ghosts = [
    Ghost(2, COLS // 2 , ROWS // 2, ghost_frames['blinky'], TILE, maze, gate),  # Updated to use the new Ghost class
    Ghost(4, COLS // 2-1, ROWS // 2, ghost_frames['inky'], TILE, maze, gate),
    Ghost(1, COLS // 2+1, ROWS // 2, ghost_frames['pinky'], TILE, maze, gate),
    Ghost(3, int(COLS // 2-1.7), int(ROWS // 2-0.75) , ghost_frames['clyde'], TILE, maze, gate)
]


center_x = len(maze[0]) // 2
center_y = len(maze) // 2 + 1  # One row below cage center

# Define gate rectangle (adjust width/height if needed)
gate_rect = pygame.Rect(center_x * TILE, center_y * TILE, TILE, TILE)
for ghost in ghosts:
        ghost.gate_rect = gate_rect  # Set this to the correct Rect


def draw():
    #draw the maze
    for y in range(ROWS):
        for x in range(COLS):
            color = (0, 0, 255) if maze[y][x] == 1 else (0, 0, 0)
            pygame.draw.rect(win, color, (x*TILE, y*TILE, TILE, TILE))


    # Draw pellets
    draw_pellets()

    draw_ghost_cage()
    player1.draw(win)
    player2.draw(win)
    for ghost in ghosts:
        ghost.draw(win)



run = True
print("Clyde tile:", COLS // 2, ROWS // 2 - 1)
print("Maze tile at Clyde position:", maze[ROWS // 2 - 1][COLS // 2])

while run:
    pygame.time.delay(100)
    keys = pygame.key.get_pressed()

    if not pygame.key.get_focused():
        continue

    # Store player and ghost positions
    stored_player1_pos = (player1.x, player1.y)
    stored_player2_pos = (player2.x, player2.y)
    stored_ghost_positions = [(ghost.x, ghost.y) for ghost in ghosts]

    if pygame.time.get_ticks() % 30000 < 1000:  # Regenerate every 30 seconds
        regenerate_maze()
        # Players
        player1 = Player(1, 1, pacman_right, maze, TILE, {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT
        }, pellets)

        player2 = Player(COLS - 2, ROWS - 2, pacman2_right, maze, TILE, {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d
        }, pellets)

        # Reposition players
        player1.x, player1.y = find_nearest_valid_position(maze, *stored_player1_pos)
        player2.x, player2.y = find_nearest_valid_position(maze, *stored_player2_pos)

        # Reposition ghosts
        for i, ghost in enumerate(ghosts):
            ghost.x, ghost.y = find_nearest_valid_position(maze, *stored_ghost_positions[i])


        draw_scoreboard(win, player1.score, pellets, gate.ghosts_escaped)
    # Inside the main game loop
    #draw_fog_of_vision()

    

    # Inside the main game loop
    handle_teleporters(player1)
    handle_teleporters(player2)
    for ghost in ghosts:
        handle_teleporters(ghost)

    player1.move(keys, (player2.x, player2.y))
    player2.move(keys, (player1.x, player1.y))

    player1.update()
    player2.update()

    player1.eat_pellet(consumed_pellets)
    player2.eat_pellet(consumed_pellets)

    # Add the pacman_positions argument when calling update
    for ghost in ghosts:
        pacman_positions = [(player1.x, player1.y), (player2.x, player2.y)]
        ghost.update(ghosts, pacman_positions)
       # ghost.draw(win)


    gate.update_gate_visuals()

   # gate.draw(win)

    win.fill((0, 0, 0))
    draw()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

pygame.quit()

