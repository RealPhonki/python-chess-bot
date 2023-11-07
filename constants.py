import pygame as pg

# customization
color_themes = {
    "Default": [(238,238,210), (118,150,86)],
    "Sand":    [(227,193,111), (184,139,74)],
    "Dark":    [(157,172,255), (111,115,210)]
}

COLOR1, COLOR2 = color_themes["Sand"]
SELECT_HIGHLIGHT = (255, 255, 255)
LAST_MOVE_HIGHLIGHT = (255, 255, 0)

HIGHLIGHT_THICKNESS = 3

# window stuff
RES = WIDTH, HEIGHT = (640, 640)
FPS = 20

# chess board stuff
TILESIZE = 80

# sprites
pieces = [pg.transform.smoothscale(pg.image.load(f"assets/pieces/{i}.png"), (TILESIZE, TILESIZE)) for i in range(12)]
