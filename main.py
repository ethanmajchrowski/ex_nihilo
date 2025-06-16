import pygame as pg
from collections import defaultdict, namedtuple
from module.machine import RockCrusher, Machine
import module.node
from module.asset import ASSETS, load_assets
import settings
from math import dist

pg.init()
display_surface = pg.display.set_mode(settings.display_surface_SIZE)
clock = pg.time.Clock()
load_assets()

# === Data & State ===
global_inventory = defaultdict(int)
font = pg.font.Font(r"asset\font\inter24.ttf", 18)

# Clickable ground
ground_rect = pg.Rect(settings.display_surface_WIDTH // 2 - 50, settings.display_surface_HEIGHT // 2 - 50, 100, 100)
# Collection notifications
CollectionEvent = namedtuple("CollectionEvent", "item new_total delta timestamp")
collection_log: list[CollectionEvent] = []
# Running time for notifications, etc.
game_time = 0
# Store objects in the game world
world_objects = []
hovering_obj = None
selected_obj = None

def add_world_object(obj):
    world_objects.append(obj)

def update_world_objects(dt):
    for obj in world_objects:
        if hasattr(obj, "update"):
            obj.update(dt)

def draw_machine(surface: pg.Surface, machine: Machine, assets):
    img: pg.Surface = getattr(assets.machine, machine.type)
    surface.blit(img, machine.rect)

    if machine.nodes:
        for node in machine.nodes:
            # color node properly
            color = (0, 0, 255) if node.kind == "input" else (255, 153, 0)
            
            # draw node as circle for now
            pg.draw.circle(surface, color, node.abs_pos, 5)

def collect_item(inventory, item: str, amount: int = 1) -> int:
    inventory[item] += amount
    if inventory != global_inventory:
        return

    # Combine with previous entry if same item and direction (gain/loss)
    # (collection_log[-1].delta * amount > 0) checks because (positive * positive = positive) and (negative * negative = positive)
    if (collection_log) and (collection_log[-1].item == item) and (collection_log[-1].delta * amount > 0):
        last = collection_log.pop()
        new_event = CollectionEvent(item, inventory[item], last.delta + amount, round(game_time))
        collection_log.append(new_event)
    else:
        collection_log.append(CollectionEvent(item, inventory[item], amount, round(game_time)))

    return inventory[item]

def transfer_item(inventory1, inventory2, item, count):
    """
    Transfers count of item from inventory1 to inventory2
    """
    if inventory1[item] - count < 0:
        return
    collect_item(inventory1, item, -count)
    collect_item(inventory2, item, count)

def draw_collection_overlay(surface):
    max_items = 5
    item_height = 20
    recent = collection_log[-max_items:][::-1]
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

running = True
while running:
    dt = clock.tick() / 1000
    game_time += dt

    # --- Events ---
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.MOUSEBUTTONDOWN:
            if ground_rect.collidepoint(event.pos):
                if event.button == 1:
                    collect_item(global_inventory, "stone", 1)
                elif event.button == 3:
                    collect_item(global_inventory, "stone", -1)
            elif hovering_obj is not None:
                selected_obj = hovering_obj
                if isinstance(selected_obj, module.node.IONode):
                    if isinstance(selected_obj.machine, RockCrusher):
                        if selected_obj.kind == "input":
                            transfer_item(global_inventory, selected_obj.machine.input_inventory, "stone", 1)
                        else:
                            transfer_item(selected_obj.machine.output_inventory, global_inventory, "gravel", 1)
        
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

    # --- Logic ---
    pg.display.set_caption(f"FPS: {round(clock.get_fps())}")
    for obj in world_objects:
        if isinstance(obj, Machine):
            obj.update(dt)

    # --- Render ---
    display_surface.fill((30, 30, 30))
    pg.draw.rect(display_surface, (60, 60, 60), ground_rect)

    for obj in world_objects:
        if isinstance(obj, Machine):
            draw_machine(display_surface, obj, ASSETS)

    # Inventory display
    item_display = font.render(f"Stone: {global_inventory['stone']}", True, (255, 255, 255))
    display_surface.blit(item_display, (10, 10))
    item_display = font.render(f"Gravel: {global_inventory['gravel']}", True, (255, 255, 255))
    display_surface.blit(item_display, (10, 10+item_display.get_height()))

    # Notifications
    if collection_log:
        draw_collection_overlay(display_surface)
    
    # Finish up
    pg.display.update()

pg.quit()