import pygame as pg
from pygame.locals import *
from sys import exit

pg.init()

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
displaySurface = pg.display.set_mode(SCREEN_SIZE)
clock = pg.Clock()

running = True
while running:
    # vars
    mouse_pos = pg.mouse.get_pos()
    dt = clock.tick() / 1000

    # input
    for event in pg.event.get():
        if event.type == QUIT:
            running = False
    
    # logic

    # rendering
    displaySurface.fill((0, 0, 0))

    pg.display.update()

pg.quit()
exit()