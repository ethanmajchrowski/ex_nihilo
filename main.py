import pygame as pg
from pygame.locals import *
from sys import exit
from math import dist

pg.init()
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
displaySurface = pg.display.set_mode(SCREEN_SIZE)

import module.node as Node

clock = pg.Clock()

nodes = Node.NodeGroup()

def determine_visible_nodes(nodes: Node.NodeGroup):
    for node in nodes.sprites():
        if not node.hidden:
            continue

        node.visible = dist(mouse_pos, node.pos) < node.show_radius

running = True
while running:
    # vars
    mouse_pos = pg.mouse.get_pos()
    dt = clock.tick() / 1000

    # input
    for event in pg.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                nodes.add(Node.Empty(mouse_pos, True))
            if event.button == 3:
                nodes.add(Node.Empty(mouse_pos, False))
    
    # logic
    determine_visible_nodes(nodes)

    # rendering
    displaySurface.fill((0, 0, 0))

    nodes.draw_visible(displaySurface)

    pg.display.update()

pg.quit()
exit()