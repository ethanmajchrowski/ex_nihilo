# Project modules
from core.game import Game, GameState

from core.systems.asset import AssetManager
from core.systems.renderer import Renderer
from core.systems.input import InputManager
from core.systems.inventory import InventoryManager
from core.systems.ui import UIManager

from logger import logger

import config.configuration as c

# Libraries
import pygame as pg

# Load all game assets
def load_assets() -> AssetManager:
    logger.info("Loading game assets")
    asset_manager = AssetManager()

    # Load machines
    asset_manager.register_group("machines")
    # asset_manager.add_asset("machines", "RockCrusher", asset_manager.load_animation(r"C:\Workspace\Projects\blender\renders\automation_game\grinder\\", 31))
    asset_manager.add_asset("machines", "RockCrusher", asset_manager.load_animation(r"C:\Workspace\Projects\blender\renders\automation_game\grinder\\", 1))
    # asset_manager.add_asset("machines", "Importer", asset_manager.load_animation(r"C:\Workspace\Projects\blender\renders\automation_game\importer\\", 60))
    asset_manager.add_asset("machines", "Importer", asset_manager.load_animation(r"C:\Workspace\Projects\blender\renders\automation_game\importer\\", 1))

    # Load fonts
    asset_manager.register_group("fonts")
    asset_manager.add_asset("fonts", "inter", asset_manager.load_font(r"assets\font\inter24.ttf", 24))

    return asset_manager

def main():
    logger.info("Starting game setup")
    
    # === Setup pygame things === #
    pg.init()
    pg.font.init()
    display_surface = pg.display.set_mode(c.DISPLAY_SIZE)
    
    # === Create system managers === #
    game_state = GameState()
    inventory_manager = InventoryManager()
    asset_manager = load_assets()
    renderer = Renderer()
    input_manager = InputManager()
    ui_manager = UIManager(display_surface.get_size())
    
    # === Create & run Game === #
    game = Game(display_surface, game_state, pg.Clock(), asset_manager, renderer, input_manager, inventory_manager, ui_manager)
    logger.info("Game initialization complete, running!")
    game.run()
    
    # Game is closed
    pg.quit()

if __name__ == "__main__":
    main()