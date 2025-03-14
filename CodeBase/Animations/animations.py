import cv2
from dataclasses import dataclass
from threading import Thread
import numpy as np
from functools import partial
from typing import Callable, Tuple
from ..Cameras.cv2_tools import WindowParameters

@dataclass
class AnimationData:
    # color_channels: int = 3
    canvas: np.ndarray = None
    background_color: Tuple[int,int,int] = (0, 0, 0)
    display: bool = True #
    pause: bool = False
    center: tuple = (None, None)

    def set_window_settings(self, window_parms: WindowParameters):
        self.canvas = np.empty((*window_parms.window_size, len(self.background_color)), dtype=np.uint8)
        self.center = (int(window_parms.window_size[1]/2), int(window_parms.window_size[0]/2)) #(x,y)
        self.size = ((window_parms.window_size[1],window_parms.window_size[0])) #(x,y)

    def update(self):
        #fill in for children classes
        return None

def default_animation(animation_var: tuple, data: AnimationData):
    from numpy import random as r
    img = data.canvas
    img[...] = np.array(data.background_color).astype(np.uint8) #required to clear the canvas

    pt1 = (int(data.size[0]*r.random()), int(data.size[1]*r.random()))
    pt2 = (int(data.size[0]*r.random()), int(data.size[1]*r.random()))
    color = (255*r.random(),255*r.random(),255*r.random())
    cv2.line(img,pt1,pt2,color,10,cv2.LINE_AA)

    return img  

def default_animation_binds(key: int, data: AnimationData, window_parms: WindowParameters):
    char = chr(key)
    print(f'{key} == {char}')
    match char:
        case 'q':
            window_parms.status = False #exits thread
        case 'p':
            data.display = not data.display
        case 'w':
            data.background_color = (0,0,0)
        case 'e':
            data.background_color = (0,0,255)
        case _:
            pass

def animate_canvas(data: AnimationData = AnimationData(),
                   animate: Callable = default_animation,
                   window_parms: WindowParameters | None = None,
                   bindings: Callable[[int, AnimationData, WindowParameters], None] = default_animation_binds,
                   ) -> Thread:
    #Initiation
    window_parms = window_parms if window_parms is not None else WindowParameters('Default Animate Canvas')
    binds = partial(bindings, data = data, w = window_parms)
    animate = partial(animate, data = data)
    data.set_window_settings(window_parms)
    data.update()

    def thread_function():
        if window_parms.fullscreen:
            cv2.namedWindow(window_parms.window_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(window_parms.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        frame = 1
        window_parms.frame_time.start_timing()
        while window_parms.status:
            
            if data.display:
                dt = window_parms.frame_time.delta_time
                delta_time = dt if dt is not None else 0
                if data.pause: 
                    delta_time = 0
                animation_var: Tuple[float,int] = (delta_time, frame)         
                img = animate(animation_var)
                frame += 1 if frame < window_parms.frames else 1
            else:
                img = data.canvas
                img[...] = np.array(data.background_color).astype(np.uint8)

            
            window_parms.call_fps(img)  
            cv2.imshow(window_parms.window_name, img)
            window_parms.frame_time.tic()
            # window_parms.frame_time.toc()
            wkey = window_parms.frame_time.calc_waitkey_time(window_parms.fps)
            key = cv2.waitKey(wkey) #in ms

            if key != -1:
                binds(key)
            
            if cv2.getWindowProperty(window_parms.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            

        if cv2.getWindowProperty(window_parms.window_name, cv2.WND_PROP_VISIBLE) > 0:
            cv2.destroyWindow(window_parms.window_name)

    canvas_thread = Thread(target=thread_function)
    return canvas_thread