import pygame

sprite_sheet = None
pacman_right = []
pacman2_right = []

def load_sprite_sheet():
    global sprite_sheet
    sprite_sheet = pygame.image.load("spritesheet.png").convert()
    sprite_sheet.set_colorkey((255, 0, 255))  # Magenta transparency

    directions = ['right', 'left', 'up', 'down']
    sprites_by_direction = {}
    ghosts = {}

    def get_sprite(x, y, width, height, scale = 1.0):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        sprite.blit(sprite_sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey((255, 0, 255))

        if scale != 1.0:
            new_size = (int(width * scale), int(height * scale))
            sprite = pygame.transform.scale(sprite, new_size)

        return sprite
    
    sprites_by_direction[directions[0]] = [get_sprite(30, 0, 30, 35, scale=0.7),
                                           get_sprite(30, 1*30, 30, 35, scale=0.7),
                                           get_sprite(5*32, 0, 32, 30, scale=0.7) ]
    
    sprites_by_direction[directions[1]] = [get_sprite(0, 0, 30, 35, scale=0.7),
                                           get_sprite(0, 1*30, 30, 35, scale=0.7),
                                           get_sprite(5*32, 0, 32, 30, scale=0.7) ]

    sprites_by_direction[directions[2]] = [get_sprite(3*32, 0, 30, 35, scale=0.7),
                                           get_sprite(3*32, 1*30, 30, 35, scale=0.7),
                                           get_sprite(5*32, 0, 32, 30, scale=0.7) ]


    sprites_by_direction[directions[3]] = [get_sprite(2*32, 0, 30, 35, scale=0.7),
                                           get_sprite(2*32, 1*30, 30, 35, scale=0.7),
                                           get_sprite(5*32, 0, 32, 30, scale=0.7) ]
    
    ghosts['blinky'] = {
        directions[0] : [get_sprite(0, 5*32, 30, 35, scale = 0.7)],
        directions[1] : [get_sprite(0, 4*32, 30, 35, scale = 0.7)],
        directions[2] : [get_sprite(0, 3*33, 30, 35, scale = 0.7)],
        directions[3] : [get_sprite(0, 2*32, 30, 35, scale = 0.7)]
    }

    ghosts['inky'] = {
        directions[0] : [get_sprite(2*32, 5*32, 30, 35, scale=0.7)],
        directions[1] : [get_sprite(2*33, 4*32, 30, 35, scale = 0.7)],
        directions[2] : [get_sprite(2*32, 3*32, 30, 35, scale = 0.7)],
        directions[3] : [get_sprite(2*32, 2*32, 30, 35, scale = 0.7)]
    }

    ghosts['pinky'] = {
        directions[0] : [get_sprite(33, 5*32, 30, 35, scale=0.7)],
        directions[1] : [get_sprite(33, 4*32, 30, 35, scale = 0.7)],
        directions[2] : [get_sprite(33, 3*32, 30, 35, scale = 0.7)],
        directions[3] : [get_sprite(33, 2*32, 30, 35, scale = 0.7)]
    }

    ghosts['clyde'] = {
        directions[0] : [get_sprite(3*32, 5*32, 30, 35, scale=0.7)],
        directions[1] : [get_sprite(3*33, 4*32, 30, 35, scale = 0.7)],
        directions[2] : [get_sprite(3*32, 3*32, 30, 35, scale = 0.7)],
        directions[3] : [get_sprite(3*32, 2*32, 30, 35, scale = 0.7)]
    }

    def recolor(sprite, new_color):
        surf = sprite.copy()
        arr = pygame.PixelArray(surf)
        arr.replace((255, 255, 0), new_color)
        del arr
        return surf

    #pacman2_right = [recolor(sprite, (0, 255, 255)) for sprite in pacman_right]
    sprites_by_direction_p2 = {
        dir: [recolor(s, (0, 255, 255)) for s in sprites_by_direction[dir]]
        for dir in directions
    }

    #return pacman_right, pacman2_right
    return sprites_by_direction, sprites_by_direction_p2, ghosts
