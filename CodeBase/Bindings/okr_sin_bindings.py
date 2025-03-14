from ..Animations.okr_sin import OKRSinData, WindowParameters
from ..Bindings.binding_tools import copy_text_to_clipboard, increment

def okr_sin_binds(key: int, data: OKRSinData, w: WindowParameters):

    def preset_omega(omega: float):
        # settings.grating_display = False
        data.grating_omega = omega
        # data.fish_roi_radius = 16 #default 8
        # data.grating_radius = (240, 240) #default 240
        # data.grating_space = 0.5 #default 0.5
        data.t_time = 0
        print(f'Preset Omega: {data.grating_omega}')

    if key == 27: #escape key
        w.status = False #exits thread
        return
    match chr(key):
        # Change cases 1,2,3 for different trials
        case '=':
            #Outputs key values of settings to terminal and copies it to clipboard:
            copy_text_to_clipboard(str(data), 'OKR SETTINGS:\n' + str(data) + '---> copied to clipboard')
        case '1':
            # 30 Degrees
            preset_omega(0.1)            
        case '2':
            # 45 Degrees
            preset_omega(0.5)            
        case '3':
            # 60 Degrees
            preset_omega(0.75)            
        case '4':
            # 45 Degrees
            preset_omega(1)            
        case '5':
            # 60 Degrees
            preset_omega(1.5)            
        case '6':
            # 60 Degrees
            preset_omega(2)            
        case '7':
            # 60 Degrees
            preset_omega(5)            
        case '8':
            # 60 Degrees
            preset_omega(10)            
        case '9':
            # 60 Degrees
            preset_omega(50)            
        case 'p':
            data.pause = not data.pause
            print(f'Animation {'Paused' if data.pause else 'Unpaused'}')
        case ' ':
            data.pause = not data.pause
            print(f'Animation {'Paused' if data.pause else 'Unpaused'}')
        case 'f':
            w.fps_display_flag = not w.fps_display_flag
        case 'q':
            data.grating_display = not data.grating_display
            print(f'Grating Display: {data.grating_display}')
        case 'y':
            if data.gratings > 0:
                data.gratings -= 1 
            print(f'Gratings: {data.gratings}')
        case 'u':
            if data.gratings < 30: #arbitrary max 
                data.gratings += 1
            print(f'Gratings: {data.gratings}')
        case 'r':
            if data.grating_space > 0:
                data.grating_space -= 0.01
            print(f'Grating Space: {data.grating_space:.2f}')
        case 't':
            if data.grating_space < 1:
                data.grating_space += 0.01
            print(f'Grating Space: {data.grating_space:.2f}')
        case 'w':
            if data.grating_radius[0] > 0:
                data.grating_radius = (data.grating_radius[0]-1,data.grating_radius[1]-1)
            print(f'Grating Radius: {data.grating_radius}')
        case 'e':
            if data.grating_radius[0] < min(data.size)/2:
                data.grating_radius = (data.grating_radius[0]+1,data.grating_radius[1]+1)
            print(f'Grating Radius: {data.grating_radius}')
        case 'd':
            if data.fish_roi_radius < min(data.size)/2:
                data.fish_roi_radius += 1
            print(f'Fish Radius: {data.fish_roi_radius}')
        case 's':
            if data.fish_roi_radius > 0:
                data.fish_roi_radius -= 1
            print(f'Fish Radius: {data.fish_roi_radius}')
        case 'a':
            data.fish_roi_radius_display = not data.fish_roi_radius_display
        case 'h':
            if data.fish_roi_radius_display or data.grating_display:  
                data.fish_roi_radius_display = False
                data.grating_display = False
            else:
                data.fish_roi_radius_display = True
                data.grating_display = True
        case '[':
            data.grating_omega = increment('grating_omega',
                                        data.grating_omega,
                                        lower_limit=0,
                                        delta=1,
                                        )
        case ']':
            data.grating_omega = increment('grating_omega',
                                        data.grating_omega,
                                        upper_limit=100,
                                        delta=1,
                                        )
        # case 'z':
        #     data.grating_direction = -data.grating_direction
        #     print(f'Grating Direction: {'CW' if data.grating_direction > 0 else 'CCW'}')
        #     return
        case 'x':
            data.grating_theta_amp = increment('grating_theta_amp',
                                               data.grating_theta_amp,
                                               lower_limit=1
                                               )
        case 'c':
            data.grating_theta_amp = increment('grating_theta_amp',
                                               data.grating_theta_amp,
                                               upper_limit=360
                                               )
        case _:
            pass