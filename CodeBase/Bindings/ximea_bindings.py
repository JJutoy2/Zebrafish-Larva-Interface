from ..Cameras.camera_stream import CamData, WindowParameters, cv2
from ..Cameras.cv2_filters import select_ROI
from ..Bindings.binding_tools import increment
from ..Cameras.ximea_tools import CamInterfaceXimea, XimeaSettings
from ..Processes.env_tools import save_list_to_env, save_value_to_env

def ximea_cam_binds(key: int, stream_vars: list, d: CamData, w: WindowParameters):
    img = stream_vars[0]

    def type_help():
        ximea_interface: CamInterfaceXimea = d.cap 
        ximea_settings: XimeaSettings = d.cap.settings
        return (ximea_interface, ximea_settings)

    if key == 27: #escape key
        w.status = False #exits thread
    match chr(key):
        case 'w':
            ximea_interface, ximea_settings = type_help()
            ximea_settings.exposure = increment('Exposure',
                                                ximea_settings.exposure,
                                                upper_limit=1000000,
                                                delta=1000,
                                                )
            ximea_interface.cam.set_exposure(ximea_settings.exposure) 

            d.cap.settings = ximea_settings
        case 'e':
            ximea_interface, ximea_settings = type_help()
            ximea_settings.exposure = increment('Exposure',
                                                ximea_settings.exposure,
                                                lower_limit=0,
                                                delta=1000,
                                                )
            ximea_interface.cam.set_exposure(ximea_settings.exposure) 
  
            d.cap.settings = ximea_settings
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
            save_value_to_env('XI_GT', d.filter_data.grey_threshold)
            save_value_to_env('XI_MB', d.filter_data.median_blur_kernal)
            save_list_to_env('XI_BB', d.filter_data.bb)
        case 'm':
            cv2.imwrite('Xi_IMG.png', img)
            print('Raw Screenshot of Ximea saved as: Xi_IMG.png')       
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
        case 'r':
            if d.filter_data.fish_eye == 1:
                d.filter_data.fish_eye = 0
                print(f'Left Eye Chosen')
            else:
                d.filter_data.fish_eye = 1
                print(f'Right Eye Chosen')
            
        case _:
            pass