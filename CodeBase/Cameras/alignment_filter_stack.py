from .cv2_tools import WindowParameters, move_to_top, check_set, Tuple
from .cv2_filters import *
from .camera_stream import CamData
import csv

def filter_stack_alignment(stream_vars: Tuple[np.ndarray,int], w: WindowParameters, d: CamData):
    '''
    Takes in stream variables, window parameters and cam data and outputs img with fish eye angle
    '''

    img = stream_vars[0]

    if d.filter_data.bb is None:
        if check_set(d.filter_data.adjust_window_name,-1.0):
            cv2.destroyWindow(d.filter_data.adjust_window_name)
        
        return img

    blurred = cv2.medianBlur(img, d.filter_data.median_blur_kernal)
    
    bw = filter_black_white(blurred,d.filter_data.grey_threshold, 
                            # invert=False
                            )
    
    
    # if d.filter_data.adjust_window:
    #     cv2.imshow(d.filter_data.adjust_window_name, bw)
    #     # cv2.imshow('blur', blurred)
    #     # move_to_top('blur')
    #     # cv2.moveWindow('blur', 300,300)
    #     move_to_top(d.filter_data.adjust_window_name)

    #Output values as k-v pairs
    w_inc = 0
    h_inc = 0
    fish_data = []
    for fish in range(0,d.filter_data.fish_subjects):

        if fish%d.filter_data.fish_columns == 0:
            w_inc = 0
        else:
            w_inc += d.filter_data.bb_w_inc

        if fish%d.filter_data.fish_columns == 0 and fish != 0:
            h_inc += d.filter_data.bb_h_inc
        # print(fish%d.filter_data.fish_columns, w_inc, h_inc)

        old_bb = d.filter_data.bb
        new_bb = [old_bb[0] + w_inc, old_bb[1] + h_inc, old_bb[2], old_bb[3]]

        cropped = filter_crop(bw, new_bb)

        eye = find_eye_areas(img,cropped,
                             new_bb,
                             d.filter_data.show_eyes,
                             d.filter_data.v_dis_thresh,
                             d.filter_data.area_thresh,
                             )
        # Data Out
        # print(type(eye))
        if len(eye) > 0:
            # fish_data.append(*eye)
            fish_data.extend(eye)
        else:
            # fish_data.append('nan')
            fish_data.extend(['nan','nan'])


    # Fish# , Aligned, Eye Diff

    output =    {'cam_time': stream_vars[-1],
                'fish_data': fish_data
                }
    # print(fish_data)
    d.set_output(output)  

    

    if check_set(d.filter_data.adjust_window_name,-1.0) and not d.filter_data.adjust_window:
        cv2.destroyWindow(d.filter_data.adjust_window_name)      

    return img