from .cv2_tools import WindowParameters, move_to_top, check_set, Tuple
from .cv2_filters import *
from .camera_stream import CamData

def filter_stack_food_area(stream_vars: Tuple[np.ndarray,int], w: WindowParameters, d: CamData):
    '''
    Takes in stream variables, window parameters and cam data and outputs img with fish eye angle
    '''
    img = stream_vars[0]
  
    if d.filter_data.bb is None:
        if check_set(d.filter_data.adjust_window_name,-1.0):
            cv2.destroyWindow(d.filter_data.adjust_window_name)
        
        return img
    
    cropped = filter_crop(img, d.filter_data.bb)
    blurred = cv2.medianBlur(cropped, d.filter_data.median_blur_kernal)
    # Too slow
    # blurred = cv2.bilateralFilter(cropped, d.filter_data.median_blur_kernal, 200, 200)
    
    bw = filter_black_white(blurred,d.filter_data.grey_threshold, 
                            invert=False
                            )
    
    if d.filter_data.adjust_window:
        cv2.imshow(d.filter_data.adjust_window_name, bw)
        # cv2.imshow('blur', blurred)
        # move_to_top('blur')
        # cv2.moveWindow('blur', 300,300)
        move_to_top(d.filter_data.adjust_window_name)

    #Output values as k-v pairs
    mouth = find_contours(bw)
    mouth_area = cv2.contourArea(mouth[0])
    #TODO Depending on eye determine which angle set to use?
    # print(mouth_area)
    rect = cv2.minAreaRect(mouth[0])
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img,[box],0,(0,0,255),2)
    
    output =    {'mouth_area': mouth_area,
                'video_time': w.frame_time.current_time-w.frame_time.start,
                }
    d.set_output(output) 

    if check_set(d.filter_data.adjust_window_name,-1.0) and not d.filter_data.adjust_window:
        cv2.destroyWindow(d.filter_data.adjust_window_name)      

    return img