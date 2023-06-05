import pygame as pg
from .. import setup, tools
from .. import Setting as Set

#충돌 처리
class Collider(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, name):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((width, height)).convert() #테두리 따고 투명도 처리
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name
        #if Set.DEBUG:
        #    self.image.fill(Set.RED)
            #디버깅 중에는 self.image를 Set.RED 색상으로 채워보기.

#진행 상태 저장
class Checkpoint(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, type, enemy_groupid=0, map_index=0, name=Set.MAP_CHECKPOINT):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type
        self.enemy_groupid = enemy_groupid
        self.map_index = map_index
        self.name = name #Set.MAP_CHECKPOINT

class Etc(pg.sprite.Sprite):
    def __init__(self, x, y, sheet, image_rect_list, scale):
        pg.sprite.Sprite.__init__(self)
        
        self.frames = []
        self.frame_index = 0
        #시트에서 비율만큼 이미지 추출해 frames리스트에 추가
        for image_rect in image_rect_list:
            self.frames.append(tools.get_image(
                sheet, *image_rect, Set.BLACK, scale
            ))
        #이미지에 추가하고 사각 영역 초기화
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    #빈 메서드. 상속자가 사용할 예정.
    def update(self, *args):
        pass

class Pole(Etc):
    def __init__(self, x, y):
        Etc.__init__(self, x, y, setup.GFX['tile_set'],
                [(263, 144, 2, 16)], Set.TILE_SIZE_MULTIPLIER)

class PoleTop(Etc):
    def __init__(self, x, y):
        Etc.__init__(self, x, y, setup.GFX['tile_set'],
                [(228, 120, 8, 8)], Set.TILE_SIZE_MULTIPLIER)

class Flag(Etc):
    def __init__(self, x, y):
        Etc.__init__(self, x, y, setup.GFX[Set.ITEM_SHEET],
                [(128, 32, 16, 16)], Set.SIZE_MULTIPLIER)
        self.state = Set.TOP_OF_POLE
        self.y_vel = 5

    def update(self):
        if self.state == Set.SLIDE_DOWN:
            #아래로 내려가고 y좌표가 485를 넘으면 state변경.
            self.rect.y += self.y_vel
            if self.rect.bottom >= 485:
                self.state = Set.BOTTOM_OF_POLE

class CastleFlag(Etc):
    def __init__(self, x, y):
        Etc.__init__(self, x, y, setup.GFX[Set.ITEM_SHEET],
                [(129, 2, 14, 14)], Set.SIZE_MULTIPLIER)
        self.y_vel = -2
        self.target_height = y
    
    def update(self):
        #특정 높이까지 -2씩 이동
        if self.rect.bottom > self.target_height:
            self.rect.y += self.y_vel

#정수 스프라이트
class Digit(pg.sprite.Sprite):
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()

class Score():
    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.y_vel = -3
        self.create_images_dict()
        self.score = score
        self.create_score_digit()
        if self.score==1000:
            self.distance = 130
        else:
            self.distance = 75
        
    def create_images_dict(self):
        self.image_dict = {}
        digit_rect_list = [(1, 168, 3, 8), (5, 168, 3, 8),
                            (8, 168, 4, 8), (0, 0, 0, 0),
                            (12, 168, 4, 8), (16, 168, 5, 8),
                            (0, 0, 0, 0), (0, 0, 0, 0),
                            (20, 168, 4, 8), (0, 0, 0, 0)]
        digit_string = '0123456789'
        #zip함수 : 두 리스트 묶어서 순서대로 조합 -> 튜플로 표현
        for digit, image_rect in zip(digit_string, digit_rect_list):
            self.image_dict[digit] = tools.get_image(setup.GFX[Set.ITEM_SHEET],
                                    *image_rect, Set.BLACK, Set.TILE_SIZE_MULTIPLIER)
   
    
    #숫자랑 이미지 매칭해서 생성
    def create_score_digit(self):
        self.digit_group = pg.sprite.Group()
        self.digit_list = []
        for digit in str(self.score):
            self.digit_list.append(Digit(self.image_dict[digit]))
        
        #숫자 사이 간격 10px
        for i, digit in enumerate(self.digit_list):
            digit.rect = digit.image.get_rect()
            digit.rect.x = self.x + (i * 10)
            digit.rect.y = self.y
    
    #점수 위로 올라갔다가 삭제(y_vel = -3)
    def update(self, score_list):
        for digit in self.digit_list:
            digit.rect.y += self.y_vel
            
        if (self.y - self.digit_list[0].rect.y) > self.distance:
            score_list.remove(self)
            
    def draw(self, screen):
        for digit in self.digit_list:
            screen.blit(digit.image, digit.rect)

