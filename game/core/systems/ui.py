import pygame as pg
import config.configuration as c

from core.entities.machine import Machine, RecipeMachine
from core.entities.node import IONode, NodeType
from logger import logger

from typing import TYPE_CHECKING, List, Any
if TYPE_CHECKING:
    from core.game import Game

class UIElement:
    def __init__(self, rect, visible=True):
        self.rect = pg.Rect(rect)
        self.visible = visible
        self.children = []
        self.parent = None

    def draw(self, surface):
        if not self.visible:
            return
        self.draw_self(surface)
        for child in self.children:
            child.draw(surface)

    def draw_self(self, surface):
        pass  # Override in subclass

    def handle_event(self, event):
        if not self.visible:
            return
        for child in self.children:
            child.handle_event(event)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def global_rect(self, rect=None):
        if rect is None:
            rect = self.rect
        if not self.parent:
            return rect
        parent_rect = self.parent.global_rect()
        return rect.move(parent_rect.topleft)

class UIToolbar(UIElement):
    def __init__(self, screen_width, height=40, padding=10, bg_color=(50, 50, 50)):
        super().__init__(pg.Rect(0, 0, screen_width, height))
        self.bg_color = bg_color
        self.padding = padding

    def draw_self(self, surface):
        rect = self.global_rect()
        pg.draw.rect(surface, self.bg_color, rect)
        pg.draw.rect(surface, (100, 100, 100), rect, 2)
        
class UIWindow(UIElement):
    def __init__(self, rect, title="Window", bg_color=(50, 50, 50)):
        super().__init__(rect)
        self.title = title
        self.bg_color = bg_color
        self.visible = True
        self.font = pg.font.SysFont("Arial", 16)

        self.close_button = UIButton(pg.Rect(self.rect.width - 25, 5, 20, 20), "X", self.close)
        self.add_child(self.close_button)

    def draw_self(self, surface):
        rect = self.global_rect(self.rect)
        pg.draw.rect(surface, self.bg_color, rect, border_radius=10)
        # draw outline
        pg.draw.rect(surface, (100, 100, 100), rect, 2, border_radius=10)
        title_surf = self.font.render(self.title, True, (255, 255, 255))
        surface.blit(title_surf, rect.move(10, 5))
    
    def close(self):
        self.visible = False
    
    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        if hasattr(child, "resize_to_parent"):
            child.resize_to_parent()

class UILabel(UIElement):
    def __init__(self, rect, text, font_size=16, color=(255, 255, 255)):
        super().__init__(rect)
        self.text = text
        self.color = color
        self.font = pg.font.SysFont("Arial", font_size)

    def draw_self(self, surface):
        rect = self.global_rect()
        text_surf = self.font.render(self.text, True, self.color)
        surface.blit(text_surf, rect)

class UIButton(UIElement):
    def __init__(self, rect, text, callback=None, bg_color=(60, 60, 60), hover_color=(80, 80, 80), text_color=(255, 255, 255),
                 clickable = True, disabled_color=(40, 40, 40)):
        super().__init__(rect)
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hover = False
        self.font = pg.font.SysFont("Arial", 16)
        self.clickable = clickable
        self.disabled_color = disabled_color

    def draw_self(self, surface):
        rect = self.global_rect()
        color = self.hover_color if self.hover else self.bg_color
        if not self.clickable:
            color = self.disabled_color
        pg.draw.rect(surface, color, rect, border_radius=5)
        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def handle_event(self, event):
        if not self.clickable:
            return
        rect = self.global_rect()
        if event.type == pg.MOUSEMOTION:
            self.hover = rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos) and self.callback:
                self.callback()
        super().handle_event(event)

class UIToggleButton(UIButton):
    def __init__(self, rect, text, callback=None, bg_color=(60, 60, 60), hover_color=(80, 80, 80), text_color=(255, 255, 255),
                 active_color=(100, 100, 100)):
        super().__init__(rect, text, callback, bg_color, hover_color, text_color)
        self.state = False
        self.active_search_color = active_color
        
    def handle_event(self, event):
        rect = self.global_rect()
        if event.type == pg.MOUSEMOTION:
            self.hover = rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos):
                self.state = not self.state
                if self.callback:
                    self.callback()
    
    def draw_self(self, surface):
        rect = self.global_rect()
        # color = self.hover_color if self.hover else self.bg_color
        if self.hover:      color = self.hover_color
        elif self.state:    color = self.active_search_color
        else:               color = self.bg_color
        
        pg.draw.rect(surface, color, rect, border_radius=5)
        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, text_surf.get_rect(center=rect.center))

