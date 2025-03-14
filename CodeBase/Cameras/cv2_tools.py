from dataclasses import dataclass
from time import time
from typing import Tuple
import cv2

#TODO Separate into a general purpose timer object and a frame timer object
class FrameTime:
    def __init__(self, name: str = 'Default', silent: bool = True) -> str:
        self.start_time:float | None = None
        self.current_time:float | None = None
        self.last_time:float | None = None
        self.delta_time:float | None = None
        self.name:str = name
        self.silent:bool = silent
        self.avg_fps:list[float] | None = None

    def start_timing(self) -> None:
        self.start:float = time()
        self.current_time:float = self.start
        self.last_time:float = self.start
        self.delta_time:float = 0
        self.avg_fps = []

    def tic(self) -> float:
        '''Returns the delta time between last tic and toc calls'''
        self.current_time = time()
        self.delta_time: float = self.current_time - self.last_time 
        # print(self.delta_time)
        # print('tic')
        self.last_time = self.current_time
        return self.delta_time 

    def toc(self) -> None:
        self.last_time = time()
        # print('toc')

    def calc_fps(self) -> str:
        if self.delta_time == 0:
            return ' '
        fps = 1/(self.delta_time)
        self.avg_fps.append(fps)
        
        if len(self.avg_fps) > 20:
            self.avg_fps.pop(0)

        fps = sum(self.avg_fps)/len(self.avg_fps)

        if not self.silent:
            print(f'{self.name} fps: {fps:.0f}')

        return f'{fps:.0f}'

    def calc_waitkey_time(self, fps) -> int:
        '''Returns waitkey time as an int in milliseconds'''
        # print(int(((1/fps)-self.delta_time)*1000))
        # if self.delta_time is None:
        fps_delta_diff = int(((1/fps)-self.delta_time)*1000)
        if fps_delta_diff <= 0:
            return 1

        return fps_delta_diff
    
@dataclass
class WindowParameters:
    status: bool = True
    window_size: tuple = (480, 800) #y, x
    window_location: tuple = (0, 0)
    frames: int = 600 #used for animations
    fps: float = 30.0 #adjust to get best results
    fps_display_flag: bool = False
    fps_display_color: tuple = (255,255, 0)
    frame_time: FrameTime | None = None
    fullscreen: bool = False
    
    def __init__(self, 
                 window_name: str = 'Default Frame', 
                 window_location: Tuple[int,int] = (0,0)):
        self.window_name:str = window_name
        self.window_location = window_location
        self.frame_time: FrameTime = FrameTime(self.window_name)
        # print(self.window_name+'_STARTED')

    def move_to_top(self):
        move_to_top(self.window_name)

    def set_window_location(self, loc: Tuple[int, int] | None = None):
        if loc is not None:
            self.window_location = loc
        set_window_location(self.window_name, self.window_location)

    def call_fps(self, display_img):
        if self.fps_display_flag:
            call_fps(self, display_img)

def call_fps(w: WindowParameters, display_img):  
    cv2.putText(img = display_img,
                text = w.frame_time.calc_fps(),
                org = (w.window_size[0]+100,30),
                fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                fontScale = 1,
                color = w.fps_display_color,
                thickness = 2,
                lineType = cv2.LINE_AA,
                )

def set_window_location(window_name: str, window_location: Tuple[int, int]):
    rect = find_window_properties(window_name)
    if rect is None:
        return
    if (rect[0], rect[1]) is not window_location:
        cv2.moveWindow(window_name,*window_location)

def find_window_properties(window_name: str):
    if check_set(window_name, -1):
        return cv2.getWindowImageRect(window_name)

def move_to_top(window_name: str):
    if check_set(window_name):
        try:
            cv2.setWindowProperty(window_name,cv2.WND_PROP_TOPMOST,1.0)
        except:
            pass

def check_set(window_name: str, wait_time: float = 1.0):
    '''Returns a bool that checks if a window is visible within a set amount of time'''
    if wait_time < 0:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
            return True
        return False

    start_time = time()
    while time() - start_time < wait_time:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
            return True
    return False
    