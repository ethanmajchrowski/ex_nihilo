# === Python modules === #
import pygame as pg
from math import dist

# === Project modules === #
from module.inventory import InventoryManager
from module.machine import RockCrusher, Machine, Importer
from module.asset import ASSETS, load_assets
from module.conveyor import Conveyor, BeltItem
from module.node import IONode

import module.node
import settings

# === Pygame Setup === #
pg.init()
display_surface = pg.display.set_mode(settings.display_surface_SIZE)
clock = pg.time.Clock()
load_assets()

# === Data & State ===
font = pg.font.Font(r"asset\font\inter24.ttf", 18)

# Clickable ground
ground_rect = pg.Rect(settings.display_surface_WIDTH // 2 - 50, settings.display_surface_HEIGHT // 2 - 50, 100, 100)

# Running time for notifications, etc.
game_time = 0
# Store objects in the game world
world_objects = []
hovering_obj = None
selected_obj = None

inventory_manager = InventoryManager()

conveyor_start = ((0, 0), None)
placing_conveyor = False

# === Functions === #

def add_world_object(obj):
    world_objects.append(obj)

def update_world_objects(dt):
    for obj in world_objects:
        if hasattr(obj, "update"):
            obj.update(dt)

def draw_machine(surface: pg.Surface, machine: Machine, assets):
    if hasattr(machine, "frame"):
        img: pg.Surface = getattr(assets.machine, machine.type)[machine.frame]
    else:
        img: pg.Surface = getattr(assets.machine, machine.type)
    surface.blit(img, machine.rect)

    if machine.nodes:
        for node in machine.nodes:
            # color node properly
            color = (0, 0, 255) if node.kind == "input" else (255, 153, 0)
            
            # draw node as circle for now
            pg.draw.circle(surface, color, node.abs_pos, 5)

def draw_collection_overlay(surface):
    max_items = 5
    item_height = 20
    recent = inventory_manager.collection_log[-max_items:][::-1]
    rendered = []
    max_width = 0

    for i, event in enumerate(recent):
        sign = "+" if event.delta > 0 else "-"
        msg = f"({event.timestamp}) {event.item} {sign}{abs(event.delta)}"
        surf = font.render(msg, True, (255, 255, 255))
        rendered.append(surf)
        max_width = max(max_width, surf.get_width())

    # Background box
    total_height = len(rendered) * item_height
    box_rect = pg.Rect(0, settings.display_surface_HEIGHT - total_height, max_width + 15, total_height)
    pg.draw.rect(surface, (100, 100, 100), box_rect)

    # Draw text
    for i, surf in enumerate(rendered):
        y = settings.display_surface_HEIGHT - (i + 1) * item_height
        surface.blit(surf, (5, y))

# === Main Loop ===
add_world_object(RockCrusher((200, 200)))
# add_world_object(RockCrusher((500, 200)))
add_world_object(Importer((500, 400), inventory_manager))
# add_world_object(Conveyor(world_objects[0].nodes[1], world_objects[1].nodes[0], inventory_manager))

running = True
while running:
    dt = clock.tick() / 1000
    game_time += dt
    keys = pg.key.get_pressed()
    mouse_pos = pg.mouse.get_pos()

    # --- Events ---
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.MOUSEMOTION:
            hovering_obj = None
            for obj in world_objects:
                if isinstance(obj, Machine) and obj.rect.collidepoint(event.pos):
                    for node in obj.nodes:
                        if dist(node.abs_pos, event.pos) < 10:
                            hovering_obj = node
                            break
                    else:
                        # No node found, but mouse is over machine
                        hovering_obj = obj
                    break  # Stop after first matching object
        
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_h:
                for obj in world_objects:
                    if isinstance(obj, Conveyor):
                        obj.items.append(BeltItem("stone"))

        elif event.type == pg.MOUSEBUTTONDOWN:
            if ground_rect.collidepoint(event.pos):
                if event.button == 1:
                    inventory_manager.collect_item(inventory_manager.global_inventory, "stone", game_time, 1)
                elif event.button == 3:
                    inventory_manager.collect_item(inventory_manager.global_inventory, "stone", game_time, -1)
            elif hovering_obj is not None:
                selected_obj = hovering_obj
                if isinstance(selected_obj, module.node.IONode):
                    if keys[pg.K_g] and selected_obj.kind == "output": # if placing conveyor and hovering over output node
                        conveyor_start = selected_obj
                        print('started conveyor')
                    
                    elif isinstance(selected_obj.machine, RockCrusher):
                        if selected_obj.kind == "input":
                            inventory_manager.transfer_item(inventory_manager.global_inventory, selected_obj.machine.input_inventory, "stone", 1, game_time)
                        else:
                            inventory_manager.transfer_item(selected_obj.machine.output_inventory, inventory_manager.global_inventory, "gravel", 1, game_time)
        
        elif event.type == pg.MOUSEBUTTONUP:
            if conveyor_start is not None:
                if isinstance(hovering_obj, IONode) and hovering_obj.kind == "input":
                    print('finished conveyor')
                    # TODO: do not allow conveyors with identical start and end nodes
                    add_world_object(Conveyor(conveyor_start, hovering_obj, inventory_manager))
                
                conveyor_start = None

    # --- Logic ---
    pg.display.set_caption(f"FPS: {round(clock.get_fps())}")
    for obj in world_objects:
        if isinstance(obj, Machine):
            obj.update(dt)
        if isinstance(obj, Conveyor):
            obj.update(dt, game_time)

    # --- Render ---
    display_surface.fill((30, 30, 30))
    pg.draw.rect(display_surface, (60, 60, 60), ground_rect)

    for obj in world_objects:
        if isinstance(obj, Machine):
            draw_machine(display_surface, obj, ASSETS)
        if isinstance(obj, Conveyor):
            pg.draw.line(display_surface, (255, 255, 255), obj.start, obj.end, 5)
            obj.draw_items(display_surface)
    
    if conveyor_start is not None:
        pg.draw.line(display_surface, (255, 255, 255), conveyor_start.abs_pos, mouse_pos, 5)

    # inventory_manager display
    item_display = font.render(f"Stone: {inventory_manager.global_inventory['stone']}", True, (255, 255, 255))
    display_surface.blit(item_display, (10, 10))
    item_display = font.render(f"Gravel: {inventory_manager.global_inventory['gravel']}", True, (255, 255, 255))
    display_surface.blit(item_display, (10, 10+item_display.get_height()))

    # IONode contents hover
    if hovering_obj is not None:
        if isinstance(hovering_obj, IONode):
            contents = hovering_obj.machine.input_inventory if hovering_obj.kind == "input" else hovering_obj.machine.output_inventory
            contents = font.render("\n".join(f"{k}: {v}" for k, v in contents.items()), True, (255, 255, 255), (0, 0, 0))
            display_surface.blit(contents, contents.get_rect(bottomleft = mouse_pos))

    # Notifications
    if inventory_manager.collection_log:
        draw_collection_overlay(display_surface)
    
    # Finish up
    pg.display.update()

pg.quit()