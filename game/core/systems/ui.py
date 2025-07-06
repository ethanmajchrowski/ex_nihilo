import pygame as pg
import pygame_gui
import pygame_gui.ui_manager

class UIManager:
    def __init__(self, display_size: tuple[int, int]) -> None:
        self.ui_manager = pygame_gui.ui_manager.UIManager(display_size)
        
        class elements:
            hello_button = pygame_gui.elements.UIButton(relative_rect=pg.Rect((10, 10, 50, 35)),
                                                        text="hello!",
                                                        manager=self.ui_manager)
        self.elements = elements
    
    def render_ui(self, surface: pg.Surface) -> None:
        self.ui_manager.draw_ui(surface)
    
    def update_ui(self, dt: float) -> None:
        self.ui_manager.update(dt)
        
    def process_event(self, event) -> None:
        self.ui_manager.process_events(event)