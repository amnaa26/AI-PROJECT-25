import pygame
import random

class Gate:
    def __init__(self, gate_rect, screen, maze, tile_size):
        self.gate_rect = gate_rect
        self.hit_count = 0
        self.broken = False
        self.ghosts_escaped = 0
        self.screen = screen
        self.maze = maze
        self.tile_size = tile_size
        self.flicker_timer = 0
        self.flicker_color = (255, 255, 255)  # Default color: white
        self.cage_rect = pygame.Rect(180, 220, 160, 100)

    def hit(self):
        """Handle a ghost hitting the gate."""
        if self.broken:
            return  # No effect if the gate is already broken

        self.hit_count += 1
        print(f"Gate hit {self.hit_count} times!")

        if self.hit_count >= 2:
            self.break_gate()
        else:
            self.start_flicker()

    def break_gate(self):
        self.broken = True
        gate_tile_x = self.gate_rect.centerx // self.tile_size
        gate_tile_y = self.gate_rect.centery // self.tile_size
        self.maze[gate_tile_y][gate_tile_x] = 0  # Make tile walkable

    def start_flicker(self):
        """Start the flickering effect."""
        self.flicker_timer = 50  # Flicker for 50 frames
        self.flicker_color = (255, 0, 0)  # Start with red

    def update_gate_visuals(self):
        """Update the visual representation of the gate."""
        if self.broken:
            return  # Don't draw anything if the gate is broken

        # Update flicker timer and color
        if self.flicker_timer > 0:
            self.flicker_timer -= 1
            if self.flicker_timer % 10 == 0:  # Change color every 10 frames
                self.flicker_color = (255, 0, 0) if self.flicker_color == (255, 255, 255) else (255, 255, 255)
        else:
            self.flicker_color = (255, 255, 255)  # Default to white after flicker ends

        # Draw the gate line
        pygame.draw.line(self.screen, self.flicker_color,
                         (self.gate_rect.left, self.gate_rect.top),
                         (self.gate_rect.right, self.gate_rect.top),
                         5)

    def allow_ghost_escape(self):
        """Allow a ghost to escape after the gate is broken."""
        if self.broken:
            self.ghosts_escaped += 1
            print(f"Ghost escaped! Total escaped: {self.ghosts_escaped}")