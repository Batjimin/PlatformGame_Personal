import pygame as pg
from .. import setup, tools
from .. import Setting as Set
from . import coin

#pg.sprite.Sprite: 스프라이트의 이미지,위치,충돌 감지 등을 관리하는 기본적인 기능을 제공
class Character(pg.sprite.Sprite):
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        
#게임 정보와 현재 게임 상태에 따라 라벨과 이미지를 생성하고 드로잉
class Info():
    def __init__(self, game_info, state):
        self.total_coin = game_info[Set.TOTAL_COIN]
        self.total_attendence = game_info[Set.ATTENDENCE]
        self.state = state
        self.game_info = game_info
        
        #필요한 라벨 및 이미지 생성
        self.create_font_image_dict()
        self.create_info_labels()
        self.create_state_labels()
        
    def create_font_image_dict(self):
        self.image_dict = {}
        
        image_rect_list = [# 0 - 9
                           (3, 230, 7, 7), (12, 230, 7, 7), (19, 230, 7, 7),
                           (27, 230, 7, 7), (35, 230, 7, 7), (43, 230, 7, 7),
                           (51, 230, 7, 7), (59, 230, 7, 7), (67, 230, 7, 7),
                           (75, 230, 7, 7), 
                           # A - Z
                           (83, 230, 7, 7), (91, 230, 7, 7), (99, 230, 7, 7),
                           (107, 230, 7, 7), (115, 230, 7, 7), (123, 230, 7, 7),
                           (3, 238, 7, 7), (11, 238, 7, 7), (20, 238, 7, 7),
                           (27, 238, 7, 7), (35, 238, 7, 7), (44, 238, 7, 7),
                           (51, 238, 7, 7), (59, 238, 7, 7), (67, 238, 7, 7),
                           (75, 238, 7, 7), (83, 238, 7, 7), (91, 238, 7, 7),
                           (99, 238, 7, 7), (108, 238, 7, 7), (115, 238, 7, 7),
                           (123, 238, 7, 7), (3, 246, 7, 7), (11, 246, 7, 7),
                           (20, 246, 7, 7), (27, 246, 7, 7), (48, 246, 7, 7),
                           # -*
                           (68, 249, 6, 2), (75, 247, 6, 6)]
                           
        character_string = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ -*'
        
        #zip함수 : 두 리스트 묶어서 순서대로 조합 -> 튜플로 표현
        #image_dict[character] : 문자열에 대응하는 이미지 참조 가능
        #영역 image_rect만큼 자르고 투명도 조정 후 2.9로 크기조정 
        for character, image_rect in zip(character_string, image_rect_list):
            self.image_dict[character] = tools.get_image(setup.GFX['text_images'], 
                                            *image_rect, (92, 148, 252), 2.9)

    def create_info_labels(self):
        self.score_text = []
        self.coin_text_label=[]
        self.coin_count_text = []
        self.score_label = []
        self.world_label = []
        self.time_label = []
        self.stage_label = []
        
        self.create_label(self.score_text, '000000', 75, 55)
        self.create_label(self.coin_text_label, 'COIN',270, 30)
        self.create_label(self.coin_count_text, '00', 270, 55)
        self.create_label(self.score_label, 'SCORE', 75, 30)
        self.create_label(self.world_label, 'HUFS', 472, 30)
        self.create_label(self.time_label, 'TIME', 625, 30)
        self.create_label(self.stage_label, '1-1', 472, 55)

        self.info_labels = [self.score_text,self.coin_text_label, self.coin_count_text, self.score_label,
                    self.world_label, self.time_label, self.stage_label]

    #프로그램 상태 별 라벨 생성. 라벨은 state속성을 바탕으로 생성된다.
    def create_state_labels(self):
        if self.state == Set.MAIN_MENU:
            self.create_main_menu_labels()
        elif self.state == Set.LOAD_SCREEN:
            self.create_player_image()
            self.create_load_screen_labels()
        elif self.state == Set.LEVEL:
            self.create_level_labels()
        elif self.state == Set.GAME_OVER:
            self.create_game_over_labels()
        elif self.state == Set.TIME_OUT:
            self.create_time_out_labels()

    def create_player_image(self):
        self.life_times_image = tools.get_image(setup.GFX['text_images'], 
                                75, 247, 6, 6, (92, 148, 252), 2.9)
        self.life_times_rect = self.life_times_image.get_rect(center=(378, 295))
        self.life_total_label = []
        self.create_label(self.life_total_label, str(self.total_attendence), 450, 285)
        
        if self.game_info[Set.PLAYER_NAME] == Set.PLAYER_1:
            rect = (178, 32, 12, 16)
        else:
            rect = (178, 128, 12, 16)
        self.player_image = tools.get_image(setup.GFX['player_chara'], 
                                *rect, (92, 148, 252), 2.9)
        self.player_rect = self.player_image.get_rect(center=(320, 290))

    def create_main_menu_labels(self):
        player1_game = []
        player2_game = []
        top = []
        top_score = []

        self.create_label(player1_game, Set.PLAYER1, 350, 360)
        self.create_label(player2_game, Set.PLAYER2, 350, 405)
        self.create_label(top, 'TOP - ', 350, 465)
        self.create_label(top_score, '000000', 460, 465)
        self.state_labels = [player1_game, player2_game, top, top_score,
                            *self.info_labels]
    
    def create_load_screen_labels(self):
        world_label = []
        self.stage_label2 = []

        self.create_label(world_label, 'HUFS', 300, 200)
        self.create_label(self.stage_label2, '1-1', 450, 200)
        self.state_labels = [world_label, self.stage_label2,
                *self.info_labels, self.life_total_label]

    def create_level_labels(self):
        self.time = Set.GAME_TIME_OUT
        self.current_time = 0

        self.clock_time_label = []
        self.create_label(self.clock_time_label, str(self.time), 645, 55)
        self.state_labels = [*self.info_labels, self.clock_time_label]

    def create_game_over_labels(self):
        game_label = []
        over_label = []
        f_label = []
        
        self.create_label(game_label, 'YOU', 280, 300)
        self.create_label(over_label, 'ARE', 360, 300)
        self.create_label(f_label, 'F', 440,300)
        
        self.state_labels = [game_label, over_label,f_label, *self.info_labels]

    def create_time_out_labels(self):
        timeout_label = []
        self.create_label(timeout_label, 'TIME OUT', 290, 310)
        self.state_labels = [timeout_label, *self.info_labels]

    #라벨 생성. 문자열을 label_list에 추가. 
    def create_label(self, label_list, string, x, y):
        for letter in string:
            label_list.append(Character(self.image_dict[letter]))
        self.set_label_rects(label_list, x, y)
    
    #사각 영역 설정. 
    def set_label_rects(self, label_list, x, y):
        #각 요소 인덱스와 함께 순회. 가로범위는 문자당 3.
        for i, letter in enumerate(label_list):
            letter.rect.x = x + ((letter.rect.width + 3) * i)
            letter.rect.y = y
            #하이픈 이미지 조정
            if letter.image == self.image_dict['-']:
                letter.rect.y += 7
                letter.rect.x += 2
    
    #레벨과 관련된 정보 처리, 상태 확인
    def update(self, level_info, level=None):
        self.level = level
        self.handle_level_state(level_info)
    
    def handle_level_state(self, level_info):
        self.score = level_info[Set.SCORE]
        self.update_text(self.score_text, self.score)
        self.update_text(self.coin_count_text, level_info[Set.TOTAL_COIN])
        self.update_text(self.stage_label, level_info[Set.LEVEL_NUM])
        if self.state == Set.LOAD_SCREEN:
            self.update_text(self.stage_label2, level_info[Set.LEVEL_NUM]) #레벨 알려주는 라벨
        #시간 오차 조정    
        if self.state == Set.LEVEL:
            if (level_info[Set.CURRENT_TIME] - self.current_time) > 1000:
                self.current_time = level_info[Set.CURRENT_TIME]
                self.time -= 1
                self.update_text(self.clock_time_label, self.time, True)
    
    def update_text(self, text, score, reset=False):
        #자릿수 초과 
        if reset and len(text) > len(str(score)):
            text.remove(text[0])
        index = len(text) - 1
        #점수 뒤에서 순회하며 가져온 문자이미지 text에 할당+사각형 영역 설정
        for digit in reversed(str(score)):
            rect = text[index].rect
            text[index] = Character(self.image_dict[digit])
            text[index].rect = rect
            index -= 1
        
    #Info 객체의 정보&라벨을 지정된 Surface에 blit     
    def draw(self, surface):
        self.draw_info(surface, self.state_labels)
        if self.state == Set.LOAD_SCREEN:
            surface.blit(self.player_image, self.player_rect)
            surface.blit(self.life_times_image, self.life_times_rect)
        
    
    # draw_info() 호출하여 정보 라벨을 그리고 blit() 메소드를 사용하여 이미지 그리기
    def draw_info(self, surface, label_list):
        for label in label_list:
            for letter in label:
                surface.blit(letter.image, letter.rect)




