from .. import tools
from .. import Setting as Set
from ..components import info

class LoadScreen(tools.State):
    def __init__(self):
        tools.State.__init__(self) 
        #self.start_time,current_time = 0.0 self.done = False self.next = None self.persist = {}
        self.time_list = [2400, 2600, 2635]
        
    def startup(self, current_time, persist):
        self.start_time = current_time
        self.persist = persist
        self.game_info = self.persist
        self.next = self.set_next_state()
        
        info_state = self.set_info_state()
        self.overhead_info = info.Info(self.game_info, info_state)
    
    def set_next_state(self):
        return Set.LEVEL
    
    def set_info_state(self):
        return Set.LOAD_SCREEN

    def update(self, surface, keys, current_time):
        if (current_time - self.start_time) < self.time_list[0]: #정보 출력
            surface.fill(Set.BLACK)
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        elif (current_time - self.start_time) < self.time_list[1]: #로딩
            surface.fill(Set.BLACK) 
        elif (current_time - self.start_time) < self.time_list[2]: #맵 로딩
            surface.fill((106, 150, 252))
        else:
            self.done = True #시간 초과. 업데이트 종료
            
class GameOver(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)
        self.time_list = [3000, 3200, 3235]

    def set_next_state(self):
        return Set.MAIN_MENU
    
    def set_info_state(self):
        return Set.GAME_OVER

class TimeOut(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)
        self.time_list = [2400, 2600, 2635]

    def set_next_state(self):
        if self.persist[Set.ATTENDENCE] == 0:
            return Set.GAME_OVER
        else:
            return Set.LOAD_SCREEN

    def set_info_state(self):
        return Set.TIME_OUT