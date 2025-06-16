import pygame as pg
from collections import defaultdict, namedtuple
import time

pg.init()
display_surface_WIDTH, display_surface_HEIGHT = 800, 600
display_surface_SIZE = (display_surface_WIDTH, display_surface_HEIGHT)
display_surface = pg.display.set_mode(display_surface_SIZE)
clock = pg.time.Clock()

# === Data & State ===
inventory = defaultdict(int)
font = pg.font.Font(r"asset\font\inter24.ttf", 18)

# Clickable ground
ground_rect = pg.Rect(display_surface_WIDTH // 2 - 50, display_surface_HEIGHT // 2 - 50, 100, 100)
# Collection notifications
CollectionEvent = namedtuple("CollectionEvent", "item new_total delta timestamp")
collection_log: list[CollectionEvent] = []

game_time = 0

def collect_item(item: str, amount: int = 1) -> int:
    inventory[item] += amount

    # Combine with previous entry if same item and direction (gain/loss)
    # (collection_log[-1].delta * amount > 0) checks because (positive * positive = positive) and (negative * negative = positive)
    if (collection_log) and (collection_log[-1].item == item) and (collection_log[-1].delta * amount > 0):
        last = collection_log.pop()
        new_event = CollectionEvent(item, inventory[item], last.delta + amount, round(game_time))
        collection_log.append(new_event)
    else:
        collection_log.append(CollectionEvent(item, inventory[item], amount, round(game_time)))

    return inventory[item]

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
    box_rect = pg.Rect(0, display_surface_HEIGHT - total_height, max_width + 15, total_height)
    pg.draw.rect(surface, (100, 100, 100), box_rect)

    # Draw text
    for i, surf in enumerate(rendered):
        y = display_surface_HEIGHT - (i + 1) * item_height
        surface.blit(surf, (5, y))

# === Main Loop ===

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
                    collect_item("stone", 1)
                elif event.button == 3:
                    collect_item("stone", -1)

    # --- Logic ---
    pg.display.set_caption(f"FPS: {round(clock.get_fps())}")

    # --- Render ---
    display_surface.fill((30, 30, 30))
    pg.draw.rect(display_surface, (60, 60, 60), ground_rect)

    # Inventory display
    stone_display = font.render(f"Stone: {inventory['stone']}", True, (255, 255, 255))
    display_surface.blit(stone_display, (10, 10))

    # Notifications
    if collection_log:
        draw_collection_overlay(display_surface)
    
    # Finish up
    pg.display.update()

pg.quit()