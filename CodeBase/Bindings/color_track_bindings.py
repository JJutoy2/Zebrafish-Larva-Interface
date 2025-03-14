from ..Cameras.camera_stream import CamData, WindowParameters, cv2
from ..Cameras.cv2_filters import select_ROI
from ..Bindings.binding_tools import increment
from ..Processes import save_list_to_env, save_value_to_env

def color_track_binds(key: int, stream_vars: list, d: CamData, w: WindowParameters):
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
            d.filter_data.adjust_window += 1
            if d.filter_data.adjust_window > 2:
                d.filter_data.adjust_window = 0
            print(f'Adjust window: {d.filter_data.adjust_window}')
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
            save_value_to_env('CT_GT', d.filter_data.grey_threshold)
            save_value_to_env('CT_MB', d.filter_data.median_blur_kernal)
            
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
        case 'm':
            disp_img = d.img_filter(stream_vars, w, d)
            cv2.imwrite('CT_IMG.png', disp_img)
            print('Screenshot of Color Track Taken, saved as: CT_IMG.png')
        case _:
            pass