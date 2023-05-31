import pygame as pg
from .. import setup, tools
from .. import Setting as Set

class Collider(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, name):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((width, height)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name
        if Set.DEBUG:
            self.image.fill(Set.RED)
            #Set.DEBUG가 True인 경우에만 self.image를 Set.RED 색상으로 채움.

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
        self.name = name

class Etc(pg.sprite.Sprite):
    def __init__(self, x, y, sheet, image_rect_list, scale):
        pg.sprite.Sprite.__init__(self)
        
        self.frames = []
        self.frame_index = 0
        for image_rect in image_rect_list:
            self.frames.append(tools.get_image(sheet, 
                    *image_rect, Set.BLACK, scale))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
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
        if self.rect.bottom > self.target_height:
            self.rect.y += self.y_vel

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
        self.distance = 130 if self.score == 1000 else 75
        
    def create_images_dict(self):
        self.image_dict = {}
        digit_rect_list = [(1, 168, 3, 8), (5, 168, 3, 8),
                            (8, 168, 4, 8), (0, 0, 0, 0),
                            (12, 168, 4, 8), (16, 168, 5, 8),
                            (0, 0, 0, 0), (0, 0, 0, 0),
                            (20, 168, 4, 8), (0, 0, 0, 0)]
        digit_string = '0123456789'
        for digit, image_rect in zip(digit_string, digit_rect_list):
            self.image_dict[digit] = tools.get_image(setup.GFX[Set.ITEM_SHEET],
                                    *image_rect, Set.BLACK, Set.TILE_SIZE_MULTIPLIER)
    
    def create_score_digit(self):
        self.digit_group = pg.sprite.Group()
        self.digit_list = []
        for digit in str(self.score):
            self.digit_list.append(Digit(self.image_dict[digit]))
        
        for i, digit in enumerate(self.digit_list):
            digit.rect = digit.image.get_rect()
            digit.rect.x = self.x + (i * 10)
            digit.rect.y = self.y
    
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

        top_height = height//2 + 3
        bottom_height = height//2 - 3
        self.image.blit(img, (0,0), (0, 0, width, top_height))
        num = (elevator_height - top_height) // bottom_height + 1
        for i in range(num):
            y = top_height + i * bottom_height
            self.image.blit(img, (0,y), (0, top_height, width, bottom_height))
        self.image.set_colorkey(Set.BLACK)

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
        if self.direction == Set.VERTICAL:
            self.y_vel = vel
        else:
            self.x_vel = vel
        

    def create_image(self, x, y, num):
        '''original slider image is short, we need to multiple it '''
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

    def update(self):
        if self.direction ==Set.VERTICAL:
            self.rect.y += self.y_vel
            if self.rect.y < -self.rect.h:
                self.rect.y = Set.SCREEN_HEIGHT
                self.y_vel = -1
            elif self.rect.y > Set.SCREEN_HEIGHT:
                self.rect.y = -self.rect.h
                self.y_vel = 1
            elif self.rect.y < self.range_start:
                self.rect.y = self.range_start
                self.y_vel = 1
            elif self.rect.bottom > self.range_end:
                self.rect.bottom = self.range_end
                self.y_vel = -1
        else:
            self.rect.x += self.x_vel
            if self.rect.x < self.range_start:
                self.rect.x = self.range_start
                self.x_vel = 1
            elif self.rect.left > self.range_end:
                self.rect.left = self.range_end
                self.x_vel = -1
    