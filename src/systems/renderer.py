import pygame as pg

import data.configuration as c
from infrastructure.asset_manager import asset_manager
from infrastructure.entity_manager import entity_manager
from infrastructure.global_inventory import global_inventory
from infrastructure.input_manager import input_manager
from infrastructure.tool_manager import tool_manager, LinkTool, PlaceTool
from infrastructure.io_registry import io_registry
from infrastructure.data_registry import data_registry
from infrastructure.utils import interpolate_color, get_footprint_center
from systems.camera import Camera


class Renderer:
    def __init__(self) -> None:
        self.debug_font = pg.font.SysFont("arial", 16)
    
    def generate_background_grid_surface(self, tile_size=256, grid_size=(2048, 2048),
                                        color1=(30, 30, 30), color2=(31, 31, 31)):
        """Stores a background surface in the asset manager under group "background" and name "grid".

        Args:
            tile_size (int, optional): Square size of background tiles. Defaults to 256.
            grid_size (tuple, optional): Size of surface. Defaults to (2048, 2048).
            color1 (tuple, optional): _color_. Defaults to (30, 30, 30).
            color2 (tuple, optional): _color_. Defaults to (31, 31, 31).
        """
        surface = pg.Surface(grid_size)
        w, h = grid_size
        for y in range(0, h, tile_size):
            for x in range(0, w, tile_size):
                rect = pg.Rect(x, y, tile_size, tile_size)
                color = color1 if ((x // tile_size + y // tile_size) % 2 == 0) else color2
                pg.draw.rect(surface, color, rect)
        asset_manager.add_asset("background", "grid", surface)

    def draw_cached_background(self, surface: pg.Surface, camera, bg_surface: pg.Surface):
        screen_w, screen_h = surface.get_size()
        offset_x, offset_y = camera.get_offset()
        bg_w, bg_h = bg_surface.get_size()

        x0 = int(offset_x) % bg_w - bg_w
        y0 = int(offset_y) % bg_h - bg_h

        for y in range(y0, screen_h, bg_h):
            for x in range(x0, screen_w, bg_w):
                surface.blit(bg_surface, (x, y))
                # pg.draw.rect(surface, (0, 0, 0), pg.Rect(x, y, bg_w, bg_h), 5)
    
    def render(self, surface: pg.Surface, mouse_pos: tuple[int, int], camera: Camera) -> None:
        offset = camera.get_offset()
        surface.fill((30, 30, 30))
        self.draw_cached_background(surface, camera, asset_manager.assets["background"]["grid"])
        
        # tile_rect = pg.Rect(camera.world_to_screen(input_manager.last_mouse_pos_snapped), (c.BASE_MACHINE_WIDTH/2, c.BASE_MACHINE_HEIGHT/2))
        # pg.draw.rect(surface, (60, 60, 60), tile_rect)
        # pg.draw.circle(surface, (255, 0, 0), camera.world_to_screen(input_manager.mouse_pos_closest_corner), 5)
        resource_nodes = entity_manager.get_resource_nodes()
        for node in resource_nodes:
            pos = camera.world_to_screen(node.position)
            # print(node.type)
            img = asset_manager.get("resource_nodes", node.type)
            surface.blit(img, pos)
        
        
        machines = entity_manager.get_machines()
        for machine in machines:
            pos = camera.world_to_screen(machine.position)
            for tile in machine.shape:
                color = (100, 100, 100)
                if input_manager.hovered_item is machine:
                    color = (140, 140, 140)
                pg.draw.rect(surface, color, pg.Rect(
                    pos[0]+tile[0] * c.BASE_MACHINE_WIDTH, pos[1]+tile[1] * c.BASE_MACHINE_HEIGHT, 
                    c.BASE_MACHINE_WIDTH, c.BASE_MACHINE_HEIGHT))
        
        for cable in entity_manager.get_power_cables():
            start_size, end_size = 2, 2
            if input_manager.mouse_pos_closest_corner == cable.start_pos: start_size += 2
            if input_manager.mouse_pos_closest_corner == cable.end_pos: end_size += 2
            
            start_size = 0 if io_registry.get_node(cable.start_pos) else start_size
            end_size = 0 if io_registry.get_node(cable.end_pos) else end_size
            
            on_color, off_color = (255, 0, 0), (100, 0, 0)
            
            color = interpolate_color(cable.grid.ticks_since_online, 0, 25, on_color, off_color)
            start, end = camera.world_to_screen(cable.start_pos), camera.world_to_screen(cable.end_pos)

            pg.draw.aaline(surface, color, start, end, 2)
            pg.draw.circle(surface, color, (start[0]+start_size//2, start[1]+start_size//2), start_size)
            pg.draw.circle(surface, color, (end[0]+end_size//2, end[1]+end_size//2), end_size)
        
        for link in entity_manager.get_transfer_links():
            start_size, end_size = 2, 2
            if input_manager.mouse_pos_closest_corner == link.start_pos: start_size += 2
            if input_manager.mouse_pos_closest_corner == link.end_pos: end_size += 2
            on_color = (241, 201, 120) if link.type == "item" else (97, 158, 249)
            start, end = camera.world_to_screen(link.start_pos), camera.world_to_screen(link.end_pos)
            color = interpolate_color(link.ticks_since_transfer, 0, 25, on_color, (150, 150, 150))

            start_size = 0 if io_registry.get_node(link.start_pos) else start_size
            end_size = 0 if io_registry.get_node(link.end_pos) else end_size

            pg.draw.aaline(surface, color, start, end, 2)
            pg.draw.circle(surface, color, (start[0]+start_size//2, start[1]+start_size//2), start_size)
            pg.draw.circle(surface, color, (end[0]+end_size//2, end[1]+end_size//2), end_size)
        
        for machine in machines:
            for node in machine.nodes:
                size = 4
                if node is input_manager.hovered_item:
                    size += 2
                pos = camera.world_to_screen(node.abs_pos)
                if node.kind == "item":
                    if node.direction == "input":
                        pg.draw.circle(surface, (0, 0, 255), pos, size)
                    if node.direction == "output":
                        pg.draw.circle(surface, (204, 102, 51), pos, size)
                if node.kind == "energy":
                    pg.draw.circle(surface, (255, 0, 0), pos, size)
                if node.kind == "fluid":
                    pg.draw.circle(surface, (0, 0, 255), pos, size)
        
        if tool_manager.current_tool:
            if isinstance(tool_manager.current_tool, LinkTool):
                if tool_manager.current_tool.placing:
                    pg.draw.aaline(surface, (135, 135, 135), 
                                   camera.world_to_screen(tool_manager.current_tool.start_pos), 
                                   camera.world_to_screen(input_manager.mouse_pos_closest_corner), 2)
            if isinstance(tool_manager.current_tool, PlaceTool):
                if tool_manager.context.selected_machine_id:
                    # get machine center position
                    mouse_pos = camera.world_to_screen(input_manager.mouse_pos_closest_corner)
                    machine_data = data_registry.machines[tool_manager.context.selected_machine_id]
                    fpx, fpy = get_footprint_center(machine_data['footprint'])
                    center_pos = (mouse_pos[0] - fpx*c.BASE_MACHINE_WIDTH, mouse_pos[1] - fpy*c.BASE_MACHINE_HEIGHT)

                    # draw machine profile
                    for x, y in machine_data['footprint']:
                        pos = (center_pos[0] + x*c.BASE_MACHINE_WIDTH, center_pos[1] + (y*c.BASE_MACHINE_HEIGHT))
                        pg.draw.rect(surface, (100//2, 100//2, 100//2), (pos, c.BASE_MACHINE_SIZE))
                    
                    # draw node previews
                    for node in machine_data["ionodes"]:
                        ox, oy = node['offset']
                        pos = (center_pos[0] + ox*c.BASE_MACHINE_WIDTH, center_pos[1] + oy*c.BASE_MACHINE_HEIGHT)
                        if node['type'] == 'energy':
                            color = (255//2, 0, 0)
                        elif node['type'] == 'item':
                            if node['direction'] == "input":
                                color = (0, 0, int(255*0.7))
                            if node['direction'] == "output":
                                color = (int(204*0.7), int(102*0.7), int(51*0.7))
                        elif node['type'] == 'fluid':
                            color = (0, 0, 255)
                        pg.draw.circle(surface, color, pos, 4)
        
        # debug labels
        f = self.debug_font.render(str(camera.screen_to_world(mouse_pos)), True, (255, 255, 255))
        surface.blit(f, (10, 10))

        f = self.debug_font.render("\n".join([f"{key}: {val}" for key, val in global_inventory._inventory.items()]), True, (255, 255, 255))
        surface.blit(f, (surface.width - f.get_width() - 15, 10))
        
        f = self.debug_font.render(str(input_manager.last_mouse_pos_snapped), True, (255, 255, 255))
        surface.blit(f, (10, 40))
        
        hovered_item = input_manager.hovered_item
        if hovered_item:
            obj_name = str(input_manager.hovered_item).split('.')[2].split(' ')[0]
        else:
            obj_name = "Nothing hovered"
        f = self.debug_font.render(str(obj_name), True, (255, 255, 255))
        surface.blit(f, (10, 40+40*1))
    