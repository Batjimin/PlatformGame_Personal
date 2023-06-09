import os
import json
import pygame as pg
from .. import setup, tools
from .. import Setting as Set
from ..components import powerup

class Player(pg.sprite.Sprite):
    def __init__(self, player_name):
        pg.sprite.Sprite.__init__(self)
        self.player_name = player_name
        self.load_data()
        self.setup_timer()
        self.setup_state()
        self.setup_speed()
        self.load_images()
        
        self.frame_index = 0
        self.state = Set.WALK
        self.image = self.right_frames[self.frame_index]
        self.rect = self.image.get_rect()

    #죽은 후 재시작
    def restart(self):
        if self.dead:
            self.dead = False
            self.big = False
            self.fire = False
            self.set_player_image(self.small_normal_frames, 0)
            self.right_frames = self.small_normal_frames[0]
            self.left_frames = self.small_normal_frames[1]
        self.state = Set.STOPPED

    #지정 경로에서 player_name.json 로드하기
    def load_data(self):
        player_file = str(self.player_name) + '.json'
        file_path = os.path.join('src', 'data', 'player', player_file)
        f = open(file_path)
        self.player_data = json.load(f)

    def setup_timer(self):
        self.walking_timer = 0
        self.death_timer = 0
        self.flagpole_timer = 0
        self.transition_timer = 0
        self.hurt_invincible_timer = 0
        self.invincible_timer = 0
        self.last_fireball_time = 0

    def setup_state(self):
        #시선 오른쪽
        self.facing_right = True 
        self.allow_jump = True
        self.allow_fireball = True
        #특수 상태는 모두 False
        self.dead = False
        self.big = False
        self.fire = False
        self.hurt_invincible = False
        self.invincible = False
        self.crouching = False

    #player_data에서 설정된 값들을 가져와 각 속성에 할당
    def setup_speed(self):
        speed = self.player_data[Set.PLAYER_SPEED]
        self.x_vel = 0
        self.y_vel = 0
        
        self.max_walk_vel = speed[Set.MAX_WALK_SPEED]
        self.max_run_vel = speed[Set.MAX_RUN_SPEED]
        self.max_y_vel = speed[Set.MAX_Y_VEL]
        self.walk_accel = speed[Set.WALK_ACCEL]
        self.run_accel = speed[Set.RUN_ACCEL]
        self.jump_vel = speed[Set.JUMP_VEL]
        
        self.gravity = Set.GRAVITY
        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel

    def load_images(self):
        sheet = setup.GFX['player_chara']
        frames_list = self.player_data[Set.PLAYER_FRAMES]

        self.right_frames = []
        self.left_frames = []

        self.right_small_normal_frames = []
        self.left_small_normal_frames = []
        self.right_big_normal_frames = []
        self.left_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_big_fire_frames = []
        
        for name, frames in frames_list.items():
            for frame in frames:
                image = tools.get_image(sheet, frame['x'], frame['y'], 
                                    frame['width'], frame['height'],
                                    Set.BLACK, Set.SIZE_MULTIPLIER)
                #왼쪽 방향 이미지는 좌우반전
                left_image = pg.transform.flip(image, True, False)

                #상태별 필요한 이미지 append
                if name == Set.RIGHT_SMALL_NORMAL:
                    self.right_small_normal_frames.append(image)
                    self.left_small_normal_frames.append(left_image)
                elif name == Set.RIGHT_BIG_NORMAL:
                    self.right_big_normal_frames.append(image)
                    self.left_big_normal_frames.append(left_image)
                elif name == Set.RIGHT_BIG_FIRE:
                    self.right_big_fire_frames.append(image)
                    self.left_big_fire_frames.append(left_image)
        
        self.small_normal_frames = [self.right_small_normal_frames,
                                    self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames,
                                    self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames,
                                    self.left_big_fire_frames]
                                    
        self.all_images = [self.right_small_normal_frames,
                           self.left_small_normal_frames,
                           self.right_big_normal_frames,
                           self.left_big_normal_frames,
                           self.right_big_fire_frames,
                           self.left_big_fire_frames]
        
        #좌우 프레임 리스트 초기화(작은 일반 크기)
        self.right_frames = self.small_normal_frames[0]
        self.left_frames = self.small_normal_frames[1]

    #입력&정보 기반으로 피격 상태, 무적 상태 확인.
    def update(self, keys, game_info, fire_group):
        self.current_time = game_info[Set.CURRENT_TIME]
        self.handle_state(keys, fire_group)
        self.check_if_hurt_invincible()
        self.check_if_invincible()
        self.animation()

    #상태에 따른 동작 수행.
    def handle_state(self, keys, fire_group):
        if self.state == Set.STOPPED:
            self.stopped(keys, fire_group)
        elif self.state == Set.WALK:
            self.walking(keys, fire_group)
        elif self.state == Set.JUMP:
            self.jumping(keys, fire_group)
        elif self.state == Set.FALL:
            self.falling(keys, fire_group)
        elif self.state == Set.DEATH_JUMP:
            self.jumping_to_death()
        elif self.state == Set.FLAGPOLE:
            self.flag_pole_sliding()
        elif self.state == Set.WALK_AUTO:
            self.walking_auto()
        elif self.state == Set.END_OF_LEVEL_FALL:
            self.y_vel += self.gravity
        elif self.state == Set.GOAL_IN:
            self.frame_index = 0
        elif self.state == Set.SMALL_TO_BIG:
            self.changing_to_big()
        elif self.state == Set.BIG_TO_SMALL:
            self.changing_to_small()
        elif self.state == Set.BIG_TO_FIRE:
            self.changing_to_fire()
        elif self.state == Set.DOWN_ELEVATOR:
            self.y_vel = 1
            self.rect.y += self.y_vel
        #올라가다 일정 높이에서 stop
        elif self.state == Set.UP_ELEVATOR:
            self.y_vel = -1
            self.rect.y += self.y_vel
            if self.rect.bottom < self.up_elevator_y:
                self.state = Set.STOPPED

    # 특정 키 눌릴 때 True
    def check_to_allow_jump(self, keys):
        if not keys[tools.keybinding['jump']]:
            self.allow_jump = True
    def check_to_allow_fireball(self, keys):
        if not keys[tools.keybinding['action']]:
            self.allow_fireball = True

    #정지상태 처리. 키 입력 확인 후 움직임을 0으로.
    def stopped(self, keys, fire_group):
        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)
        
        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0
        
        if keys[tools.keybinding['action']]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)

        if keys[tools.keybinding['down']]:
            self.update_crouch_or_not(True)

        if keys[tools.keybinding['left']]:
            self.facing_right = False
            self.update_crouch_or_not()
            self.state = Set.WALK
        elif keys[tools.keybinding['right']]:
            self.facing_right = True
            self.update_crouch_or_not()
            self.state = Set.WALK
        elif keys[tools.keybinding['jump']]:
            if self.allow_jump:
                self.state = Set.JUMP
                self.y_vel = self.jump_vel
        
        if not keys[tools.keybinding['down']]:
            self.update_crouch_or_not()

    def update_crouch_or_not(self, isDown=False):
        #작은 상태로 ↓ : 숙임
        if not self.big:
            self.crouching = True if isDown else False
            return
        if not isDown and not self.crouching:
            return
        
        #큰 상태로 ↓ : 숙여지며 크기 감소
        self.crouching = True if isDown else False
        #7: 숙인 이미지, 0: 일반 이미지 인덱스
        frame_index = 7 if isDown else 0 
        bottom = self.rect.bottom
        left = self.rect.x
        if self.facing_right:
            self.image = self.right_frames[frame_index]
        else:
            self.image = self.left_frames[frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left
        self.frame_index = frame_index

    def walking(self, keys, fire_group):
        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)

        #프레임 인덱스 0이면 시간 경과별 업데이트(이동 프레임 1~3)
        if self.frame_index == 0:
            self.frame_index += 1
            self.walking_timer = self.current_time
        #게임시간과 이동시간 오차가 애니메이션 속도를 넘어설 경우
        elif (self.current_time - self.walking_timer >
                    self.calculate_animation_speed()):
            #프레임 인덱스 3넘으면 1로 초기화.
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time
        
        
        if keys[tools.keybinding['action']]:
            #가속도 달리기 기준 설정. 사출기 사용 가능하면 사용
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)
        else:
            #가속도 붙이기
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel
        
        #속도 따라 점프의 y속도 조정.
        if keys[tools.keybinding['jump']]:
            if self.allow_jump:
                self.state = Set.JUMP
                if abs(self.x_vel) > 4:
                    self.y_vel = self.jump_vel - 0.5
                else:
                    self.y_vel = self.jump_vel
                
        #왼쪽 전환. 속도 0 이상이면 급커브 이미지[5] 사용.
        if keys[tools.keybinding['left']]:
            self.facing_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = Set.SMALL_TURNAROUND
            
            #왼쪽이라 isNegative=True
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel, True)
        
        #오른쪽 전환
        elif keys[tools.keybinding['right']]:
            self.facing_right = True
            if self.x_vel < 0:
                self.frame_index = 5
                self.x_accel = Set.SMALL_TURNAROUND
            
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel)
        
        #눌린 키가 없을 때. x속도 있으면 감속.
        else:
            if self.facing_right:
                if self.x_vel > 0:
                    self.x_vel -= self.x_accel
                else:
                    self.x_vel = 0
                    self.state = Set.STOPPED
            else:
                if self.x_vel < 0:
                    self.x_vel += self.x_accel
                else:
                    self.x_vel = 0
                    self.state = Set.STOPPED

    def jumping(self, keys, fire_group):
        self.check_to_allow_fireball(keys)
        #추가 점프 허가 X
        self.allow_jump = False
        #점프 프레임 인덱스 4
        self.frame_index = 4
        self.gravity = Set.JUMP_GRAVITY
        self.y_vel += self.gravity
        
        #하향상태. 최속보다 느리면 점프중력 없애기.
        if self.y_vel >= 0 and self.y_vel < self.max_y_vel:
            self.gravity = Set.GRAVITY
            self.state = Set.FALL

        if keys[tools.keybinding['right']]:
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel)
        elif keys[tools.keybinding['left']]:
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel, True)
        
        #점프키 눌리지 않으면 중력 초기화+하강상태
        if not keys[tools.keybinding['jump']]:
            self.gravity = Set.GRAVITY
            self.state = Set.FALL
        
        if keys[tools.keybinding['action']]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)


    def falling(self, keys, fire_group):
        self.check_to_allow_fireball(keys)
        #일반 중력가속도(gravity) 적용.
        self.y_vel = self.cal_vel(self.y_vel, self.max_y_vel, self.gravity)
        
        if keys[tools.keybinding['right']]:
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel)
        elif keys[tools.keybinding['left']]:
            self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel, True)
        
        if keys[tools.keybinding['action']]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)
    
    #사망 직전 짧은 점프
    def jumping_to_death(self):
        #사망시간 기록
        if self.death_timer == 0:
            self.death_timer = self.current_time
        # 0.5초 후 추락.
        elif (self.current_time - self.death_timer) > 500:
            self.rect.y += self.y_vel
            self.y_vel += self.gravity

    #속도 계산. 
    def cal_vel(self, vel, max_vel, accel, isNegative=False):
        """ ( max_vel && accel ) > 0 """
        if isNegative:
            new_vel = vel * -1
        else:
            new_vel = vel
        #최대 속도까지 가속도 추가. 넘어가면 고정.
        if (new_vel + accel) < max_vel:
            new_vel += accel
        else:
            new_vel = max_vel
            
        if isNegative:
            return new_vel * -1
        else:
            return new_vel

    def calculate_animation_speed(self):
        if self.x_vel == 0:
            animation_speed = 130
        #우측 이동. 속도 증가할수록 빠른 애니메이션
        elif self.x_vel > 0:
            animation_speed = 130 - (self.x_vel * 13)
        #좌측 이동. 속도 증가할수록 빠른 애니메이션(속도 음수)
        else:
            animation_speed = 130 - (self.x_vel * 13 * -1)
        return animation_speed

    def shoot_fireball(self, powerup_group):
        #0.3초간 사출기 연속사용 방지.
        if (self.current_time - self.last_fireball_time) > 300:
            self.allow_fireball = False
            #사출기 생성
            powerup_group.add(powerup.FireBall(self.rect.right, 
                            self.rect.y, self.facing_right))
            self.last_fireball_time = self.current_time
            self.frame_index = 6

    def flag_pole_sliding(self):
        self.state = Set.FLAGPOLE
        self.x_vel = 0
        self.y_vel = 5

        #타이머 시작. 높이 별 프레임 설정
        if self.flagpole_timer == 0:
            self.flagpole_timer = self.current_time
        elif self.rect.bottom < 493:
            if (self.current_time - self.flagpole_timer) < 65:
                self.frame_index = 9
            elif (self.current_time - self.flagpole_timer) < 130:
                self.frame_index = 10
            else:
                self.flagpole_timer = self.current_time
        elif self.rect.bottom >= 493:
            self.frame_index = 10

    #walking과 유사한 형태
    def walking_auto(self):
        self.max_x_vel = 5
        self.x_accel = self.walk_accel
        
        self.x_vel = self.cal_vel(self.x_vel, self.max_x_vel, self.x_accel)
        
        if (self.walking_timer == 0 or (self.current_time - self.walking_timer) > 200):
            self.walking_timer = self.current_time
        elif (self.current_time - self.walking_timer >
                    self.calculate_animation_speed()):
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time

    def changing_to_big(self):
        #단계별 경과 시간
        timer_list = [135, 200, 365, 430, 495, 560, 625, 690, 755, 820, 885]
        #단계별 크기
        size_list = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2]
        frames = [(self.small_normal_frames, 0), (self.small_normal_frames, 7),
                    (self.big_normal_frames, 0)]
        if self.transition_timer == 0:
            self.big = True
            self.change_index = 0
            self.transition_timer = self.current_time
        elif (self.current_time - self.transition_timer) > timer_list[self.change_index]:
            if (self.change_index + 1) >= len(timer_list):
                #커지기 
                self.transition_timer = 0
                self.set_player_image(self.big_normal_frames, 0)
                self.state = Set.WALK
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames
            else:
                #단계에 맞는 프레임 가져오기
                frame, frame_index = frames[size_list[self.change_index]]
                self.set_player_image(frame, frame_index)
            self.change_index += 1

    #changing_to_big과 유사한 형태
    def changing_to_small(self):
        timer_list = [265, 330, 395, 460, 525, 590, 655, 720, 785, 850, 915]
        # 0이 크고 2가 작은 것!
        size_list = [0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
        frames = [(self.big_normal_frames, 4), (self.big_normal_frames, 8),
                    (self.small_normal_frames, 8)]

        if self.transition_timer == 0:
            self.change_index = 0
            self.transition_timer = self.current_time
        elif (self.current_time - self.transition_timer) > timer_list[self.change_index]:
            if (self.change_index + 1) >= len(timer_list):
                #작아지기
                self.transition_timer = 0
                self.set_player_image(self.small_normal_frames, 0)
                self.state = Set.WALK
                self.big = False
                self.fire = False
                self.hurt_invincible = True #피격 시 일시적 투명화
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames
            else:
                frame, frame_index = frames[size_list[self.change_index]]
                self.set_player_image(frame, frame_index)
            self.change_index += 1

    def changing_to_fire(self):
        timer_list = [65, 195, 260, 325, 390, 455, 520, 585, 650, 715, 780, 845, 910, 975]
        # 깜빡깜빡 색상변화
        size_list = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1]
        frames = [(self.big_fire_frames, 3), (self.big_normal_frames, 3),
                    (self.big_fire_frames, 3), (self.big_normal_frames, 3)]
                    
        if self.transition_timer == 0:
            self.change_index = 0
            self.transition_timer = self.current_time
        elif (self.current_time - self.transition_timer) > timer_list[self.change_index]:
            if (self.change_index + 1) >= len(timer_list):
                #강화
                self.transition_timer = 0
                self.set_player_image(self.big_fire_frames, 3)
                self.fire = True
                self.state = Set.WALK
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames
            else:
                frame, frame_index = frames[size_list[self.change_index]]
                self.set_player_image(frame, frame_index)
            self.change_index += 1

    #플레이어 이미지 설정
    def set_player_image(self, frames, frame_index):
        self.frame_index = frame_index
        if self.facing_right:
            self.right_frames = frames[0]
            self.image = frames[0][frame_index]
        else:
            self.left_frames = frames[1]
            self.image = frames[1][frame_index]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    #피격 시 무적화(투명도 조절) check_if_invincible과 유사한 형태
    def check_if_hurt_invincible(self):
        #무적 상태
        if self.hurt_invincible:
            if self.hurt_invincible_timer == 0:
                self.hurt_invincible_timer = self.current_time
                self.hurt_invincible_timer2 = self.current_time
            elif (self.current_time - self.hurt_invincible_timer) < 2000:
                if (self.current_time - self.hurt_invincible_timer2) < 35:
                    self.image.set_alpha(0)
                elif (self.current_time - self.hurt_invincible_timer2) < 70:
                    self.image.set_alpha(255)
                    self.hurt_invincible_timer2 = self.current_time
            else:
                self.hurt_invincible = False
                self.hurt_invincible_timer = 0
                for frames in self.all_images:
                    for image in frames:
                        image.set_alpha(255)

    def check_if_invincible(self):
        if self.invincible:
            #처음으로 무적 상태 되었을 때 실행
            if self.invincible_timer == 0:
                self.invincible_timer = self.current_time #무적 상태 시작 시간 기록
                self.invincible_timer2 = self.current_time #투명도 변경 타이밍 제어
            #10초간 투명도 조절 -> 깜박임 효과.
            elif (self.current_time - self.invincible_timer) < 10000:
                if (self.current_time - self.invincible_timer2) < 35:
                    self.image.set_alpha(0)
                elif (self.current_time - self.invincible_timer2) < 70:
                    self.image.set_alpha(255)
                    self.invincible_timer2 = self.current_time
            #이후 2초간 깜박임 효과 (텀 길어짐)
            elif (self.current_time - self.invincible_timer) < 12000:
                if (self.current_time - self.invincible_timer2) < 100:
                    self.image.set_alpha(0)
                elif (self.current_time - self.invincible_timer2) < 200:
                    self.image.set_alpha(255)
                    self.invincible_timer2 = self.current_time
            #무적 상태 종료.
            else:
                self.invincible = False
                self.invincible_timer = 0
                for frames in self.all_images:
                    for image in frames:
                        image.set_alpha(255)

    #방향에 따른 프레임 업데이트
    def animation(self):
        if self.facing_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    #사망 직전 점프 시 호출. 여기서 점프 후 death_jump()에서 낙하
    def start_death_jump(self, game_info):
        self.dead = True
        self.y_vel = -15
        self.gravity = .5
        self.frame_index = 6
        self.state = Set.DEATH_JUMP