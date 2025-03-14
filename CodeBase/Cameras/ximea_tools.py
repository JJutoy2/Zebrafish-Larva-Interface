from ximea import xiapi
from typing import Tuple
from ..Cameras.camera_stream import stream_camera, np, cv2, WindowParameters
from dataclasses import dataclass

@dataclass
class XimeaSettings:
    height: int | None = None
    width: int | None = None 
    height_scale: float = 0.5
    width_scale: float = 0.5
    exposure: int = 150000

@dataclass
class CamInterfaceXimea:
    cam: xiapi.Camera | None = None
    img: xiapi.Image | None = None
    settings: XimeaSettings | None = None

    def __init__(self,
                 xi_settings: XimeaSettings | None = None):
        self.cam = xiapi.Camera()
        try:
            self.cam.open_device()
        except xiapi.Xi_error:
            print('Ximea camera not found')
            return

        self.settings = XimeaSettings() if xi_settings is None else xi_settings

        if xi_settings is not None:
            set_xi_settings(self.cam, xi_settings)

        #create instance of Image to store image data and metadata
        self.img = xiapi.Image()

        #start data acquisition
        self.cam.start_acquisition()

    def read(self) -> Tuple[bool, np.ndarray]:
        '''Returns image from ximea cam'''
        try:
            self.cam.get_image(self.img)
            frame = self.img.get_image_data_numpy()
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            ret = True
        except:
            ret = False
            frame = None

        return (ret, frame)

    def release(self):
        '''Closes connection to xi cam'''
        self.cam.close_device()

#TODO Verify
def set_xi_settings(cam: xiapi.Camera, settings: XimeaSettings):
    settings.width = cam.get_width()
    settings.height = cam.get_height()
    cam.set_width(int(settings.width*settings.width_scale))
    cam.set_height(int(settings.height*settings.height_scale))
    cam.set_exposure(settings.exposure)
    print(f'xi_fps:{cam.get_framerate()}')
    

def setup_ximea_cam(loc: Tuple[int,int] = (0,0)):
    #Import necessary subfunctions
    from ..Bindings.ximea_bindings import ximea_cam_binds
    from ..Cameras.double_eye_filter_stack import filter_stack_double_eye_angle, FilterData, CamData 
    from ..Processes.env_tools import load_value_from_env, load_list_from_env
    
    #Instantiate filters and filter data
    cam_filter_data = FilterData()
    cam_filter_data.grey_threshold = int(load_value_from_env('XI_GT'))
    cam_filter_data.median_blur_kernal = int(load_value_from_env('XI_MB'))
    try:
        cam_filter_data.bb = load_list_from_env('XI_BB')
    except Exception as E:
        print(E)
        pass
    
    ximea_settings = XimeaSettings()
    ximea_settings.exposure = int(load_value_from_env('XI_EXPOSURE'))
    ximea_settings.width_scale = float(load_value_from_env('XI_SCALE'))
    ximea_settings.height_scale = float(load_value_from_env('XI_SCALE'))
    
    try: 
        loc = load_list_from_env('LOC_XI')
    except: 
        loc: Tuple[int,int] = (0,0)
    cam_interface_ximea = CamInterfaceXimea(ximea_settings)
    cam_window = WindowParameters('Ximea Window', loc)
    cam_window.window_size = (ximea_settings.height, ximea_settings.width)
        
    cam_data = CamData(cam_interface_ximea, filter_stack_double_eye_angle, cam_filter_data)
    cam_window.fps = int(load_value_from_env('XI_FPS'))
    cam_thread = stream_camera(cam_data,
                               cam_window,
                               ximea_cam_binds,
                               )    
    
    return (cam_data, cam_window, cam_thread)