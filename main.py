import pygame as pg
from collections import defaultdict

pg.init()
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
display_surface = pg.display.set_mode(SCREEN_SIZE)
clock = pg.time.Clock()

# Game variables
inventory = defaultdict(int)
font = pg.font.Font(r"asset\font\inter24.ttf", 18)
collection_notif: list[tuple[str, str, int, int]] = []

# Simulated "ground" click zone
ground_rect = pg.Rect((SCREEN_WIDTH//2)-50, (SCREEN_HEIGHT//2)-50, 100, 100)

def collect_item(item: str, ct: int = 1) -> int:
    """
    Adds item to inventory with ct number, returns new amount of that item.
    """
    inventory[item] += ct
    # increase previous collection notif if it is the same type, otherwise add new one
    if (len(collection_notif) > 0 and collection_notif[-1][0] == item and 
    ((collection_notif[-1][2] > 0 and ct > 0) or (collection_notif[-1][2] < 0 and ct < 0))):
        collection_notif[-1] = (item, inventory[item], collection_notif[-1][2] + ct, round(time))
    else:
        collection_notif.append((item, inventory[item], ct, round(time)))
    return inventory[item]

time = 0
running = True
while running:
    # variables
    dt = clock.tick() / 1000
    time += dt

    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if ground_rect.collidepoint(event.pos):
                collect_item("stone", 1)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 2:
            if ground_rect.collidepoint(event.pos):
                collect_item("stone", -1)
    
    # logic
    pg.display.set_caption(f"FPS: {round(clock.get_fps())}")

    # rendering
    display_surface.fill((30, 30, 30))

    # Draw the clickable ground area
    pg.draw.rect(display_surface, (60, 60, 60), ground_rect)


    # Draw inventory display
    stone_text = font.render(f"Stone: {inventory['stone']}", True, (255, 255, 255))
    display_surface.blit(stone_text, (10, 10))

    # show latest collections
    if len(collection_notif) > 0:        
        collection_item_height = 20
        collection_texts: list[tuple[pg.Surface, int]] = []
        recent_items = collection_notif[-5:].copy()
        recent_items.reverse()
        longest_str = 0
        for i, item in enumerate(recent_items):
            y = SCREEN_HEIGHT-collection_item_height*(i+1)
            if item[2] < 0: sign = "-"
            else: sign = "+"
            surf = font.render(f"({item[3]}) {item[0]} {sign}{abs(item[2])}", True, (255, 255, 255))
            longest_str = max(longest_str, surf.get_width())
            collection_texts.append((surf, y))

        rh = collection_item_height*len(collection_texts)
        pg.draw.rect(display_surface, (100, 100, 100), (0, SCREEN_HEIGHT-(rh), longest_str+15, rh))
        for text in collection_texts:
            display_surface.blit(text[0], (5, text[1]))

    pg.display.update()

pg.quit()
