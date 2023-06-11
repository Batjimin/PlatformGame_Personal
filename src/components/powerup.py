import pygame as pg
from .. import setup
from .. import Setting as Set
from . import etc

class Powerup(etc.Etc):
    def __init__(self, x, y, sheet, image_rect_list, scale):
        etc.Etc.__init__(self, x, y, sheet, image_rect_list, scale)
        self.rect.centerx = x
        self.state = Set.REVEAL
        self.y_vel = -1
        self.x_vel = 0
        self.direction = Set.RIGHT
        self.QR_brick_height = y
        self.gravity = 1
        self.max_y_vel = 8
        self.animate_timer = 0
    
    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        
        self.rect.y += self.y_vel
        self.check_y_collisions(level)
        
        if self.rect.x <= 0:
            self.kill()
        elif self.rect.y > (level.viewport.bottom):
            self.kill()

    #벽 접촉 시 방향전환
    def check_x_collisions(self, level):
        sprite_group = pg.sprite.Group(level.ground_step_elevator_group,
                            level.tile_group, level.QR_brick_group)
        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite:
            if self.direction == Set.RIGHT:
                self.rect.right = sprite.rect.left-1
                self.direction = Set.LEFT
            elif self.direction == Set.LEFT:
                self.rect.left = sprite.rect.right
                self.direction = Set.RIGHT
            self.x_vel = self.speed if self.direction == Set.RIGHT else -1 * self.speed
            if sprite.name == Set.MAP_TILE:
                self.x_vel = 0
    
    def check_y_collisions(self, level):
        sprite_group = pg.sprite.Group(level.ground_step_elevator_group,
                            level.tile_group, level.QR_brick_group)

        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite:
            self.y_vel = 0
            self.rect.bottom = sprite.rect.top
            self.state = Set.SLIDE
        level.check_is_falling(self)

    def animation(self):
        self.image = self.frames[self.frame_index]

class Coffee(Powerup):
    def __init__(self, x, y):
        Powerup.__init__(self, x, y, setup.GFX[Set.ITEM_SHEET],
                [(0, 0, 16, 16)], Set.SIZE_MULTIPLIER)
        self.type = Set.TYPE_COFFEE
        self.speed = 2

    def update(self, game_info, level):
        if self.state == Set.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom <= self.QR_brick_height:
                self.rect.bottom = self.QR_brick_height
                self.y_vel = 0
                self.state = Set.SLIDE
        elif self.state == Set.SLIDE:
            self.x_vel = self.speed if self.direction == Set.RIGHT else -1 * self.speed
        elif self.state == Set.FALL:
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity
        
        if self.state == Set.SLIDE or self.state == Set.FALL:
            self.update_position(level)
        self.animation()

class LifeCoffee(Coffee):
    def __init__(self, x, y):
        Powerup.__init__(self, x, y, setup.GFX[Set.ITEM_SHEET],
                [(16, 0, 16, 16)], Set.SIZE_MULTIPLIER)
        self.type = Set.TYPE_LIFECOFFEE
        self.speed = 2

class Hot6(Powerup):
    def __init__(self, x, y):
        frame_rect_list = [(0, 32, 16, 16), (16, 32, 16, 16),
                        (32, 32, 16, 16), (48, 32, 16, 16)]
        Powerup.__init__(self, x, y, setup.GFX[Set.ITEM_SHEET],
                    frame_rect_list, Set.SIZE_MULTIPLIER)
        self.type = Set.TYPE_HOT6

    def update(self, game_info, *args):
        self.current_time = game_info[Set.CURRENT_TIME]
        if self.state == Set.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom <= self.QR_brick_height:
                self.rect.bottom = self.QR_brick_height
                self.y_vel = 0
                self.state = Set.STAYED
        
        if (self.current_time - self.animate_timer) > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animate_timer = self.current_time

        self.animation()

class Star(Powerup):
    def __init__(self, x, y):
        frame_rect_list = [(1, 48, 15, 16), (17, 48, 15, 16),
                        (33, 48, 15, 16), (49, 48, 15, 16)]
        Powerup.__init__(self, x, y, setup.GFX[Set.ITEM_SHEET],
                    frame_rect_list, Set.SIZE_MULTIPLIER)
        self.type = Set.TYPE_STAR
        self.gravity = .4
        self.speed = 5
        
    def update(self, game_info, level):
        self.current_time = game_info[Set.CURRENT_TIME]
        if self.state == Set.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom <= self.QR_brick_height:
                self.rect.bottom = self.QR_brick_height
                self.y_vel = -2
        
        if (self.current_time - self.animate_timer) > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animate_timer = self.current_time
        
        self.animation()
    
    def check_y_collisions(self, level):
        sprite_group = pg.sprite.Group(level.ground_step_elevator_group,
                            level.tile_group, level.QR_brick_group)

        sprite = pg.sprite.spritecollideany(self, sprite_group)

        if sprite:
            if self.rect.top > sprite.rect.top:
                self.y_vel = 5
            else:
                self.rect.bottom = sprite.rect.y
                self.y_vel = -5
                
class FireBall(Powerup):
    def __init__(self, x, y, facing_right):
        # first 3 Frames are flying, last 4 frams are exploding
        frame_rect_list = [(96, 144, 8, 8), (104, 144, 8, 8), 
                        (96, 152, 8, 8), (104, 152, 8, 8),
                        (112, 144, 16, 16), (112, 160, 16, 16),
                        (112, 176, 16, 16)]
        Powerup.__init__(self, x, y, setup.GFX[Set.ITEM_SHEET],
                    frame_rect_list, Set.SIZE_MULTIPLIER)
        self.type = Set.TYPE_FIREBALL
        self.y_vel = 10
        self.gravity = .9
        self.state = Set.FLYING
        self.rect.right = x
        if facing_right:
            self.direction = Set.RIGHT
            self.x_vel = 12
        else:
            self.direction = Set.LEFT
            self.x_vel = -12

    def update(self, game_info, level):
        self.current_time = game_info[Set.CURRENT_TIME]
        
        if self.state == Set.FLYING :
            self.y_vel += self.gravity
            if (self.current_time - self.animate_timer) > 200:
                if self.frame_index < 3:
                    self.frame_index += 1
                else:
                    self.frame_index = 0
                self.animate_timer = self.current_time
            self.update_position(level)
        elif self.state == Set.EXPLODING:
            if (self.current_time - self.animate_timer) > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                else:
                    self.kill()
                self.animate_timer = self.current_time
        self.animation()
    
    def check_x_collisions(self, level):
        sprite_group = pg.sprite.Group(level.ground_step_elevator_group,
                            level.tile_group, level.QR_brick_group)
        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite:
            self.change_to_explode()
    
    def check_y_collisions(self, level):
        sprite_group = pg.sprite.Group(level.ground_step_elevator_group,
                            level.tile_group, level.QR_brick_group)

        sprite = pg.sprite.spritecollideany(self, sprite_group)
        enemy = pg.sprite.spritecollideany(self, level.enemy_group)
        if sprite:
            if self.rect.top > sprite.rect.top:
                self.change_to_explode()
            else:
                self.rect.bottom = sprite.rect.y
                self.y_vel = -8
                if self.direction == Set.RIGHT:
                    self.x_vel = 15
                else:
                    self.x_vel = -15
                
        elif enemy:
            if (enemy.name != Set.FIRESTICK) :
                level.update_score(100, enemy, 0)
                level.move_to_dying_group(level.enemy_group, enemy)
                enemy.start_death_jump(self.direction)
            self.change_to_explode()
    
    def change_to_explode(self):
        self.frame_index = 4
        self.state = Set.EXPLODING
