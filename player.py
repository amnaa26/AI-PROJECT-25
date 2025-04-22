import pygame

class Player:
    def __init__(self, x, y, frames, maze, tile_size, keys, pellets):
        self.pellets = pellets
        self.x = x
        self.y = y
        self.frames = frames  # Dictionary of sprite lists for each direction
        self.tile_size = tile_size
        self.maze = maze
        self.keys = keys  # Dictionary of movement keys
        self.frame_index = 0
        self.frame_delay = 5
        self.frame_timer = 0
        self.current_frame = 0
        self.direction = 'right'
        self.score = 0  # Score tracking
        self.alive = True  # Player state: alive or dead
        self.power_up = False  # Power-up state for killing ghosts
        self.power_up_timer = 0  # Timer for power-up duration

    def move(self, keys_pressed, other_player_pos):
        dx, dy = 0, 0
        if keys_pressed[self.keys['up']]:
            dy = -1
            self.direction = 'up'
        elif keys_pressed[self.keys['down']]:
            dy = 1
            self.direction = 'down'
        elif keys_pressed[self.keys['left']]:
            dx = -1
            self.direction = 'left'
        elif keys_pressed[self.keys['right']]:
            dx = 1
            self.direction = 'right'

        new_x = self.x + dx
        new_y = self.y + dy

        # Ensure the new position is valid
        if 0 <= new_y < len(self.maze) and 0 <= new_x < len(self.maze[0]) and (new_x, new_y) != other_player_pos:
            if self.maze[new_y][new_x] == 0:  # Path, not a wall
                self.x = new_x
                self.y = new_y

    '''
    def eat_pellet(self, pellets):
        """Check if the player is on a pellet and consume it."""
        if (self.y, self.x) in pellets:
            pellets.remove((self.y, self.x))
            self.score += 10  # Add points for eating a pellet
            self.frame_delay = 3  # Speed up animation temporarily
            pygame.time.set_timer(pygame.USEREVENT, 500)  # Reset animation speed after 500ms
    '''

    def eat_pellet(self, consumed_pellets):
        """Check if the player is on a pellet and consume it."""
        if (self.y, self.x) in self.pellets:
            self.pellets.remove((self.y, self.x))
            consumed_pellets.add((self.y, self.x))  # Track consumed pellets
            self.score += 10
            self.frame_delay = 3  # Speed up animation temporarily
            pygame.time.set_timer(pygame.USEREVENT, 500)  # Reset animation speed after 500ms

    def kill_ghost(self, ghost):
        """Kill a ghost if the player is in power-up mode."""
        if self.power_up:
            ghost.alive = False  # Kill the ghost
            self.score += 50  # Add points for killing a ghost

    def be_killed(self):
        """Handle the player being killed by a ghost."""
        self.alive = False
        self.frame_timer = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # Respawn after 2 seconds

    def update(self):
        """Update the player's animation and power-up state."""
        if not self.alive:
            return  # Do not update if the player is dead

        # Update animation frame
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])

        # Update power-up timer
        if self.power_up:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.power_up = False  # End power-up state

    def draw(self, surface):
        """Draw the player's sprite on the screen."""
        if not self.frames:
            return

        # Handle flashing effect when being killed
        if not self.alive:
            if self.frame_timer % 2 == 0:  # Flash every other frame
                return

        # Get the current sprite
        sprite = self.frames[self.direction][self.current_frame]
        if sprite.get_size() != (self.tile_size, self.tile_size):
            sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))

        offset = (self.tile_size - sprite.get_width()) // 2

        # Draw the sprite
        surface.blit(sprite, (self.x * self.tile_size + offset, self.y * self.tile_size + offset))

        # Highlight the player during power-up
        if self.power_up:
            pygame.draw.circle(surface, (255, 0, 0), (self.x * self.tile_size + self.tile_size // 2,
                                                       self.y * self.tile_size + self.tile_size // 2),
                               self.tile_size // 2, 2)