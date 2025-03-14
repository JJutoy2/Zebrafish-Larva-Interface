from ..Animations.rotating_static_animation import RotatingStaticAnimationData, WindowParameters
from ..Bindings.binding_tools import copy_text_to_clipboard

def rotating_static_binds(key: int, data: RotatingStaticAnimationData, w: WindowParameters):

    def preset_omega(omega: float):
        # settings.static_display = False
        data.static_omega = omega
        data.fish_roi_radius = 8 #default 8
        # data.static_radius = (240, 240) #default 240
        # data.static_space = 0.5 #default 0.5
        print(f'Preset Omega: {data.static_omega}')

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
        case 'p':
            data.pause = not data.pause
            print(f'Animation {'Paused' if data.pause else 'Unpaused'}')
        case ' ':
            data.pause = not data.pause
            print(f'Animation {'Paused' if data.pause else 'Unpaused'}')
        case 'q':
            data.static_display = not data.static_display
        case 'w':
            if data.static_prob > 0:
                data.static_prob -= data.static_prob_delta
            print(f'Static Radius: {data.static_prob:.2f}')
            data.update()
        case 'e':
            if data.static_prob < 1:
                data.static_prob += data.static_prob_delta
            print(f'Static Radius: {data.static_prob:.2f}')
            data.update()
        case 'd':
            if data.fish_roi_radius < min(data.size)/2:
                data.fish_roi_radius += 1
            print(f'Fish Radius: {data.fish_roi_radius}')
            return
        case 'f':
            w.fps_display_flag = not w.fps_display_flag
        case 's':
            if data.fish_roi_radius > 0:
                data.fish_roi_radius -= 1
            print(f'Fish Radius: {data.fish_roi_radius}')
            return
        case 'a':
            data.fish_roi_radius_display = not data.fish_roi_radius_display
            return
        case 'h':
            if data.fish_roi_radius_display or data.static_display:  
                data.fish_roi_radius_display = False
                data.static_display = False
            else:
                data.fish_roi_radius_display = True
                data.static_display = True
        case '[':
            if data.static_omega > 0:
                data.static_omega -= 1
            print(f'Static Omega: {data.static_omega}')
            return
        case ']':
            if data.static_omega < 500: #arbitrary limit
                data.static_omega += 1
            print(f'Static Omega: {data.static_omega}')
            return
        case 'z':
            data.static_direction = -data.static_direction
            print(f'Static Direction: {'CW' if data.static_direction > 0 else 'CCW'}')
            return
        case _:
            pass