class UIInventoryPanel(UIElement):
    def __init__(self, game: "Game"):
        super().__init__(pg.Rect(0, 0, 0, 0))  # placeholder rect
        self.game = game
        self.search_query = ""
        self.scroll_offset = 0
        self.font = pg.font.SysFont("Arial", 16)
        self.row_height = 40
        self.visible_rows = 0
        self.search_bar_height = 25
        self.active_search = False
        
        self.hover = False
        self.hovering_pos = (0, 0)
        
        self.row_buttons: dict[str, list[UIButton]] = {}
    
    def get_buttons_for_item(self, item_name: str) -> list[UIButton]:
        buttons: list[UIButton] = []
        
        if c.REGISTRY.is_craftable(item_name):
            buttons.append(UIButton(pg.Rect(0, 0, 60, 24), "Craft", callback=lambda: self.open_craft_panel(item_name), bg_color=(50, 50, 50)))
        
        if item_name in c.REGISTRY.machines:
            buttons.append(UIButton(pg.Rect(0, 0, 60, 24), "Place", callback=lambda: self.place_machine(item_name), bg_color=(50, 50, 50)))
        
        buttons.append(UIButton(pg.Rect(0, 0, 60, 24), "Info", callback=lambda: self.show_item_info(item_name), bg_color=(50, 50, 50)))
        
        if (item_name in c.REGISTRY.items 
                and self.game.inventory_manager.global_inventory.get(item_name, 0) > 0):
            if c.REGISTRY.get_item(item_name).is_tagged("can_deposit"):
                buttons.append(UIButton(pg.Rect(0, 0, 60, 24), "Place", callback=lambda: self.place_machine(item_name), bg_color=(50, 50, 50)))
        
        if item_name in c.REGISTRY.transport:
            buttons.append(UIButton(pg.Rect(0, 0, 60, 24), "Place", callback=lambda: self.place_transport(item_name), bg_color=(50, 50, 50)))
        
        return buttons
    
    def open_craft_panel(self, item_name: str):
        assert self.parent is not None
        self.parent.visible = False
        self.game.ui_manager.windows[1].visible = True
        crafting_panel = self.game.ui_manager.windows[1].children[1]
        assert isinstance(crafting_panel, UICraftingPanel)
        crafting_panel.selected_object = c.REGISTRY.get_item(item_name)
    
    def place_machine(self, item_name: str):
        machine = c.REGISTRY.get_machine(item_name)
        assert machine is not None
        assert self.parent is not None
        logger.info(f"PLacing machine {machine.name}")
        self.parent.visible = False
        self.game.state.selected_placing = machine
        self.game.state.tools.PLACING_MACHINE = True
        self.game.state.selected_rot = 0
    
    def place_transport(self, item_name: str):
        transport = c.REGISTRY.get_transport(item_name)
        assert self.parent is not None
        logger.info(f"Placing transport {transport.name}")
        self.parent.visible = False
        self.game.state.selected_placing = transport
        self.game.state.tools.PLACING_CONVEYORS = True
    
    def show_item_info(self, item_name: str):
        pass
    
    def deposit_item(self, item_name: str):
        pass
    
    def resize_to_parent(self):
        print(self.rect)
        if not self.parent:
            return
        parent_rect = self.parent.rect
        self.rect = pg.Rect(5, 30, parent_rect.width - 10, parent_rect.height - 35)
        self.visible_rows = (self.rect.height - self.search_bar_height - 5) // self.row_height
        self.search_bar_rect = pg.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, 20)

    def handle_event(self, event):
        for button_row in self.row_buttons.values():
            for button in button_row:
                button.handle_event(event)

        if event.type == pg.MOUSEBUTTONDOWN:
            self.active_search = self.global_rect(self.search_bar_rect).collidepoint(event.pos)
            if self.active_search and event.button == 3:
                self.search_query = ""

        elif event.type == pg.KEYDOWN and self.active_search:
            if event.key == pg.K_BACKSPACE:
                self.search_query = self.search_query[:-1]
            elif event.key == pg.K_RETURN:
                self.active_search = False
            elif event.unicode.isprintable():
                self.search_query += event.unicode

        elif event.type == pg.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.row_height
            max_offset = max(0, len(self.filtered_items()) - self.visible_rows) * self.row_height
            self.scroll_offset = max(0, min(self.scroll_offset, max_offset))
        
        elif event.type == pg.MOUSEMOTION:
            self.hover = self.global_rect().collidepoint(event.pos)
            if self.hover:
                self.hovering_pos = event.pos

    def filtered_items(self):
        inv = self.game.inventory_manager.global_inventory
        return sorted([name for name in inv if self.search_query.lower() in name.lower()])

    def draw_self(self, surface):
        #background
        pg.draw.rect(surface, (20, 20, 20), self.global_rect(), border_radius=5)

        # Draw search bar
        search_rect = self.global_rect(self.search_bar_rect)
        pg.draw.rect(surface, (40, 40, 40), search_rect)
        pg.draw.rect(surface, (90, 90, 90), search_rect, 2)
        text = self.search_query if (self.active_search or self.search_query) else "Search..."
        search_text = self.font.render(text, True, (200, 200, 200))
        surface.blit(search_text, search_rect.move(5, 2))

        # Draw filtered items
        items = self.filtered_items()
        start_index = self.scroll_offset // self.row_height
        end_index = min(start_index + self.visible_rows, len(items))
        display_items = items[start_index:end_index]

        for i, name in enumerate(display_items):
            y = self.rect.y + 30 + i * self.row_height
            self.draw_item_row(surface, name, y)

    def draw_item_row(self, surface, name, y):
        rect = self.global_rect(pg.Rect(self.rect.x + 5, y, self.rect.width - 10, self.row_height - 2))
        color = (60, 60, 60) if not (self.hover and rect.collidepoint(self.hovering_pos)) else (70, 70, 70)
        pg.draw.rect(surface, color, rect)

        # Image
        if self.game.asset_manager.is_asset("items", name):
            image = self.game.asset_manager.assets["items"][name]
        else:
            image = self.game.asset_manager.assets["items"]["null"]
        
        image = pg.transform.scale2x(image)
        if image:
            surface.blit(image, (rect.x + 2, rect.y + 2))

        # Name and amount
        amount = self.game.inventory_manager.global_inventory.get(name, 0)
        text = f"{name.title()}: {amount}"
        label = self.font.render(text, True, (255, 255, 255))
        surface.blit(label, (rect.x + 40, rect.y + 10))
        
        # Row Buttons
        if name not in self.row_buttons:
            self.row_buttons[name] = self.get_buttons_for_item(name)
        
        buttons = self.row_buttons[name]
        x = rect.right - len(buttons) * 70 + 5 * (len(buttons) - 1) - 5
        for button in buttons:
            button.rect.topleft = (x, rect.y + 5)
            button.draw(surface)
            x += button.rect.width + 5

