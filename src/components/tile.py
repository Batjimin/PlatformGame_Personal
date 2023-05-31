from .. import setup
from .. import Setting as Set
from . import coin, etc, powerup

def create_tile(tile_group, item, level):
    if Set.COLOR in item:
        color = item[Set.COLOR]
    else:
        color = Set.COLOR_TYPE_ORANGE

    x, y, type = item['x'], item['y'], item['type'] #item 딕셔너리에서 가져오기
    if type == Set.TYPE_COIN:
        tile_group.add(Tile(x, y, type, 
                    color, level.coin_group)) #코인 타입은 코인그룹
    elif (type == Set.TYPE_STAR or
        type == Set.TYPE_HOT6 or
        type == Set.TYPE_LIFECOFFEE):
        tile_group.add(Tile(x, y, type,
                    color, level.powerup_group)) #아이템 타입은 powerup그룹
    else:
        if Set.TILE_NUM in item:
            create_tile_list(tile_group, item[Set.TILE_NUM], x, y, type,
                        color, item['direction']) #dic에 타일 수 있으면 생성
        else:
            tile_group.add(Tile(x, y, type, color)) #없으면 타일그룹에 추가.
            
#방향 따라서 num개의 타일 생성.          
def create_tile_list(tile_group, num, x, y, type, color, direction):
    size = 43   #(16*Set.TILE_SIZE_MULTIPLIER) == 43
    tmp_x, tmp_y = x, y
    for i in range(num):
        if direction == Set.VERTICAL: #세로방향 생성(좌표)
            tmp_y = y + i * size
        else: #가로방향 생성(좌표)
            tmp_x = x + i * size
        tile_group.add(Tile(tmp_x, tmp_y, type, color)) #타일 그룹 추가
        
class Tile(etc.Etc): #etc.Etc클래스 상속
    def __init__(self, x, y, type, color=Set.ORANGE, group=None, name=Set.MAP_TILE):
        orange_rect = [(16, 0, 16, 16), (432, 0, 16, 16)]
        green_rect = [(208, 32, 16, 16), (48, 32, 16, 16)]
        if color == Set.COLOR_TYPE_ORANGE:
            frame_rect = orange_rect
        else:
            frame_rect = green_rect
        #class Etc: def __init__(self, x, y, sheet, image_rect_list, scale)
        etc.Etc.__init__(self, x, y, setup.GFX['tile_set'],
                        frame_rect, Set.TILE_SIZE_MULTIPLIER)

        self.rest_height = y
        self.state = Set.STAYED
        self.y_vel = 0
        self.gravity = 1.2
        self.type = type
        if self.type == Set.TYPE_COIN:
            self.coin_num = 10
        else:
            self.coin_num = 0
        self.group = group
        self.name = name
    
    def update(self):
        if self.state == Set.BUMPED:
            self.bumped()
    
    def bumped(self):
        self.rect.y += self.y_vel #내려오기
        self.y_vel += self.gravity #중력으로 감속 걸기
        
        if self.rect.y >= self.rest_height:  #현위치 >= 디폴트 위치
            self.rect.y = self.rest_height   #너무 내려오면 위치고정
            if self.type == Set.TYPE_COIN:
                if self.coin_num > 0:
                    self.state = Set.STAYED
                else:
                    self.state = Set.OPENED
            elif self.type == Set.TYPE_STAR:
                self.state = Set.OPENED
                self.group.add(powerup.Star(self.rect.centerx, self.rest_height))
            elif self.type == Set.TYPE_HOT6:
                self.state = Set.OPENED
                self.group.add(powerup.Hot6(self.rect.centerx, self.rest_height))
            elif self.type == Set.TYPE_LIFECOFFEE:
                self.state = Set.OPENED
                self.group.add(powerup.LifeCoffee(self.rect.centerx, self.rest_height))
            else:
                self.state = Set.STAYED
            #OPENED - 빈 상태(민무늬). STAYED - 그 상태 그대로.
            
    def start_bump(self, score_group): #충돌 순간의 동작
        self.y_vel -= 7 #튀어오르기
        
        if self.type == Set.TYPE_COIN:
            if self.coin_num > 0:
                self.group.add(coin.Coin(self.rect.centerx, self.rect.y, score_group))
                self.coin_num -= 1
                if self.coin_num == 0:
                    self.frame_index = 1 #프레임 초기화 후 그 프레임으로 이미지 업데이트
                    self.image = self.frames[self.frame_index]
        elif (self.type == Set.TYPE_STAR or 
            self.type == Set.TYPE_HOT6 or 
            self.type == Set.TYPE_LIFECOFFEE):
            self.frame_index = 1
            self.image = self.frames[self.frame_index]
        
        self.state = Set.BUMPED
    
    def change_to_piece(self, group):
        #4분할
        arg_list = [(self.rect.x, self.rect.y - (self.rect.height/2), -2, -12),
                    (self.rect.right, self.rect.y - (self.rect.height/2), 2, -12),
                    (self.rect.x, self.rect.y, -2, -6),
                    (self.rect.right, self.rect.y, 2, -6)]
        
        #인자로 객체 생성 후 현 타일 삭제
        for arg in arg_list:
            group.add(TilePiece(*arg))
        self.kill()
        
class TilePiece(etc.Etc): #Etc클래스 상속
    def __init__(self, x, y, x_vel, y_vel):
        etc.Etc.__init__(self, x, y, setup.GFX['tile_set'],
            [(68, 20, 8, 8)], Set.TILE_SIZE_MULTIPLIER) #이미지 세팅
        self.x_vel = x_vel 
        self.y_vel = y_vel
        self.gravity = 0.8
    
    def update(self, *args): #속도 따라 이동하고 아래 가속도 적용
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if self.rect.y > Set.SCREEN_HEIGHT: #화면 벗어남
            self.kill()
    