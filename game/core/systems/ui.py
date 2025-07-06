import pygame as pg
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
import config.configuration as c

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from core.game import Game

# custom class to overrider on_close_window_button_pressed to hide instead of kill the window
class UIHidingWindow(pygame_gui.elements.UIWindow):
    def __init__(self, rect: pg.Rect | pg.FRect, manager: IUIManagerInterface | None = None, window_display_title: str = "", element_id: List[str] | str | None = None, object_id: ObjectID | str | None = None, resizable: bool = False, visible: int = 1, draggable: bool = True, *, ignore_shadow_for_initial_size_and_pos: bool = True, always_on_top: bool = False):
        super().__init__(rect, manager, window_display_title, element_id, object_id, resizable, visible, draggable, ignore_shadow_for_initial_size_and_pos=ignore_shadow_for_initial_size_and_pos, always_on_top=always_on_top)

    def on_close_window_button_pressed(self):
        self.hide()

class UIManager:
    def __init__(self, display_size: tuple[int, int]) -> None:
        self.ui_manager = pygame_gui.UIManager(display_size, r"assets\graphics\themes\theme.json")
        # self.ui_manager = pygame_gui.UIManager(display_size)
        self.ui_manager.theme_update_check_interval = 0.25
        self.game: "Game"
        
        class containers:
            top_bar = pygame_gui.elements.UIPanel(relative_rect=pg.Rect(0, 10, (30*4)+12, 36), manager=self.ui_manager, 
                                                  anchors={"centerx": "centerx"})
            
            _rect = pg.Rect(c.DISPLAY_WIDTH_CENTER-300, c.DISPLAY_HEIGHT_CENTER-250, 600, 500)
            inventory_window = UIHidingWindow(rect=_rect, manager=self.ui_manager, 
                                                  window_display_title="Inventory", resizable=True)
            inventory_window.hide()
            recipe_window = UIHidingWindow(rect=_rect, manager=self.ui_manager, 
                                                  window_display_title="Recipes", resizable=True)
            recipe_window.hide()
            build_window = UIHidingWindow(rect=_rect, manager=self.ui_manager, 
                                                  window_display_title="Build", resizable=True)
            build_window.hide()
            stats_window = UIHidingWindow(rect=_rect, manager=self.ui_manager, 
                                                  window_display_title="Statistics", resizable=True)
            stats_window.hide()
        self.containers = containers
        
        class elements:
            # === Top bar buttons === #
            inventory_tab_button = pygame_gui.elements.UIButton(relative_rect=(0, 0, 30, 30), 
                                             manager=self.ui_manager, text="I", 
                                             container=self.containers.top_bar)
            inventory_tab_button.set_tooltip("Inventory")
            recipes_tab_button = pygame_gui.elements.UIButton(relative_rect=(30, 0, 30, 30), 
                                             manager=self.ui_manager, text="R", 
                                             container=self.containers.top_bar)
            recipes_tab_button.set_tooltip("Recipes")
            build_tab_button = pygame_gui.elements.UIButton(relative_rect=(60, 0, 30, 30), 
                                             manager=self.ui_manager, text="B", 
                                             container=self.containers.top_bar)
            build_tab_button.set_tooltip("Build")
            stats_tab_button = pygame_gui.elements.UIButton(relative_rect=(90, 0, 30, 30), 
                                             manager=self.ui_manager, text="S", 
                                             container=self.containers.top_bar)
            stats_tab_button.set_tooltip("Statistics")
            
        self.elements = elements
            
    def render_ui(self, surface: pg.Surface) -> None:
        self.ui_manager.draw_ui(surface)
    
    def update_ui(self, dt: float) -> None:
        self.ui_manager.update(dt)
        
    def process_event(self, event) -> None:
        self.ui_manager.process_events(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            match event.ui_element:
                # Gameplay windows
                case self.elements.inventory_tab_button:
                    if not self.containers.inventory_window.visible:
                        self.containers.inventory_window.show()
                case self.elements.recipes_tab_button:
                    if not self.containers.recipe_window.visible:
                        self.containers.recipe_window.show()
                case self.elements.build_tab_button:
                    if not self.containers.build_window.visible:
                        self.containers.build_window.show()
                case self.elements.stats_tab_button:
                    if not self.containers.stats_window.visible:
                        self.containers.stats_window.show()
    
    def hello_button_pressed(self):
        print("hello!")
