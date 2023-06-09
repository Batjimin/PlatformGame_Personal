# coin item
import pygame as pg
from .. import setup, tools
from .. import Setting as s


class Coin(pg.sprite.Sprite):   
    def __init__(self, x, y, score_group):
        pg.sprite.Sprite.__init__(self)

        self.frames = []
        self.frame_index = 0
        self.load_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y - 5
        self.gravity = 1
        self.y_vel = -15
        self.animation_timer = 0
        self.initial_height = self.rect.bottom - 5
        self.score_group = score_group

    def load_frames(self):
        sheet = setup.GFX[s.ITEM_SHEET] #이미지 시트 가져오기
        frame_rect_list = [(52, 113, 8, 14), (4, 113, 8, 14), #애니메이션의 각 프레임의 영역을 정의
                           (20, 113, 8, 14), (36, 113, 8, 14)] #프레임의 좌표와 크기 정보를 담고 있는 리스트. 각각의 튜플은 (x, y, width, height) 형식
        for frame_rect in frame_rect_list: 
            self.frames.append(tools.get_image( #이미지 시트에서 frame_rect에 해당하는 영역을 잘라내어 프레임 이미지를 가져옴
                sheet, *frame_rect, s.BLACK, s.TILE_SIZE_MULTIPLIER)) 
            #s.BLACK은 투명한 부분의 색상을 나타내는 RGB 값
            #s.TILE_SIZE_MULTIPLIER는 이미지의 크기를 조정하는 비율

    
    def update(self, game_info):
        self.current_time = game_info[s.CURRENT_TIME]
        self.spinning()
        
    def spinning(self): # 동전 회전 관련, 중력에 따라 동전 위치 업데이트
        self.image = self.frames[self.frame_index]
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        
        if (self.current_time - self.animation_timer) > 80:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animation_timer = self.current_time
        
        if self.rect.bottom > self.initial_height:  # 일정 높이 아래로 내려올 시 kill
            self.kill()
            
class StaticCoin(pg.sprite.Sprite): # 정지된 코인 
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.frame_index = 0
        self.frames = []
        self.load_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_timer = 0

    def load_frames(self):  # 코인 클래스의 동명 함수와 동일한 역할
        sheet = setup.GFX[s.ITEM_SHEET]
        frame_rect_list = [(3, 98, 9, 13), (19, 98, 9, 13),
                        (35, 98, 9, 13), (51, 98, 9, 13)]
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect, 
                            s.BLACK, s.TILE_SIZE_MULTIPLIER))

    def update(self, game_info):    # 시간에 따라 프레임 변경
        self.current_time = game_info[s.CURRENT_TIME]

        time_list = [375, 125, 125, 125]
        if self.animation_timer == 0:
            self.animation_timer = self.current_time
        elif (self.current_time - self.animation_timer) > time_list[self.frame_index]:
            self.frame_index += 1
            if self.frame_index == 4:
                self.frame_index = 0
            self.animation_timer = self.current_time
        
        self.image = self.frames[self.frame_index]
        
class FlashCoin(pg.sprite.Sprite):  # 깜빡이는 동전
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.frame_index = 0
        self.frames = []
        self.load_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_timer = 0
        
    def load_frames(self):
        sheet = setup.GFX[s.ITEM_SHEET]
        frame_rect_list = [(1, 160, 5, 8), (9, 160, 5, 8),
                        (17, 160, 5, 8), (9, 160, 5, 8)]
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect, 
                            s.BLACK, s.TILE_SIZE_MULTIPLIER))

    def update(self, current_time):
        time_list = [375, 125, 125, 125]
        if self.animation_timer == 0:
            self.animation_timer = current_time
        elif (current_time - self.animation_timer) > time_list[self.frame_index]:
            self.frame_index += 1
            if self.frame_index == 4:
                self.frame_index = 0
            self.animation_timer = current_time
        
        self.image = self.frames[self.frame_index]