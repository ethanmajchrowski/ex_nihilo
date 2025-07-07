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

    # def zoom_at(self, focus_pos, zoom_delta):
    #     """
    #     Zoom in or out, keeping focus_pos (screen-space) locked in place.
    #     """
    #     old_zoom = self.zoom
    #     self.zoom *= zoom_delta
    #     self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

    #     # Adjust position to preserve focus point
    #     if self.zoom != old_zoom:
    #         world_before = self.screen_to_world(focus_pos)
    #         world_after = self.screen_to_world(focus_pos)
    #         self.position[0] += world_before[0] - world_after[0]
    #         self.position[1] += world_before[1] - world_after[1]
