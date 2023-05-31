
import os
import pygame as pg
from . import Setting as Set
from . import tools

pg.init()
pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
SCREEN = pg.display.set_mode(Set.SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()

GFX = tools.load_gfx(os.path.join("resources","graphics"))