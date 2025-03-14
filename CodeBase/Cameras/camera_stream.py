import cv2
from threading import Thread, Lock
from dataclasses import dataclass 
from ..Cameras.cv2_filters import FilterData
from ..Cameras.cv2_tools import WindowParameters
from typing import Callable, Tuple, Protocol
from functools import partial
import numpy as np

#Interface type for typing
class CamInterface(Protocol):
    settings: any
    def read(self) -> Tuple[bool, np.ndarray]:
        pass
    def release(self):
        pass


@dataclass
class CamData:
    # thread: threading.Thread = None
    output: dict = None
    output_lock: Lock = None
    img_filter: Callable | None = None
    filter_data: FilterData | None = None
    img: np.ndarray | None = None
    display: bool = True
    pause: bool = False
    center: tuple = (None, None)
    frame: int = 0

    def set_window_settings(self, window_parms: WindowParameters):
        self.center = (int(window_parms.window_size[1]/2), int(window_parms.window_size[0]/2)) #(x,y)
        self.size = ((window_parms.window_size[1],window_parms.window_size[0])) #(x,y)
        if self.filter_data is not None:
            self.filter_data.adjust_window_name = window_parms.window_name + '- adjustment window'

    def __init__(self, 
                 src: int | str | CamInterface = 0,
                 img_filter_function: Callable[[np.ndarray], np.ndarray] | None = None,
                 filter_data: FilterData | None = None,
                 ):
        
        if type(src) == int:
            print("Loading Camera")
            self.cap: CamInterface = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        elif type(src) == str:
            file_type = src.split('.')[-1]
            if file_type == 'tif':
                self.cap: CamInterface = cv2.VideoCapture(src, cv2.IMREAD_UNCHANGED)
                print("Loading tif Video")
            else: 
                self.cap: CamInterface = cv2.VideoCapture(src)
                print("Loading Regular Video")
        else:
            print("Loading XiCam")
            self.cap = src
        self.src = src
        self.img_filter = img_filter_function
        self.filter_data = filter_data
        self.output_lock = Lock()

    def get_output(self):
        with self.output_lock:
            return self.output
        
    def set_output(self, out:dict):
        with self.output_lock:
            self.output = out

    # def __repr__(self):
    #     return f'{self.cap}'
        
def default_cam_binds(key: int, stream_vars: list, data: CamData, window_parms: WindowParameters):
    if key == 27: #escape key
        window_parms.status = False #exits thread
    match chr(key):
        case 'q':
            window_parms.status = False    
        case 'p':
            data.pause = not data.pause
        case 'h':
            data.display = not data.display

