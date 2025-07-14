from logger import logger
import pygame as pg
import data.configuration as c

from game.game import Game

def main():
    pg.init()
    display_surface = pg.display.set_mode(c.DISPLAY_SIZE)
    pg.display.set_caption("EX NIHILO | FPS: 0")
    logger.info("Game initialized")
    game = Game(display_surface)
    game.run()

if __name__ == "__main__":
    main()