class UIMachineTooltip(UIElement):
    def __init__(self, game: "Game"):
        super().__init__(pg.Rect(0, 0, 200, 120))  # will auto-position top-right
        self.game = game
        self.machine = None
        self.font = pg.font.SysFont("Arial", 16)
        self.visible = False

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            hovered = self.game.state.hovering_obj
            self.visible = False
            self.machine = None
            if hovered:
                for item in hovered:
                    if isinstance(item, Machine):
                        self.machine = item
                        self.visible = True

            # Update position top-right
            sw, _ = self.game.display.get_size()
            self.rect.topleft = (sw - self.rect.width - 10, 10)

    def draw_self(self, surface):
        if not self.visible or not self.machine:
            return

        pg.draw.rect(surface, (25, 25, 25), self.global_rect(), border_radius=5)
        pg.draw.rect(surface, (80, 80, 80), self.global_rect(), 1, border_radius=5)
        
        recipe, progress_text, recipe_text = None, None, None
        if isinstance(self.machine, RecipeMachine) and self.machine.active_recipe is not None:
            recipe = self.machine.active_recipe

            if recipe.inputs and recipe.outputs:
                recipe_text = f"> {recipe.inputs} -> {recipe.outputs} ({recipe.duration}s)"
            elif recipe.inputs and not recipe.outputs:
                recipe_text = f"> Collecting {recipe.inputs} ({recipe.duration}s)"
            elif recipe.outputs and not recipe.inputs:
                recipe_text = f"> Generating {recipe.outputs} ({recipe.duration}s)"
            else:
                recipe_text = f"> Misc recipe ({recipe.duration}s)"
            
            progress_text = f"> Progress: {int((self.machine.progress/recipe.duration) * 100)}%"

        input_nodes = {}
        output_nodes = {}
        for node in self.machine.nodes:
            if node.kind == "input" and node.node_type == NodeType.ITEM:
                input_nodes.update(node.inventory)
            elif node.kind == "output" and node.node_type == NodeType.ITEM:
                output_nodes.update(node.inventory)

        lines = [
            f"{self.machine.mtype.name}",
            recipe_text,
            progress_text, 
            f"> I/O: {input_nodes} / {output_nodes}"
        ]

        i = 0
        for text in lines:
            if text is None:
                continue
            txt_surf = self.font.render(text, True, (255, 255, 255))
            surface.blit(txt_surf, (self.rect.x + 8, self.rect.y + 8 + i * 20))
            i += 1

