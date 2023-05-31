import pygame as pg
from .. import tools
from .. import setup
from .. import Setting as Set
from .. components import info

class Menu(tools.State):
    def __init__(self):
        tools.State.__init__(self)
        persist = {Set.TOTAL_COIN: 0,
                   Set.SCORE: 0,
                   Set.ATTENDENCE: 3,
                   Set.TOP_SCORE: 0,
                   Set.CURRENT_TIME: 0.0,
                   Set.LEVEL_NUM: 1,
                   Set.PLAYER_NAME: Set.PLAYER_1}
        self.startup(0.0, persist)
    
    def startup(self, current_time, persist):
        self.next = Set.LOAD_SCREEN #메뉴 다음 로딩
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.Info(self.game_info, Set.MAIN_MENU)

        self.setup_background()
        self.setup_player()
        self.setup_cursor()
        
    def setup_background(self):
        self.background = setup.GFX['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                    (int(self.background_rect.width*Set.BACKGROUND_MULTIPLER),
                                    int(self.background_rect.height*Set.BACKGROUND_MULTIPLER)))
        
        self.viewport = setup.SCREEN.get_rect(bottom=setup.SCREEN_RECT.bottom) #스크린 사각영역
        self.image_dict = {}
        image = tools.get_image(setup.GFX['title_screen'], 1, 60, 176, 88,
                            (255, 0, 220), Set.SIZE_MULTIPLIER)
        rect = image.get_rect()
        rect.x, rect.y = (170, 100)
        self.image_dict['GAME_NAME_BOX'] = (image, rect)

    def setup_player(self):
        self.player_list = []
        player_rect_info = [(178, 32, 12, 16), (178, 128, 12, 16)]
        for rect in player_rect_info:
            image = tools.get_image(setup.GFX['player_chara'],
                                *rect, Set.BLACK, 2.9)
            rect = image.get_rect()
            rect.x, rect.bottom = 110, Set.GROUND_HEIGHT
            self.player_list.append((image, rect))
        self.player_index = 0

    #커서 설정. 이미지는 ITEM_SHEET에서, 디폴트는 PLAYER1에.
    def setup_cursor(self):
        self.cursor = pg.sprite.Sprite()
        self.cursor.image = tools.get_image(setup.GFX[Set.ITEM_SHEET], 24, 160, 8, 8, Set.BLACK, 3)
        rect = self.cursor.image.get_rect()
        rect.x, rect.y = (220, 358)
        self.cursor.rect = rect
        self.cursor.state = Set.PLAYER1

    #화면 업데이트
    def update(self, surface, keys, current_time):
        self.current_time = current_time
        self.game_info[Set.CURRENT_TIME] = self.current_time
        self.player_image = self.player_list[self.player_index][0]
        self.player_rect = self.player_list[self.player_index][1]
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        #이미지 그리기
        surface.blit(self.background, self.viewport, self.viewport)
        surface.blit(self.image_dict['GAME_NAME_BOX'][0],
                     self.image_dict['GAME_NAME_BOX'][1])
        surface.blit(self.player_image, self.player_rect)
        surface.blit(self.cursor.image, self.cursor.rect)
        #정보 표시 화면 출력
        self.overhead_info.draw(surface)

    def update_cursor(self, keys):
        if self.cursor.state == Set.PLAYER1:
            self.cursor.rect.y = 358
            if keys[pg.K_DOWN]:
                self.cursor.state = Set.PLAYER2
                self.player_index = 1
                self.game_info[Set.PLAYER_NAME] = Set.PLAYER_2
        elif self.cursor.state == Set.PLAYER2:
            self.cursor.rect.y = 403
            if keys[pg.K_UP]:
                self.cursor.state = Set.PLAYER1
                self.player_index = 0
                self.game_info[Set.PLAYER_NAME] = Set.PLAYER_1
        if keys[pg.K_RETURN]:
            self.reset_game_info()
            self.done = True
    
    def reset_game_info(self):
        self.game_info[Set.TOTAL_COIN] = 0
        self.game_info[Set.SCORE] = 0
        self.game_info[Set.ATTENDENCE] = 3
        self.game_info[Set.CURRENT_TIME] = 0.0
        self.game_info[Set.LEVEL_NUM] = 1
        
        self.persist = self.game_info