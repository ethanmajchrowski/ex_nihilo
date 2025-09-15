from infrastructure.input_manager import input_manager
import pygame as pg

class Camera:
    def __init__(self, screen_size, position=(0, 0), zoom=1.0):
        self.position = list(position)
        self.screen_width, self.screen_height = screen_size
        self.zoom = zoom
    
        # self.min_zoom = 0.25
        # self.max_zoom = 4.0

    def move(self, dx, dy):
        self.position[0] += dx / self.zoom
        self.position[1] += dy / self.zoom
    
    def get_offset(self):
        return -self.position[0], -self.position[1]

    def set_pos(self, x, y):
        self.position = [x, y]

    def world_to_screen(self, world_pos):
        return (
            (world_pos[0] - self.position[0]) * self.zoom,
            (world_pos[1] - self.position[1]) * self.zoom
        )

    def screen_to_world(self, screen_pos):
        return (
            screen_pos[0] / self.zoom + self.position[0],
            screen_pos[1] / self.zoom + self.position[1]
        )
    
    def update(self, dt):
        if input_manager.held_keys[pg.K_d]: self.move(500*dt, 0)
        if input_manager.held_keys[pg.K_a]: self.move(-500*dt, 0)
        if input_manager.held_keys[pg.K_w]: self.move(0, -500*dt)
        if input_manager.held_keys[pg.K_s]: self.move(0, 500*dt)
        if input_manager.held_keys[pg.K_h]: self.set_pos(0, 0)