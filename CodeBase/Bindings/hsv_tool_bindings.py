from ..Cameras.camera_stream import CamData, WindowParameters, cv2
from ..Cameras.cv2_filters import select_ROI
from ..Bindings.binding_tools import increment
from ..Processes.env_tools import load_list_from_env, save_list_to_env
from tkinter import simpledialog

def hsv_keys(input: str):
    match str(input).lower()[0]:
        case 'p':
            key = 'PINK'
        case 'w':
            key = 'WHITE'
        case _:
            key = 'DEFAULT'
    return key


def hsv_tool_binds(key: int, stream_vars: list, d: CamData, w: WindowParameters):
    img = stream_vars[0]
    if key == 27: #escape key
        w.status = False #exits thread
    match chr(key):
        case 'b':
            d.filter_data.bb = select_ROI(img, w.window_name)
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
        case '=':
            key = simpledialog.askstring('HSV Save Key Name Prompt', 
                                         'Enter HSV Key to Save (P, W)',
                                         initialvalue='P')
            key = hsv_keys(key)

            save_list_to_env(f'HSV_LOWS_{key}', d.filter_data.hsv_lower)
            save_list_to_env(f'HSV_HIGHS_{key}', d.filter_data.hsv_upper)
        case 'l':
            key = simpledialog.askstring('HSV Load Key Name Prompt', 
                                         'Enter HSV Key to Load (P, W)',
                                         initialvalue='P')
            key = hsv_keys(key)

            d.filter_data.hsv_lower = load_list_from_env(f'HSV_LOWS_{key}')
            d.filter_data.hsv_upper = load_list_from_env(f'HSV_HIGHS_{key}')

            if d.filter_data.hsv_lower is None or d.filter_data.hsv_lower is None:
                return
            cv2.setTrackbarPos('LB Hue', w.window_name, d.filter_data.hsv_lower[0])
            cv2.setTrackbarPos('UB Hue', w.window_name, d.filter_data.hsv_upper[0])
            cv2.setTrackbarPos('LB Saturation', w.window_name, d.filter_data.hsv_lower[1])
            cv2.setTrackbarPos('UB Saturation', w.window_name, d.filter_data.hsv_upper[1])
            cv2.setTrackbarPos('LB Value', w.window_name, d.filter_data.hsv_lower[2])
            cv2.setTrackbarPos('UB Value', w.window_name, d.filter_data.hsv_upper[2])

        case _:
            pass