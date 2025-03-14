import cv2
import numpy as np
from CodeBase.Cameras.cv2_filters import filter_hsv
from CodeBase.Cameras.cv2_tools import check_set
from CodeBase.Cameras.camera_stream import *

def filter_stack_find_hsv(stream_vars: Tuple[np.ndarray,int], w: WindowParameters, d: CamData):
    img = stream_vars[0]
   
    low_h = cv2.getTrackbarPos('LB Hue', w.window_name)
    upper_h = cv2.getTrackbarPos('UB Hue', w.window_name)
    low_s = cv2.getTrackbarPos('LB Saturation', w.window_name)
    upper_s = cv2.getTrackbarPos('UB Saturation', w.window_name)
    low_v = cv2.getTrackbarPos('LB Value', w.window_name)
    upper_v = cv2.getTrackbarPos('UB Value', w.window_name)
    
    d.filter_data.hsv_lower = np.array([low_h, low_s, low_v])
    d.filter_data.hsv_upper = np.array([upper_h, upper_s, upper_v])

    if d.filter_data.adjust_window:
        cv2.imshow(d.filter_data.adjust_window_name, img)

    masked_frame = filter_hsv(img, 
                            d.filter_data.hsv_lower,
                            d.filter_data.hsv_upper,
                            )
    
    if check_set(d.filter_data.adjust_window_name,-1.0) and not d.filter_data.adjust_window:
        cv2.destroyWindow(d.filter_data.adjust_window_name)    
    
    return masked_frame

def setup_hsv_find_tool(src:int = 0, loc: Tuple[int,int] = (0,0)):
    #Import necessary subfunctions
    from CodeBase.Bindings.hsv_tool_bindings import hsv_tool_binds

    #Instantiate filters and filter data
    cam_filter_data = FilterData()

    cam_data = CamData(src, filter_stack_find_hsv, cam_filter_data)
    cam_window = WindowParameters('HSV Find Tool', loc)

    def pre_read_process():
        #Creates trackbars after window is made
        def nothing(val):
            pass
        cv2.createTrackbar('LB Hue',cam_window.window_name,0,179,nothing)
        cv2.createTrackbar('UB Hue',cam_window.window_name,179,179,nothing)
        cv2.createTrackbar('LB Saturation',cam_window.window_name,0,255,nothing)
        cv2.createTrackbar('UB Saturation',cam_window.window_name,255,255,nothing)
        cv2.createTrackbar('LB Value',cam_window.window_name,0,255,nothing)
        cv2.createTrackbar('UB Value',cam_window.window_name,255,255,nothing)

    cam_thread = stream_camera(cam_data,
                                  cam_window,
                                  hsv_tool_binds,
                                  pre_read_process,
                                  )    
    
    return (cam_data, cam_window, cam_thread)
