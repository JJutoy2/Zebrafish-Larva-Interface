from ..Animations.okr_animation import OKRAnimationData, WindowParameters
from ..Bindings.binding_tools import copy_text_to_clipboard, increment

def okr_binds(key: int, data: OKRAnimationData, w: WindowParameters):

    def preset_omega(omega: float):
        # settings.grating_display = False
        data.grating_omega = omega
        data.fish_roi_radius = 8 #default 8
        data.grating_radius = (240, 240) #default 240
        data.grating_space = 0.5 #default 0.5
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
            preset_omega(30.0)            
        case '2':
            # 45 Degrees
            preset_omega(45.0)            
        case '3':
            # 60 Degrees
            preset_omega(60.0)
        case '4':
            x_inc = increment('Center', data.fish_roi_offset[0],lower_limit=-120)
            data.fish_roi_offset = (x_inc, data.fish_roi_offset[1])
        case '6':
            x_inc = increment('Center', data.fish_roi_offset[0],upper_limit=120)
            data.fish_roi_offset = (x_inc, data.fish_roi_offset[1])
        case '8':
            y_inc = increment('Center', data.fish_roi_offset[1],lower_limit=-120)
            data.fish_roi_offset = (data.fish_roi_offset[0], y_inc)
        case '5':
            y_inc = increment('Center', data.fish_roi_offset[1],upper_limit=120)
            data.fish_roi_offset = (data.fish_roi_offset[0], y_inc)
            print(data.fish_roi_offset)
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
            if data.grating_omega > 0:
                data.grating_omega -= 1
            print(f'Gratings Omega: {data.grating_omega}')
            return
        case ']':
            if data.grating_omega < 500: #arbitrary limit
                data.grating_omega += 1
            print(f'Gratings Omega: {data.grating_omega}')
            return
        case 'k':            
            data.grating_thickness = increment('Grating Thickness',
                                               data.grating_thickness,
                                               upper_limit=data.grating_radius[0]
                                               )
        case 'j':
            data.grating_thickness = increment('Grating Thickness',
                                               data.grating_thickness,
                                               lower_limit=0
                                               )
        case 'z':
            data.grating_direction = -data.grating_direction
            print(f'Grating Direction: {'CW' if data.grating_direction > 0 else 'CCW'}')
            return
        case _:
            pass