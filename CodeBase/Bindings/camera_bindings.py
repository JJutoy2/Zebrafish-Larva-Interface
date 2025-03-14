from ..Cameras.camera_stream import CamData, WindowParameters, cv2
from ..Cameras.cv2_filters import select_ROI
from ..Bindings.binding_tools import increment
from ..Processes.env_tools import save_list_to_env, save_value_to_env

def cam_binds(key: int, stream_vars: list, d: CamData, w: WindowParameters):
    img = stream_vars[0]
    if key == 27: #escape key
        w.status = False #exits thread
    match chr(key):
        case 'b':
            d.filter_data.bb = select_ROI(img, w.window_name)
        case 'e':
            d.filter_data.show_eyes = not d.filter_data.show_eyes 
        case 'q':
            w.status = False    
        case 'p':
            d.pause = not d.pause
        case 'h':
            d.display = not d.display
        case 'k':
            w.fps = increment('FPS',
                              w.fps,
                              upper_limit = 1200,
                              delta = 10
                              )
        case 'j':
            w.fps = increment('FPS',
                              w.fps,
                              lower_limit = 10,
                              delta = 10
                              )
        case 'a':
            d.filter_data.adjust_window = not d.filter_data.adjust_window
        case 'f':
            w.fps_display_flag = not w.fps_display_flag
        case 't':
            d.filter_data.grey_threshold = increment('Grey Threshold',
                                                     d.filter_data.grey_threshold,
                                                     lower_limit=0
                                                    )
        case 'y':
            d.filter_data.grey_threshold = increment('Grey Threshold',
                                                     d.filter_data.grey_threshold,
                                                     upper_limit =255
                                                    )
        case '.':
            d.filter_data.median_blur_kernal = increment('Median Blur',
                                                         d.filter_data.median_blur_kernal,
                                                         upper_limit=100,
                                                         delta=2
                                                         )
        case ',':
            d.filter_data.median_blur_kernal = increment('Median Blur',
                                                         d.filter_data.median_blur_kernal,
                                                         lower_limit=1,
                                                         delta=2
                                                         )
        case '=':
            save_value_to_env('CAM_GT', d.filter_data.grey_threshold)
            save_value_to_env('CAM_MB', d.filter_data.median_blur_kernal)
            save_list_to_env('CAM_BB', d.filter_data.bb)
        case 'm':
            cv2.imwrite('Cam_IMG.png', img )
            print('Raw Screenshot of Cam saved as: Cam_IMG.png')   
        case _:
            pass