class UICraftingPanel(UIElement):
    def __init__(self, game: "Game"):
        super().__init__(pg.Rect(0, 0, 0, 0))
        self.game = game
        self.search_query = ""
        self.scroll_offset = 0
        self.font = pg.font.SysFont("Arial", 16)
        self.row_height = 40
        self.search_bar_height = 25
        self.visible_rows = 0
        self.active_search = False
        self.selected_object: Any = None
        self.hover = False
        self.hovering_pos = (0, 0)
        self.sidebar_width = 200

        # Predefined craft button
        self.craft_button = UIButton(
            rect=pg.Rect(0, 0, 120, 30),
            text="Craft",
            callback=self.craft_selected_machine,
            bg_color=(60, 100, 60),
            hover_color=(80, 120, 80)
        )
        # self.craft_button.parent = self

    def resize_to_parent(self):
        if not self.parent:
            return
        parent_rect = self.parent.rect
        self.rect = pg.Rect(5, 30, parent_rect.width - 10, parent_rect.height - 35)
        self.visible_rows = (self.rect.height - self.search_bar_height - 5) // self.row_height
        self.search_bar_rect = pg.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10 - self.sidebar_width, 20)

    def handle_event(self, event):
        self.craft_button.handle_event(event)

        if event.type == pg.MOUSEBUTTONDOWN:
            self.active_search = self.global_rect(self.search_bar_rect).collidepoint(event.pos)
            if self.active_search and event.button == 3:
                self.search_query = ""

            for i, machine in enumerate(self.filtered_machines()[self.scroll_offset // self.row_height :]):
                row_rect = self.global_rect(pg.Rect(
                    self.rect.x + 5, self.rect.y + 30 + i * self.row_height,
                    self.rect.width - self.sidebar_width - 20, self.row_height - 2
                ))
                if row_rect.collidepoint(event.pos):
                    self.selected_object = machine
                    
                    break

        elif event.type == pg.KEYDOWN and self.active_search:
            if event.key == pg.K_BACKSPACE:
                self.search_query = self.search_query[:-1]
            elif event.key == pg.K_RETURN:
                self.active_search = False
            elif event.unicode.isprintable():
                self.search_query += event.unicode

        elif event.type == pg.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.row_height
            max_offset = max(0, len(self.filtered_machines()) - self.visible_rows) * self.row_height
            self.scroll_offset = max(0, min(self.scroll_offset, max_offset))

        elif event.type == pg.MOUSEMOTION:
            self.hover = self.global_rect().collidepoint(event.pos)
            if self.hover:
                self.hovering_pos = event.pos

    def filtered_machines(self):
        return [
            item for item in c.REGISTRY.get_craftable().values()
            if self.search_query.lower() in item.name.lower()
        ]

    def draw_self(self, surface: pg.Surface):
        pg.draw.rect(surface, (25, 25, 25), self.global_rect(), border_radius=5)

        # Draw search bar
        search_rect = self.global_rect(self.search_bar_rect)
        pg.draw.rect(surface, color=(40, 40, 40), rect=search_rect)
        pg.draw.rect(surface, color=(90, 90, 90), rect=search_rect, width=2)
        
        text = self.search_query if (self.active_search or self.search_query) else "Search..."
        search_text = self.font.render(text, antialias=True, color=(200, 200, 200))
        
        surface.blit(source=search_text, dest=search_rect.move(5, 2))

        # Draw filtered machine list
        machines = self.filtered_machines()
        start = self.scroll_offset // self.row_height
        end = min(start + self.visible_rows, len(machines))
        display = machines[start:end]

        for i, mtype in enumerate(display):
            y = self.rect.y + 30 + i * self.row_height
            self.draw_machine_row(surface, mtype, y)

        # Sidebar
        self.draw_sidebar(surface)

    def draw_machine_row(self, surface, mtype, y):
        row_rect = self.global_rect(pg.Rect(
            self.rect.x + 5, y, self.rect.width - self.sidebar_width - 10, self.row_height - 2
        ))
        color = (60, 60, 60) if not (self.hover and row_rect.collidepoint(self.hovering_pos)) else (70, 70, 70)
        if self.selected_object == mtype:
            color = (80, 80, 80)
        pg.draw.rect(surface, color, row_rect)

        text = self.font.render(mtype.name.title(), True, (255, 255, 255))
        surface.blit(text, (row_rect.x + 10, row_rect.y + 10))

    def draw_sidebar(self, surface):
        sidebar_rect = self.global_rect(pg.Rect(
            self.rect.right - self.sidebar_width, self.rect.y + 5,
            self.sidebar_width - 5, self.rect.height - 10
        ))
        pg.draw.rect(surface, (40, 40, 40), sidebar_rect, border_radius=5)

        x = sidebar_rect.x + 10
        y = sidebar_rect.y + 10

        if self.selected_object:
            mtype = self.selected_object
            surface.blit(self.font.render(mtype.name.title(), True, (255, 255, 0)), (x, y))
            y += 25

            surface.blit(self.font.render("Cost:", True, (200, 200, 200)), (x, y))
            y += 20
            for item, amt in mtype.craft_cost.items():
                surface.blit(self.font.render(f"{item}: {self.game.inventory_manager.global_inventory[item]}/{amt}", True, (180, 180, 180)), (x, y))
                y += 18

            y += 10
            current = self.game.inventory_manager.global_inventory.get(mtype.name, 0)
            surface.blit(self.font.render(f"Owned: {current}", True, (100, 255, 100)), (x, y))
            y += 35

            # Position and draw static craft button
            self.craft_button.rect = pg.Rect(x, y, 120, 30)
            self.craft_button.draw(surface)

        else:
            surface.blit(self.font.render("Select a machine", True, (150, 150, 150)), (x, y))

    def craft_selected_machine(self):
        if not self.selected_object:
            return
        if self.game.inventory_manager.can_craft(self.selected_object):
            self.game.inventory_manager.craft(self.selected_object)

class UIHotbarButton(UIToggleButton):
    def __init__(self, rect, text, bg_color=(60, 60, 60), hover_color=(80, 80, 80), text_color=(255, 255, 255), active_color=(100, 100, 100)):
        super().__init__(rect, text, None, bg_color, hover_color, text_color, active_color)
    
    def handle_event(self, event):
        rect = self.global_rect()
        if event.type == pg.MOUSEMOTION:
            self.hover = rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos):
                self.state = not self.state
                if self.callback:
                    self.callback(self)

class UIHotbar(UIElement):
    def __init__(self, center_pos, visible=True):
        self.rect = pg.Rect(0, 0, 0, 40)
        self.center = center_pos
        super().__init__(self.rect, visible)
        self.buttons: list[UIHotbarButton] = []
        self.active_search_button = -1
        
        self.width = 0
    
    def add_button(self, button: UIHotbarButton):
        button.callback = self.button_callback
        self.buttons.append(button)
        self.add_child(button)
        self.update_rect()
    
    def update_rect(self):
        # assumes all buttons are the same width
        self.width = 5
        for i, button in enumerate(self.buttons):
            # add width to background rect + 5 for padding
            self.width += button.rect.w + 5
            button.rect.top = 5
            # set button position to 5 padding on left and right and then width of buttons
            button.rect.x = 5*(i+1) + i*button.rect.w
            # fix button positions
        self.rect.w = self.width
        self.rect.center = self.center
        print("width: ", self.width)
    
    def draw_self(self, surface):
        pg.draw.rect(surface, (50, 50, 50), self.rect, border_radius=5)
    
    def button_callback(self, button: UIHotbarButton):
        for other_button in self.buttons:
            if other_button is not button:
                other_button.state = False

class UIPlacingInfo(UIElement):
    def __init__(self, game: "Game"):
        self.rect = pg.Rect(0, 0, 200, 56)
        self.rect.bottomright = (c.DISPLAY_WIDTH-10, c.DISPLAY_HEIGHT-10)
        super().__init__(self.rect)
        
        self.game = game
        self.font = pg.sysfont.SysFont("Arial", 16)
    
    def draw_self(self, surface):
        pg.draw.rect(surface, (25, 25, 25), self.global_rect(), border_radius=5)
        pg.draw.rect(surface, (80, 80, 80), self.global_rect(), 1, border_radius=5)
        
        txt_surf = self.font.render(
        f"Placing {self.game.state.selected_placing.name}", 
        antialias=True, 
        color=(255, 255, 255))
        surface.blit(txt_surf, (self.rect.x + 8, self.rect.y + 8))
        
        txt_surf = self.font.render(
        f"{self.game.inventory_manager.global_inventory[self.game.state.selected_placing.name]} left", 
        antialias=True, 
        color=(255, 255, 255))
        surface.blit(txt_surf, (self.rect.x + 8, self.rect.y + 28))

class UIManager:
    def __init__(self):
        self.game: "Game"
        self.elements = []
        self.windows: list[UIWindow] = []  # for external access if needed

    def create_ui(self):
        # Toolbar
        self.toolbar = UIToolbar(screen_width=c.DISPLAY_WIDTH)
        self.add(self.toolbar)

        # Windows
        toolbars = ["Inventory", "Crafting", "Recipes", "Statistics"]
        for i in range(4):
            window_width, window_height = c.DISPLAY_WIDTH * 0.75, c.DISPLAY_HEIGHT * 0.80
            window_left, window_top = c.DISPLAY_WIDTH_CENTER - window_width//2, c.DISPLAY_HEIGHT_CENTER - window_height//2
            win = UIWindow(pg.Rect(window_left, window_top, window_width, window_height), title=toolbars[i])
            self.add(win)
            self.windows.append(win)
            win.visible = False

        # Toolbar buttons to toggle windows
        for i in range(4):
            def make_callback(w=self.windows[i]):
                return lambda: setattr(w, "visible", not w.visible)

            btn = UIButton(pg.Rect(0, 0, 80, 30), toolbars[i], make_callback())
            btn.rect.topleft = (c.DISPLAY_WIDTH // 2 - 170 + i * 90, 5)
            self.toolbar.add_child(btn)
        
        self.inv_panel = UIInventoryPanel(self.game)
        self.windows[0].add_child(self.inv_panel)
        
        self.crafting_panel = UICraftingPanel(self.game)
        self.windows[1].add_child(self.crafting_panel)
        
        self.tooltip = UIMachineTooltip(self.game)
        self.elements.append(self.tooltip)
        
        self.placing_info = UIPlacingInfo(self.game)
        self.elements.append(self.placing_info)
        
        # self.hotbar = UIHotbar((c.DISPLAY_WIDTH_CENTER, c.DISPLAY_HEIGHT*0.9))
        # self.elements.append(self.hotbar)
        # self.hotbar.add_button(UIHotbarButton(pg.rect.Rect(0, 0, 55, 30), "PLACE"))
        # self.hotbar.add_button(UIHotbarButton(pg.rect.Rect(0, 0, 55, 30), "LINK"))
        # self.hotbar.add_button(UIHotbarButton(pg.rect.Rect(0, 0, 55, 30), "DELETE"))

    def add(self, element):
        self.elements.append(element)

    def draw(self, surface):
        for el in self.elements:
            el.draw(surface)

    def handle_event(self, event):
        for el in self.elements:
            el.handle_event(event)
