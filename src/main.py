from . import tools
from . import Setting as Set
from .states import main_menu, load_screen, level

def main():
    game = tools.Control()
    state_dict = {Set.MAIN_MENU: main_menu.Menu(),
                  Set.LOAD_SCREEN: load_screen.LoadScreen(),
                  Set.LEVEL: level.Level(),
                  Set.GAME_OVER: load_screen.GameOver(),
                  Set.TIME_OUT: load_screen.TimeOut()}
    game.setup_states(state_dict, Set.MAIN_MENU)
    game.main()
