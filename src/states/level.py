import os
import json
import pygame as pg
from .. import setup, tools
from .. import Setting as Set
from ..components import info, etc, player, tile, QR_brick, enemy, coin


class Level(tools.State):
    def __init__(self):
        tools.State.__init__(self)
        self.player = None

    def startup(self, current_time, persist):
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[Set.CURRENT_TIME] = current_time
        self.death_timer = 0
        self.castle_timer = 0
        
        #온갖 요소들 초기화
        self.moving_score_list = []
        self.overhead_info = info.Info(self.game_info, Set.LEVEL)
        self.load_map()
        self.setup_background()
        self.setup_maps()
        self.ground_group = self.setup_collide(Set.MAP_GROUND)
        self.step_group = self.setup_collide(Set.MAP_STEP)
        self.setup_elevator()
        self.setup_slider()
        self.setup_static_coin()
        self.setup_tile_and_QR_brick()
        self.setup_player()
        self.setup_enemies()
        self.setup_checkpoints()
        self.setup_flagpole()
        self.setup_sprite_groups()

    # 맵 설계 불러오기. src/data/maps/ level_${단계}.json
    def load_map(self):
        map_file = 'level_' + str(self.game_info[Set.LEVEL_NUM]) + '.json'
        file_path = os.path.join('src', 'data', 'maps', map_file)
        f = open(file_path)
        self.map_data = json.load(f)
        f.close()
        
    
    def setup_background(self):
        #이미지 파일 이름 불러오기
        img_name = self.map_data[Set.MAP_IMAGE]
        self.background = setup.GFX[img_name]
        self.bg_rect = self.background.get_rect()
        #배경 이미지 크기 조절
        self.background = pg.transform.scale(self.background, 
                                    (int(self.bg_rect.width*Set.BACKGROUND_MULTIPLER),
                                    int(self.bg_rect.height*Set.BACKGROUND_MULTIPLER)))
        self.bg_rect = self.background.get_rect()

        #배경 크기에 맞는 표면 생성 후 픽셀 포맷 변환(처리속도 향상)
        self.level = pg.Surface((self.bg_rect.w, self.bg_rect.h)).convert()
        #현 화면 영역. y좌표 = 이미지 하단으로 한 사각영역 출력
        self.viewport = setup.SCREEN.get_rect(bottom=self.bg_rect.bottom)

    #map_data에 'maps'있으면 시작~끝 위치와 시작점 튜플 추가.
    def setup_maps(self):
        self.map_list = []
        if Set.MAP_MAPS in self.map_data:
            for data in self.map_data[Set.MAP_MAPS]:
                self.map_list.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
            self.start_x, self.end_x, self.player_x, self.player_y = self.map_list[0]
        else:
            #기본값
            self.start_x = 0
            self.end_x = self.bg_rect.w
            self.player_x = 110
            self.player_y = Set.GROUND_HEIGHT
        
    def change_map(self, index, type):
        #맵 리스트의 튜플에서 가져오기.
        self.start_x, self.end_x, self.player_x, self.player_y = self.map_list[index]
        self.viewport.x = self.start_x
        #클리어 후 이동 : STOPPED상태
        if type == Set.CHECKPOINT_TYPE_MAP:
            self.player.rect.x = self.viewport.x + self.player_x
            self.player.rect.bottom = self.player_y
            self.player.state = Set.STOPPED
        #엘리베이터 이동 : 엘리베이터 높이가 플레이어만큼 up
        elif type == Set.CHECKPOINT_TYPE_ELEVATOR_UP:
            self.player.rect.x = self.viewport.x + self.player_x
            self.player.rect.bottom = Set.GROUND_HEIGHT
            self.player.state = Set.UP_ELEVATOR
            self.player.up_elevator_y = self.player_y
            
    #충돌체 설정.
    def setup_collide(self, name):
        group = pg.sprite.Group()
        if name in self.map_data:
            for data in self.map_data[name]:
                #데이터에 이름 있으면 충돌체 데이터 추가해 group에 넣고 반환
                group.add(etc.Collider(data['x'], data['y'], 
                        data['width'], data['height'], name))
        return group

    #엘리베이터 : 충돌체와 마찬가지로 group생성. 반환은 x.
    def setup_elevator(self):
        self.elevator_group = pg.sprite.Group()
        #엘리베이터 정보 있다면 객체 초기화 후 그룹 추가.
        if Set.MAP_ELEVATOR in self.map_data:
            for data in self.map_data[Set.MAP_ELEVATOR]:
                self.elevator_group.add(etc.Elevator(data['x'], data['y'],
                    data['width'], data['height'], data['type']))

    #움직임 범위 지정해 슬라이더 스프라이트 그룹 생성
    def setup_slider(self):
        self.slider_group = pg.sprite.Group()
        if Set.MAP_SLIDER in self.map_data:
            for data in self.map_data[Set.MAP_SLIDER]:
                if Set.VELOCITY in data:
                    vel = data[Set.VELOCITY]
                else:
                    vel = 1
                self.slider_group.add(etc.Slider(data['x'], data['y'], data['num'],
                    data['direction'], data['range_start'], data['range_end'], vel))

    #움직임 x 코인
    def setup_static_coin(self):
        self.static_coin_group = pg.sprite.Group()
        if Set.MAP_COIN in self.map_data:
            for data in self.map_data[Set.MAP_COIN]:
                self.static_coin_group.add(coin.StaticCoin(data['x'], data['y']))

    #타일과 상자 스프라이트 그룹 생성
    def setup_tile_and_QR_brick(self):
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.Group()
        self.tile_group = pg.sprite.Group()
        self.tilepiece_group = pg.sprite.Group()

        if Set.MAP_TILE in self.map_data:
            for data in self.map_data[Set.MAP_TILE]:
                tile.create_tile(self.tile_group, data, self)
        
        #타입에 따라 코인, 아이템 그룹 분리
        self.QR_brick_group = pg.sprite.Group()
        if Set.MAP_QR_BRICK in self.map_data:
            for data in self.map_data[Set.MAP_QR_BRICK]:
                if data['type'] == Set.TYPE_COIN:
                    self.QR_brick_group.add(QR_brick.QR_brick(data['x'], data['y'], data['type'], self.coin_group))
                else:
                    self.QR_brick_group.add(QR_brick.QR_brick(data['x'], data['y'], data['type'], self.powerup_group))
            
    #디버깅 상황은 이제 필요 없으니 주석처리
    def setup_player(self):
        #플레이어 없을 때 생성, 이미 있으면 재시작
        if self.player is None:
            self.player = player.Player(self.game_info[Set.PLAYER_NAME])
        else:
            self.player.restart()
        #초기위치 세팅
        self.player.rect.x = self.viewport.x + self.player_x
        self.player.rect.bottom = self.player_y
        #if Set.DEBUG:
        #    self.player.rect.x = self.viewport.x + Set.DEBUG_START_X
        #    self.player.rect.bottom = Set.DEBUG_START_Y
        self.viewport.x = self.player.rect.x - 110

    def setup_enemies(self):
        self.enemy_group_list = []
        index = 0
        for data in self.map_data[Set.MAP_ENEMY]:
            group = pg.sprite.Group()
            #캐릭터 인덱스 정보 아이템으로 가려오기
            for item in data[str(index)]:
                group.add(enemy.create_enemy(item, self))
            self.enemy_group_list.append(group)
            index += 1
            
    #체크포인트 정보 가져와 세팅
    def setup_checkpoints(self):
        self.checkpoint_group = pg.sprite.Group()
        for data in self.map_data[Set.MAP_CHECKPOINT]:
            if Set.ENEMY_GROUPID in data:
                enemy_groupid = data[Set.ENEMY_GROUPID]
            else:
                enemy_groupid = 0
            if Set.MAP_INDEX in data:
                map_index = data[Set.MAP_INDEX]
            else:
                map_index = 0
            self.checkpoint_group.add(etc.Checkpoint(data['x'], data['y'], data['width'], 
                data['height'], data['type'], enemy_groupid, map_index))
    
    def setup_flagpole(self):
        self.flagpole_group = pg.sprite.Group()
        if Set.MAP_FLAGPOLE in self.map_data:
            for data in self.map_data[Set.MAP_FLAGPOLE]:
                if data['type'] == Set.FLAGPOLE_TYPE_FLAG:
                    sprite = etc.Flag(data['x'], data['y'])
                    self.flag = sprite
                elif data['type'] == Set.FLAGPOLE_TYPE_POLE:
                    sprite = etc.Pole(data['x'], data['y'])
                else:
                    sprite = etc.PoleTop(data['x'], data['y'])
                self.flagpole_group.add(sprite)
        
    def setup_sprite_groups(self):
        self.dying_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.shell_group = pg.sprite.Group()
        #발판, 이동 수단 한 그룹으로 묶기
        self.ground_step_elevator_group = pg.sprite.Group(self.ground_group,
                        self.elevator_group, self.step_group, self.slider_group)
        self.player_group = pg.sprite.Group(self.player)
        
    def update(self, surface, keys, current_time):
        self.game_info[Set.CURRENT_TIME] = self.current_time = current_time
        self.handle_states(keys)
        self.draw(surface)
    
    #모든 스프라이트 업데이트
    def handle_states(self, keys):
        self.update_all_sprites(keys)
    
    def update_all_sprites(self, keys):
        #죽으면 업데이트 후 정보 갱신 후 끝
        if self.player.dead:
            self.player.update(keys, self.game_info, self.powerup_group)
            if self.current_time - self.death_timer > 3000:
                self.update_game_info()
                self.done = True
        #도착하면 플레이어+정보+깃발 상태 업데이트 후 끝
        elif self.player.state == Set.IN_END:
            self.player.update(keys, self.game_info, None)
            self.flagpole_group.update()
            if self.current_time - self.castle_timer > 2000:
                self.update_game_info()
                self.done = True
        #일시정지 상태. 플레이어는 업데이트 불필요
        elif self.in_frozen_state():
            self.player.update(keys, self.game_info, None)
            self.check_checkpoints()
            self.update_viewport()
            self.overhead_info.update(self.game_info, self.player)
            for score in self.moving_score_list:
                score.update(self.moving_score_list)
        else:
            self.player.update(keys, self.game_info, self.powerup_group)
            self.flagpole_group.update()
            self.check_checkpoints()
            self.slider_group.update()
            self.static_coin_group.update(self.game_info)
            self.enemy_group.update(self.game_info, self)
            self.shell_group.update(self.game_info, self)
            self.tile_group.update()
            self.QR_brick_group.update(self.game_info)
            self.powerup_group.update(self.game_info, self)
            self.coin_group.update(self.game_info)
            self.tilepiece_group.update()
            self.dying_group.update(self.game_info, self)
            self.update_player_position()
            self.check_for_player_death()
            self.update_viewport()
            self.overhead_info.update(self.game_info, self.player)
            for score in self.moving_score_list:
                score.update(self.moving_score_list)
    
    def check_checkpoints(self):
        #pg.sprite.spritecollideany() : sprite와 충돌하는 그룹 내 스프라이트 반환
        checkpoint = pg.sprite.spritecollideany(self.player, self.checkpoint_group)
        
        if checkpoint:
            if checkpoint.type == Set.CHECKPOINT_TYPE_ENEMY:
                group = self.enemy_group_list[checkpoint.enemy_groupid]
                self.enemy_group.add(group)
            elif checkpoint.type == Set.CHECKPOINT_TYPE_FLAG:
                self.player.state = Set.FLAGPOLE
                if self.player.rect.bottom < self.flag.rect.y:
                    self.player.rect.bottom = self.flag.rect.y
                self.flag.state = Set.SLIDE_DOWN
                self.update_flag_score()
            elif checkpoint.type == Set.CHECKPOINT_TYPE_END:
                self.player.state = Set.IN_END
                self.player.x_vel = 0
                self.castle_timer = self.current_time
                self.flagpole_group.add(etc.CastleFlag(8746, 336))
            elif (checkpoint.type == Set.CHECKPOINT_TYPE_COFFEE and
                    self.player.y_vel < 0):
                coffee_QR_brick = QR_brick.QR_brick(checkpoint.rect.x, checkpoint.rect.bottom - 40,
                                Set.TYPE_LIFECOFFEE, self.powerup_group)
                coffee_QR_brick.start_bump(self.moving_score_list)
                self.QR_brick_group.add(coffee_QR_brick)
                self.player.y_vel = 7
                self.player.rect.y = coffee_QR_brick.rect.bottom
                self.player.state = Set.FALL
            elif checkpoint.type == Set.CHECKPOINT_TYPE_ELEVATOR:
                self.player.state = Set.WALK_AUTO
            elif checkpoint.type == Set.CHECKPOINT_TYPE_ELEVATOR_UP:
                self.change_map(checkpoint.map_index, checkpoint.type)
            elif checkpoint.type == Set.CHECKPOINT_TYPE_MAP:
                self.change_map(checkpoint.map_index, checkpoint.type)
            elif checkpoint.type == Set.CHECKPOINT_TYPE_BOSS:
                self.player.state = Set.WALK_AUTO
            checkpoint.kill()

    def update_flag_score(self):
        base_y = Set.GROUND_HEIGHT - 80
        
        y_score_list = [(base_y, 100), (base_y-120, 400),
                    (base_y-200, 800), (base_y-320, 2000),
                    (0, 5000)]
        for y, score in y_score_list:
            if self.player.rect.y > y:
                self.update_score(score, self.flag)
                break
        
    def update_player_position(self):
        if self.player.state == Set.UP_ELEVATOR:
            return

        self.player.rect.x += round(self.player.x_vel)
        if self.player.rect.x < self.start_x:
            self.player.rect.x = self.start_x
        elif self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x
        self.check_player_x_collisions()
        
        if not self.player.dead:
            self.player.rect.y += round(self.player.y_vel)
            self.check_player_y_collisions()
    
    def check_player_x_collisions(self):
        ground_step_elevator = pg.sprite.spritecollideany(self.player, self.ground_step_elevator_group)
        tile = pg.sprite.spritecollideany(self.player, self.tile_group)
        QR_brick = pg.sprite.spritecollideany(self.player, self.QR_brick_group)
        enemy = pg.sprite.spritecollideany(self.player, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.player, self.shell_group)
        powerup = pg.sprite.spritecollideany(self.player, self.powerup_group)
        coin = pg.sprite.spritecollideany(self.player, self.static_coin_group)

        #플레이어와 충돌한 그룹에 따른 작동 구분
        if QR_brick:
            self.adjust_player_for_x_collisions(QR_brick)
        elif tile:
            self.adjust_player_for_x_collisions(tile)
        elif ground_step_elevator:
            if (ground_step_elevator.name == Set.MAP_ELEVATOR and
                ground_step_elevator.type == Set.ELEVATOR_TYPE_HORIZONTAL):
                return
            self.adjust_player_for_x_collisions(ground_step_elevator)
        elif powerup:
            if powerup.type == Set.TYPE_COFFEE:
                self.update_score(1000, powerup, 0)
                if not self.player.big:
                    self.player.y_vel = -1
                    self.player.state = Set.SMALL_TO_BIG
            elif powerup.type == Set.TYPE_HOT6:
                self.update_score(1000, powerup, 0)
                if not self.player.big:
                    self.player.state = Set.SMALL_TO_BIG
                elif self.player.big and not self.player.fire:
                    self.player.state = Set.BIG_TO_FIRE
            elif powerup.type == Set.TYPE_STAR:
                self.update_score(1000, powerup, 0)
                self.player.invincible = True
            elif powerup.type == Set.TYPE_LIFECOFFEE:
                self.update_score(500, powerup, 0)
                self.game_info[Set.ATTENDENCE] += 1
            if powerup.type != Set.TYPE_FIREBALL:
                powerup.kill()
        elif enemy:
            if self.player.invincible:
                self.update_score(100, enemy, 0)
                self.move_to_dying_group(self.enemy_group, enemy)
                direction = Set.RIGHT if self.player.facing_right else Set.LEFT
                enemy.start_death_jump(direction)
            elif self.player.hurt_invincible:
                pass
            elif self.player.big:
                self.player.y_vel = -1
                self.player.state = Set.BIG_TO_SMALL
            else:
                self.player.start_death_jump(self.game_info)
                self.death_timer = self.current_time
        elif shell:
            if shell.state == Set.WORK_SLIDE:
                if self.player.invincible:
                    self.update_score(200, shell, 0)
                    self.move_to_dying_group(self.shell_group, shell)
                    direction = Set.RIGHT if self.player.facing_right else Set.LEFT
                    shell.start_death_jump(direction)
                elif self.player.hurt_invincible:
                    pass
                elif self.player.big:
                    self.player.y_vel = -1
                    self.player.state = Set.BIG_TO_SMALL
                else:
                    self.player.start_death_jump(self.game_info)
                    self.death_timer = self.current_time
            else:
                self.update_score(400, shell, 0)
                if self.player.rect.x < shell.rect.x:
                    self.player.rect.left = shell.rect.x 
                    shell.direction = Set.RIGHT
                    shell.x_vel = 10
                else:
                    self.player.rect.x = shell.rect.left
                    shell.direction = Set.LEFT
                    shell.x_vel = -10
                shell.rect.x += shell.x_vel * 4
                shell.state = Set.WORK_SLIDE
        elif coin:
            self.update_score(100, coin, 1)
            coin.kill()

    def adjust_player_for_x_collisions(self, collider):
        #작업 미수행
        if collider.name == Set.MAP_SLIDER:
            return
        #겹침방지
        if self.player.rect.x < collider.rect.x:
            self.player.rect.right = collider.rect.left
        else:
            self.player.rect.left = collider.rect.right
        #정지
        self.player.x_vel = 0

    def check_player_y_collisions(self):
        ground_step_elevator = pg.sprite.spritecollideany(self.player, self.ground_step_elevator_group)
        enemy = pg.sprite.spritecollideany(self.player, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.player, self.shell_group)

        if self.player.rect.bottom < Set.GROUND_HEIGHT:
            tile = pg.sprite.spritecollideany(self.player, self.tile_group)
            QR_brick = pg.sprite.spritecollideany(self.player, self.QR_brick_group)
            tile, QR_brick = self.prevent_collision_conflict(tile, QR_brick)
        #공중에 있지 않으면 타일과 상자 충돌 검사는 불필요
        else:
            tile, QR_brick = False, False

        if QR_brick:
            self.adjust_player_for_y_collisions(QR_brick)
        elif tile:
            self.adjust_player_for_y_collisions(tile)
        elif ground_step_elevator:
            self.adjust_player_for_y_collisions(ground_step_elevator)
        elif enemy:
            if self.player.invincible:
                self.update_score(100, enemy, 0)
                self.move_to_dying_group(self.enemy_group, enemy)
                direction = Set.RIGHT if self.player.facing_right else Set.LEFT
                enemy.start_death_jump(direction)
            #부산물, 장애물은 충돌검사 확인 불필요.
            elif (
                enemy.name == Set.FIRESTICK or
                enemy.name == Set.FIRE_PROF or
                enemy.name == Set.FIRE):
                pass
            elif self.player.y_vel > 0:
                self.update_score(100, enemy, 0)
                enemy.state = Set.JUMPED_ON
                if enemy.name == Set.BOO:
                    self.move_to_dying_group(self.enemy_group, enemy)
                elif enemy.name == Set.PROF or enemy.name == Set.FLY_PROF:
                    self.enemy_group.remove(enemy)
                    self.shell_group.add(enemy)

                self.player.rect.bottom = enemy.rect.top
                self.player.state = Set.JUMP
                self.player.y_vel = -7
        elif shell:
            if self.player.y_vel > 0:
                if shell.state != Set.WORK_SLIDE:
                    shell.state = Set.WORK_SLIDE
                    if self.player.rect.centerx < shell.rect.centerx:
                        shell.direction = Set.RIGHT
                        shell.rect.left = self.player.rect.right + 5
                    else:
                        shell.direction = Set.LEFT
                        shell.rect.right = self.player.rect.left - 5
        self.check_is_falling(self.player)
        self.check_if_player_on_IN_elevator()
    
    def prevent_collision_conflict(self, sprite1, sprite2):
        #가까운 거리의 충돌을 우선시
        if sprite1 and sprite2:
            distance1 = abs(self.player.rect.centerx - sprite1.rect.centerx)
            distance2 = abs(self.player.rect.centerx - sprite2.rect.centerx)
            if distance1 < distance2:
                sprite2 = False
            else:
                sprite1 = False
        return sprite1, sprite2
        
    def adjust_player_for_y_collisions(self, sprite):
        #플레이어가 스프라이트 아래일때 한정.
        if self.player.rect.top > sprite.rect.top:
            #타일 위 적이 있다면 처리.
            if sprite.name == Set.MAP_TILE:
                self.check_if_enemy_on_tile_QR_brick(sprite)
                if sprite.state == Set.STAYED:
                    #일반형 + 큰 플레이어 = 파괴
                    if self.player.big and sprite.type == Set.TYPE_NONE:
                        sprite.change_to_piece(self.dying_group)
                    #코인 있으면 업데이트 + 튕기기
                    else:
                        if sprite.type == Set.TYPE_COIN:
                            self.update_score(200, sprite, 1)
                        sprite.start_bump(self.moving_score_list)
            elif sprite.name == Set.MAP_QR_BRICK:
                self.check_if_enemy_on_tile_QR_brick(sprite)
                if sprite.state == Set.STAYED:
                    if sprite.type == Set.TYPE_COIN:
                        self.update_score(200, sprite, 1)
                    sprite.start_bump(self.moving_score_list)
            #수평 엘리베이터 = 충돌판정 종료.
            elif (sprite.name == Set.MAP_ELEVATOR and
                sprite.type == Set.ELEVATOR_TYPE_HORIZONTAL):
                return
            
            self.player.y_vel = 7
            self.player.rect.top = sprite.rect.bottom
            self.player.state = Set.FALL
            
        #위에서 아래로의 충돌
        else:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            if self.player.state == Set.FLAGPOLE:
                self.player.state = Set.WALK_AUTO
            elif self.player.state == Set.END_OF_LEVEL_FALL:
                self.player.state = Set.WALK_AUTO
            #도착지점이 아닌 이상 자동걷기 X
            else:
                self.player.state = Set.WALK
    
    def check_if_enemy_on_tile_QR_brick(self, tile):
        #충돌 물체 위로 5 이동
        tile.rect.y -= 5
        #충돌한 적 스프라이트 탐색
        enemy = pg.sprite.spritecollideany(tile, self.enemy_group)
        if enemy:
            self.update_score(100, enemy, 0)
            self.move_to_dying_group(self.enemy_group, enemy)
            #타격 위치에 따른 적 방향 전환
            if self.player.rect.centerx > tile.rect.centerx:
                direction = Set.RIGHT
            else:
                direction = Set.LEFT
            enemy.start_death_jump(direction)
        tile.rect.y += 5

    #상태 변화 시 일시정지상태 확인
    def in_frozen_state(self):
        if (self.player.state == Set.SMALL_TO_BIG or
            self.player.state == Set.BIG_TO_SMALL or
            self.player.state == Set.BIG_TO_FIRE or
            self.player.state == Set.DEATH_JUMP or
            self.player.state == Set.DOWN_ELEVATOR or
            self.player.state == Set.UP_ELEVATOR):
            return True
        else:
            return False

    def check_is_falling(self, sprite):
        sprite.rect.y += 1 #충돌 기준범위(박스) 아래로 1 이동
        check_group = pg.sprite.Group(self.ground_step_elevator_group,
                            self.tile_group, self.QR_brick_group)
        
        #충돌 여하와 상태 따라 플레이어 상태 결정
        if pg.sprite.spritecollideany(sprite, check_group) is None:
            if (sprite.state == Set.WALK_AUTO or
                sprite.state == Set.END_OF_LEVEL_FALL):
                sprite.state = Set.END_OF_LEVEL_FALL
            elif (sprite.state != Set.JUMP and 
                sprite.state != Set.FLAGPOLE and
                not self.in_frozen_state()):
                sprite.state = Set.FALL
        #충돌기준범위 복구
        sprite.rect.y -= 1
    
    #사망 확인. 화면 높이를 넘어서는 행위도 사망으로 간주.
    def check_for_player_death(self):
        if (self.player.rect.y > Set.SCREEN_HEIGHT or
            self.overhead_info.time <= 0):
            self.player.start_death_jump(self.game_info)
            self.death_timer = self.current_time

    def check_if_player_on_IN_elevator(self):
        #이동 가능여부 확인
        self.player.rect.y += 1
        elevator = pg.sprite.spritecollideany(self.player, self.elevator_group)
        #엘리베이터 존재하고 이동 가능 상태일 경우
        if elevator and elevator.type == Set.ELEVATOR_TYPE_IN:
            #숙인 상태로 엘리베이터의 중간에 섰을 때.
            if (self.player.crouching and
                self.player.rect.x < elevator.rect.centerx and
                self.player.rect.right > elevator.rect.centerx):
                self.player.state = Set.DOWN_ELEVATOR
        self.player.rect.y -= 1
        
    def update_game_info(self):
        if self.player.dead:
            self.persist[Set.ATTENDENCE] -= 1

        if self.persist[Set.ATTENDENCE] == 0:
            self.next = Set.GAME_OVER
        elif self.overhead_info.time == 0:
            self.next = Set.TIME_OUT
        elif self.player.dead:
            self.next = Set.LOAD_SCREEN
        else:
            self.game_info[Set.LEVEL_NUM] += 1
            self.next = Set.LOAD_SCREEN

    def update_viewport(self):
        #화면 내 맵 영역 3등분, 플레이어 중심값 지정
        third = self.viewport.x + self.viewport.w//3
        player_center = self.player.rect.centerx
        
        #오른쪽 이동 중(끝 지점 아닌 상태)
        if (self.player.x_vel > 0 and 
            player_center >= third and
            self.viewport.right < self.end_x):
            self.viewport.x += round(self.player.x_vel) #이동속도 반올림 해 시야 이동
        elif self.player.x_vel < 0 and self.viewport.x > self.start_x:
            self.viewport.x += round(self.player.x_vel)
    
    def move_to_dying_group(self, group, sprite):
        group.remove(sprite)
        self.dying_group.add(sprite)
        
    def update_score(self, score, sprite, coin_num=0):
        self.game_info[Set.SCORE] += score
        self.game_info[Set.TOTAL_COIN] += coin_num
        
        #점수 출력 효과 
        x = sprite.rect.x
        y = sprite.rect.y - 10
        self.moving_score_list.append(etc.Score(x, y, score))

    def draw(self, surface):
        #시야 영역 내 배경 이미지 draw
        self.level.blit(self.background, self.viewport, self.viewport)
        self.powerup_group.draw(self.level)
        self.tile_group.draw(self.level)
        self.QR_brick_group.draw(self.level)
        self.coin_group.draw(self.level)
        self.dying_group.draw(self.level)
        self.tilepiece_group.draw(self.level)
        self.flagpole_group.draw(self.level)
        self.shell_group.draw(self.level)
        self.enemy_group.draw(self.level)
        self.player_group.draw(self.level)
        self.static_coin_group.draw(self.level)
        self.slider_group.draw(self.level)
        self.elevator_group.draw(self.level)
        
        #점수 출력 효과 draw
        for score in self.moving_score_list:
            score.draw(self.level)
        #if Set.DEBUG:
        #    self.ground_step_elevator_group.draw(self.level)
        #    self.checkpoint_group.draw(self.level)

        #level표면 시야범위만큼 draw / 상단표시정보 surface에 draw
        surface.blit(self.level, (0,0), self.viewport)
        self.overhead_info.draw(surface)