import pygame
import random
from search_agents import bfs, astar, minimax_choose_move

class Ghost:
    def __init__(self, id, x, y, frames, tile_size, maze, gate):
        self.id = id
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.frames = frames  # Dictionary of sprite lists for each direction
        self.rect = pygame.Rect(self.x * tile_size, self.y * tile_size, tile_size, tile_size)
        self.maze = maze
        self.gate = gate

        self.has_escaped = False
        self.bump_count = 0
        self.speed = 2
        self.direction_name = 'down'
        self.current_frame = 0
        self.frame_counter = 0
        self.last_pos = None
        self.bumped_this_frame = False

        # Load pre-trained path for Clyde
        if self.id == 4:
            try:
                with open("trained_clyde_path.txt", "r") as f:
                    self.trained_path = eval(f.read())
            except FileNotFoundError:
                print("Trained path not found. Using random movement.")
                self.trained_path = []

    def tile_position(self):
        """Return the current tile position of the ghost."""
        return (self.rect.x // self.tile_size, self.rect.y // self.tile_size)

    def draw(self, surface):
        """Draw the ghost's sprite on the screen."""
        sprite = self.frames[self.direction_name][self.current_frame]
        sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
        surface.blit(sprite, self.rect.topleft)

    def is_walkable(self, x, y):
        """Check if a tile is walkable."""
        if self.maze[y][x] == 1:
            return False

        # If ghost hasn't escaped, only allow movement near the gate
        if not self.has_escaped:
            gate_tile = (self.gate.gate_rect.centerx // self.tile_size,
                         self.gate.gate_rect.centery // self.tile_size)
            distance_to_gate = pygame.Vector2(x, y).distance_to(gate_tile)
            return distance_to_gate < 2  # Only allow movement near gate

        return True  # Free movement after escape

    def update(self, ghosts, pacman_positions):
        """Update the ghost's behavior based on its ID."""
        gate_center = self.gate.gate_rect.center
        gate_tile = (gate_center[0] // self.tile_size, gate_center[1] // self.tile_size)

        self.bumped_this_frame = False

        if not self.has_escaped:
            # If gate is broken, head straight to the gate tile
            if self.gate.broken:
                path_to_gate = bfs(self.tile_position(), gate_tile, self.maze)
                if path_to_gate:
                    self.move_along_path(path_to_gate)

                # Check if reached gate tile to mark as escaped
                if self.tile_position() == gate_tile:
                    self.has_escaped = True
                    print(f"Ghost {self.id} escaped through the gate!")
            else:
                # Normal behavior when gate is intact
                path_to_gate = bfs(self.tile_position(), gate_tile, self.maze)
                if path_to_gate:
                    self.move_along_path(path_to_gate)

                # Attack the gate if reached
                gate_hitbox = self.gate.gate_rect.inflate(6, 6)
                if gate_hitbox.collidepoint(self.rect.center) and self.tile_position() == gate_tile:
                    if not self.bumped_this_frame:
                        self.bump_count += 1
                        self.gate.hit()
                        self.gate.flicker_timer = 10
                        self.bumped_this_frame = True
                        print(f"Ghost {self.id} attacked the gate! Hit {self.bump_count}/2")

        # After escape behavior
        if self.has_escaped:
            if self.id == 1:  # Pinky - BFS to player1
                path = bfs(self.tile_position(), pacman_positions[0], self.maze)
                print(f"Pinky BFS Path: {path}")
                if path:
                    self.move_along_path(path)
            elif self.id == 2:  # Blinky - A* to player2
                path = astar(self.tile_position(), pacman_positions[1], self.maze)
                if path:
                    self.move_along_path(path)
            elif self.id == 3:  # Clyde - Minimax
                best_move = minimax_choose_move(self.tile_position(), pacman_positions[0], self.maze)
                print(f"Clyde Minimax Move: {best_move}")
                self.rect.x, self.rect.y = best_move[0] * self.tile_size, best_move[1] * self.tile_size
            elif self.id == 4:  # Inky - Use pre-trained path or fallback to random movement
                if self.trained_path:
                    self.move_along_path(self.trained_path)
                else:
                    pos = self.random_move(self.tile_position())
                    self.rect.x, self.rect.y = pos[0] * self.tile_size, pos[1] * self.tile_size

            # Prevent re-entering cage
            if self.gate.cage_rect.collidepoint(self.rect.center):
                self.rect.y -= self.tile_size

        # Update animation frame
        self.frame_counter += 1
        if self.frame_counter >= 5:  # Change frame every 5 updates
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction_name])

    def move_along_path(self, path):
        if not path:
            return

        next_tile = path[0]  # Take the first step
        target_x = next_tile[0] * self.tile_size
        target_y = next_tile[1] * self.tile_size

        # Ensure the next tile is walkable
        if self.maze[next_tile[1]][next_tile[0]] != 0:
            print(f"Invalid move detected at {next_tile}. Stopping movement.")
            return

        dx = target_x - self.rect.x
        dy = target_y - self.rect.y

        # Pick animation direction
        if abs(dx) > abs(dy):
            self.direction_name = 'right' if dx > 0 else 'left'
        else:
            self.direction_name = 'down' if dy > 0 else 'up'

        v = pygame.Vector2(dx, dy)
        if v.length() > 0:
            v = v.normalize()
            self.rect.x += v.x * self.speed
            self.rect.y += v.y * self.speed

        # Snap to tile-center if close
        if abs(self.rect.x - target_x) < self.speed:
            self.rect.x = target_x
        if abs(self.rect.y - target_y) < self.speed:
            self.rect.y = target_y

    def random_move(self, pos):
        """Perform random movement for Clyde if no valid path is available."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        valid_moves = []
        for dx, dy in directions:
            nx, ny = pos[0] + dx, pos[1] + dy
            if 0 <= nx < len(self.maze[0]) and 0 <= ny < len(self.maze) and self.maze[ny][nx] == 0:
                valid_moves.append((nx, ny))
        return random.choice(valid_moves) if valid_moves else pos