def stream_camera(data: CamData,
                  window_parms: WindowParameters | None = None,
                  bindings: Callable[[str, CamData, WindowParameters], None] = default_cam_binds,
                  pre_read_process: Callable | None = None,
                  first_frame_process: Callable | None = None,
                  ) -> Thread:
    window_parms = window_parms if window_parms is not None else WindowParameters()
    binds = partial(bindings, d = data, w = window_parms)
    data.set_window_settings(window_parms)

    def thread_function():
        cv2.namedWindow(window_parms.window_name)
        # if window_parms.fullscreen:
        #     cv2.setWindowProperty(window_parms.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        if pre_read_process is not None:
            pre_read_process(data, window_parms)

        window_parms.frame_time.start_timing()
        while window_parms.status:
            if not data.pause:
                
                ret, img = data.cap.read()

                if not ret:
                    print("Can't receive img (stream end?). Exiting ...")
                    break

                #Frame count
                data.frame += 1

                #RESIZING
                height, width, layers = img.shape
                new_h = int(height / 2) #TODO Change to cam data var
                new_w = int(width / 2)
                img = cv2.resize(img, (new_w, new_h))
                
                stream_vars: Tuple[np.ndarray,int,int] = (img, window_parms.frame_time.tic(),data.frame)

                if first_frame_process is not None:
                    first_frame_process(stream_vars, data, window_parms)
                # window_parms.frame_time.toc()
                # Apply img filters            
                if data.display is True:
                    display_img = data.img_filter(stream_vars, window_parms, data) if data.img_filter is not None else img
                    window_parms.frames += 1
                else: 
                    display_img = img
                    display_img[...] = np.array([0,0,0]).astype(np.uint8)

                window_parms.call_fps(display_img)
                
                # Display the resulting frame
                cv2.imshow(window_parms.window_name, display_img)
            
            # print(window_parms.frame_time.calc_waitkey_time(window_parms.fps))
            
            
            # wkey = window_parms.frame_time.calc_waitkey_time(window_parms.fps)
            # key = cv2.waitKey(wkey)
            key = cv2.waitKey(1)

            #bindings
            if key != -1:
                binds(key, stream_vars)
            
            if cv2.getWindowProperty(window_parms.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

            
        if cv2.getWindowProperty(window_parms.window_name, cv2.WND_PROP_VISIBLE) > 0:
            cv2.destroyWindow(window_parms.window_name)
        
        data.cap.release()
    
    canvas_thread = Thread(target=thread_function)
    return canvas_thread

#Template setup function
def setup_cam(src:int = 0, loc: Tuple[int,int] = (0,0)):
    #Import necessary subfunctions
    from ..Bindings.camera_bindings import cam_binds
    from ..Cameras.double_eye_filter_stack import filter_stack_double_eye_angle
    # from ..Cameras.food_filter_stack import filter_stack_food_area
    from ..Processes.env_tools import load_value_from_env, load_list_from_env

    try: 
        loc = load_list_from_env('LOC_CAM')
    except: 
        loc: Tuple[int,int] = (0,0)

    #Instantiate filters and filter data
    cam_filter_data = FilterData()
    cam_filter_data.grey_threshold = int(load_value_from_env('CAM_GT'))
    cam_filter_data.median_blur_kernal = int(load_value_from_env('CAM_MB'))
    cam_filter_data.bb = load_list_from_env('CAM_BB')

    
    cam_data = CamData(src, filter_stack_double_eye_angle, cam_filter_data)
    cam_window = WindowParameters('Default Cam Window', loc)
    cam_window.fps = int(load_value_from_env('CAM_FPS'))
    
    cam_thread = stream_camera(cam_data,
                                  cam_window,
                                  cam_binds,
                                  )    
    
    return (cam_data, cam_window, cam_thread)

#Car Tracking Setup Function
def setup_color_track_cam(src:int = 0, loc: Tuple[int,int] = (0,0)):
    from ..Bindings.color_track_bindings import color_track_binds
    from .filter_stack_color_track import filter_stack_color_track
    from .cv2_filters import set_warp_params
    from ..Processes.env_tools import load_list_from_env, load_value_from_env

    # Load from env variables:
    warp_points = [load_list_from_env('WARP_POINT_A'),
                   load_list_from_env('WARP_POINT_B'),
                   load_list_from_env('WARP_POINT_C'),
                   load_list_from_env('WARP_POINT_D'),
                   ]
    # print(warp_points)
    
    try:
        loc = load_list_from_env('LOC_CT')
    except:
        loc: Tuple[int,int] = (0,0)

    hsv_lows = load_list_from_env('HSV_LOWS_PINK')
    hsv_highs = load_list_from_env('HSV_HIGHS_PINK')

    #SETUP FILTER
    cam_filter_data = FilterData()
    cam_filter_data.warp_params = set_warp_params(warp_points)
    cam_filter_data.countour_area_min = 0
    cam_filter_data.hsv_lower = hsv_lows
    cam_filter_data.hsv_upper = hsv_highs
    cam_filter_data.adjust_window = 0
    cam_filter_data.median_blur_kernal = int(load_value_from_env('CT_MB'))
    cam_filter_data.grey_threshold = int(load_value_from_env('CT_GT'))

    cam_data = CamData(src, filter_stack_color_track, cam_filter_data)
    cam_window = WindowParameters('Car Tracking Window', loc)

    cam_thread = stream_camera(cam_data,
                                  cam_window,
                                  color_track_binds,
                                  #   t_fps=True
                                  )    
    
    return (cam_data, cam_window, cam_thread)

#Load Vid for alignment
def setup_vid_post(src:str, loc: Tuple[int,int] = (0,0)):
    #Import necessary subfunctions
    from ..Bindings.camera_bindings import cam_binds
    from ..Cameras.alignment_filter_stack import filter_stack_alignment
    from ..Processes.env_tools import load_value_from_env, load_list_from_env
    from ..Cameras.cv2_filters import select_ROI

    try: 
        loc = load_list_from_env('LOC_CAM')
    except: 
        loc: Tuple[int,int] = (0,0)

    #Instantiate filters and filter data
    vid_filter_data = FilterData()
    # cam_filter_data.grey_threshold = int(load_value_from_env('CAM_GT'))
    # cam_filter_data.median_blur_kernal = int(load_value_from_env('CAM_MB'))
    vid_filter_data.bb = load_list_from_env('CAM_BB')
    vid_filter_data.grey_threshold = float(load_value_from_env('CAM_GT'))
    vid_filter_data.median_blur_kernal = int(load_value_from_env('CAM_MB'))
    vid_filter_data.fish_subjects = 15
    vid_filter_data.fish_columns = 5
    vid_filter_data.bb_w_inc = 90
    vid_filter_data.bb_h_inc = 195
    vid_filter_data.v_dis_thresh = 5
    vid_filter_data.area_thresh = 80
    vid_filter_data.bb_init = True
    
    
    cam_data = CamData(src, filter_stack_alignment, vid_filter_data)
    cam_window = WindowParameters('Alignment Process Window', loc)
    cam_window.fps = int(load_value_from_env('CAM_FPS'))
    
    def first_frame_proc(sv: list[Tuple[np.ndarray,int], float], data: CamData, window_parms: WindowParameters):
        if data.filter_data.bb_init:
            
            img = sv[0]
            bb = select_ROI(img,'First Frame')
            if bb == None:
                print(f'Using Previous BB: {data.filter_data.bb}')
            else:
                data.filter_data.bb = bb
            data.filter_data.bb_init = False
            
    cam_thread = stream_camera(cam_data,
                                  cam_window,
                                  cam_binds,
                                  first_frame_process=first_frame_proc
                                  )    
    
    return (cam_data, cam_window, cam_thread)