class Elevator(Etc):
    def __init__(self, x, y, width, height, type, name=Set.MAP_ELEVATOR):
        if type == Set.ELEVATOR_TYPE_HORIZONTAL:
            rect = [(32, 128, 37, 30)]
        else:
            rect = [(0, 160, 32, 30)]
        Etc.__init__(self, x, y, setup.GFX['tile_set'],
                rect, Set.TILE_SIZE_MULTIPLIER)
        self.name = name
        self.type = type
        #수직형 높이조정
        if type != Set.ELEVATOR_TYPE_HORIZONTAL:
            self.create_image(x, y, height)

    def create_image(self, x, y, elevator_height):
        img = self.image
        rect = self.image.get_rect()
        width = rect.w
        height = rect.h
        self.image = pg.Surface((width, elevator_height)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        #경계선 제거
        top_height = height//2 + 3 
        bottom_height = height//2 - 3
        self.image.blit(img, (0,0), (0, 0, width, top_height))
        num = (elevator_height - top_height) // bottom_height + 1
        #엘리베이터 쌓아올리기
        for i in range(num):
            y = top_height + i * bottom_height
            self.image.blit(img, (0,y), (0, top_height, width, bottom_height))
        #배경 검은색(투명화 작업)
        self.image.set_colorkey(Set.BLACK)

    #충돌무시 : 수평형, 하강상태
    def check_ignore_collision(self, level):
        if self.type == Set.ELEVATOR_TYPE_HORIZONTAL:
            return True
        elif level.player.state == Set.DOWN_ELEVATOR:
            return True
        return False

class Slider(Etc):
    def __init__(self, x, y, num, direction, range_start, range_end, vel, name=Set.MAP_SLIDER):
        Etc.__init__(self, x, y, setup.GFX[Set.ITEM_SHEET],
                [(64, 128, 15, 8)], 2.8)
        self.name = name
        self.create_image(x, y, num)
        self.range_start = range_start
        self.range_end = range_end
        self.direction = direction
        #수평, 수직 방향 두 가지 존재
        if self.direction == Set.VERTICAL:
            self.y_vel = vel
        else:
            self.x_vel = vel
        

    def create_image(self, x, y, num):
        '''이미지가 짧아서 엘리베이터처럼 중첩해 사용'''
        if num == 1:
            return
        img = self.image
        rect = self.image.get_rect()
        width = rect.w
        height = rect.h
        self.image = pg.Surface((width * num, height)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        for i in range(num):
            x = i * width
            self.image.blit(img, (x,0))
        self.image.set_colorkey(Set.BLACK)

    #이동하다 범위 or 화면 넘어서면 역주행
    def update(self):
        if self.direction ==Set.VERTICAL:
            self.rect.y += self.y_vel
            #화면 위 벗어나면 아래로 이동해서 상승
            if self.rect.y < -self.rect.h:
                self.rect.y = Set.SCREEN_HEIGHT
                self.y_vel = -1
            #아래 벗어나면 위로 이동해서 하강
            elif self.rect.y > Set.SCREEN_HEIGHT:
                self.rect.y = -self.rect.h
                self.y_vel = 1
            #지정범위보다 위면 시작점 고정 후 하강
            elif self.rect.y < self.range_start:
                self.rect.y = self.range_start
                self.y_vel = 1
            #지정범위보다 아래면 끝점 고정 후 상승
            elif self.rect.bottom > self.range_end:
                self.rect.bottom = self.range_end
                self.y_vel = -1
        else:
            self.rect.x += self.x_vel
            #범위 시작점 넘어가면 우측이동
            if self.rect.x < self.range_start:
                self.rect.x = self.range_start
                self.x_vel = 1
            #범위 끝점 넘어가면 좌측이동
            elif self.rect.left > self.range_end:
                self.rect.left = self.range_end
                self.x_vel = -1
    