from .cv2_tools import WindowParameters, move_to_top, check_set, Tuple
from .cv2_filters import *
from .camera_stream import CamData

def filter_stack_color_track(stream_vars: Tuple[np.ndarray,int], w: WindowParameters, d: CamData):
    img = stream_vars[0]
    warped_img = cv2.warpPerspective(img,
                                 d.filter_data.warp_params[2],
                                 (d.filter_data.warp_params[0], d.filter_data.warp_params[1]),
                                 flags=cv2.INTER_LINEAR)
    hsv = filter_hsv(warped_img,
                     lower_hsv_i=d.filter_data.hsv_lower,
                     upper_hsv_i=d.filter_data.hsv_upper,
                     )
    blur = cv2.medianBlur(hsv,d.filter_data.median_blur_kernal)
    grey = filter_black_white(blur,d.filter_data.grey_threshold,invert=False)
    contours = find_contours(grey)

    if len(contours) != 0 and cv2.contourArea(contours[-1]) > d.filter_data.countour_area_min:
        found_moments = cv2.moments(contours[-1])
        if found_moments['m00'] > 0:
            car_x = int(found_moments['m10']/found_moments['m00'])
            car_y = int(found_moments['m01']/found_moments['m00'])
            cv2.drawMarker(warped_img,(car_x,car_y),(0,0,255),2,10,2)

            output = {'car_x': car_x,
                      'car_y': car_y,
            }
            d.set_output(output) 

    if d.filter_data.adjust_window == 1:
        cv2.imshow(d.filter_data.adjust_window_name, hsv)
        move_to_top(d.filter_data.adjust_window_name)
    elif d.filter_data.adjust_window == 2:
        cv2.imshow(d.filter_data.adjust_window_name, grey)
        move_to_top(d.filter_data.adjust_window_name)

    if check_set(d.filter_data.adjust_window_name,-1.0) and not d.filter_data.adjust_window:
        cv2.destroyWindow(d.filter_data.adjust_window_name)     
    
    return warped_img