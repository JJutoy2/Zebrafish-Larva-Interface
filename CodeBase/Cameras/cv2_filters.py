import cv2
from dataclasses import dataclass
import numpy as np

# TODO Include adjust window location so it can be loadable
# Keep filters as independent from data objects as possible for modularity
@dataclass
class FilterData:
    adjust_window: bool | int = True
    adjust_window_name: str | None = None
    countour_area_min: int | None = None # For countour filter
    countour_area_max: int | None = None # For contour filter
    bb: list[int] | None = None # For crop filter
    grey_threshold: int = 122 # For black white filter
    hsv_lower: list[int] | None = None  # For HSV Filter
    hsv_upper: list[int] | None = None # For HSV Filter
    warp_params: list[int, int, any] | None = None #For Warp filter
    median_blur_kernal: int | None = 1 #for median blur
    fish_eye: int = 0 #0 left, 1 right
    show_eyes: bool = True
    fish_subjects: int | None = None
    fish_columns: int | None = None
    bb_w_inc: int | None = None
    bb_h_inc: int | None = None
    v_dis_thresh: int | None = None
    area_thresh: float | None = None
    bb_init: bool | None = None

def select_ROI(img, window_name:str):
    print("Setting ROI...")
    roi_win_name = f'{window_name} ROI Window'
    try:
        cv2.namedWindow(roi_win_name)
        cv2.setWindowProperty(roi_win_name,cv2.WND_PROP_TOPMOST,1.0)
        bb = cv2.selectROI(windowName=roi_win_name,
                            img = img,
                            fromCenter=False,
                            showCrosshair=True)
        cv2.destroyWindow(roi_win_name)
        print(f'Bounding Box: {bb}')
    except:
        pass
    if bb.count(0) or bb is None:
        bb = None
        print("ROI Not set")
    return bb
    
def filter_black_white(img, thresh_val: int = 122, invert: bool = True) -> np.ndarray:
    '''Applies black and white filter to cv2 image, 
    '''
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grey = cv2.threshold(grey,thresh_val,255,cv2.THRESH_BINARY)[1]
    if invert:
        grey = (255-grey)
   
    return grey

def filter_crop(img, bb):
    '''Crops image based on Bounding Box (bb) values'''
    if bb is not None:
        (x, y, w, h) = [int(v) for v in bb]
        try:
            cropped = img[y:y+h,x:x+w]
        except:
            bb = None
            print("ROI Window Failure - ROI Set to NONE")
    else:
        cropped = img
    return cropped


def filter_hsv(img, lower_hsv_i: list[int], upper_hsv_i: list[int]):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #Convert list into np arrays
    lower_hsv = np.array(lower_hsv_i)
    upper_hsv = np.array(upper_hsv_i)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    # Apply the mask on the image to extract the original color
    masked_frame = cv2.bitwise_and(img, img, mask=mask)
    # cv2.imshow('HSV', masked_frame)
    return masked_frame

def set_warp_params(point: list[list[int]]):
    '''Returns max_width, max_height, warp_matrix from a given set of four points'''
    #A = 0, B = 1, C = 2, D = 3
    width_AD = np.sqrt(((point[0][0] - point[3][0]) ** 2) + ((point[0][1] - point[3][1]) ** 2))
    width_BC = np.sqrt(((point[1][0] - point[2][0]) ** 2) + ((point[1][1] - point[2][1]) ** 2))
    max_width = max(int(width_AD), int(width_BC))    
    
    height_AB = np.sqrt(((point[0][0] - point[1][0]) ** 2) + ((point[0][1] - point[1][1]) ** 2))
    height_CD = np.sqrt(((point[2][0] - point[3][0]) ** 2) + ((point[2][1] - point[3][1]) ** 2))
    max_height = max(int(height_AB), int(height_CD))
    
    input_pts = np.float32([point[0], point[1], point[2], point[3]])
    output_pts = np.float32([[0, 0],
                            [0, max_height - 1],
                            [max_width - 1, max_height - 1],
                            [max_width - 1, 0]])
    warp_matrix = cv2.getPerspectiveTransform(input_pts,output_pts)

    return (max_width, max_height, warp_matrix)

#TODO Clean and document UNUSED
# def find_contours(img, bb, img2contour, area_min: int = 0, area_max: int = 25) -> list:
#         '''Find contour data based on given img. Keys: area_min(int), area_max(int)'''

#         contours, _ = cv2.findContours(img2contour, 
#                                         # cv2.RETR_EXTERNAL, 
#                                         # cv2.RETR_CCOMP, 
#                                         # cv2.RETR_LIST,
#                                         cv2.RETR_TREE,
#                                         # cv2.CHAIN_APPROX_SIMPLE
#                                         cv2.CHAIN_APPROX_NONE
#                                         )

#         cnts = []
#         try:            
#             areas = [cnt for cnt in contours if area_min < cv2.contourArea(cnt) < area_max]
            
#             for a in areas:
#                 x,y,w,h = cv2.boundingRect(a)
#                 if bb is not None:
#                     x = x + bb[0]
#                     y = y + bb[1]
#                     # print(x,y,cv2.contourArea(a))
#                 cnts.append([x,y,cv2.contourArea(a)])
#                 cv2.circle(img, (int(x+w/2),int(y+h/2)), 1, (255,0, 0), 5)
#             # self.x_com, self.y_com, _ = min(cnts, key=lambda x: x[2])
#             # print(self.x_com, self.y_com)
#         except:
#             print("No contours found!")
#         # print(cnts)
#         # self.cnts.append(cnts)
#         # print(self.cnts)
#         return cnts

def find_contours(grey_frame: any) -> list:
    """Finds the contours of a greyed image

    Args:
        grey_frame (any): a GREY Image

    Returns:
        list: list of contours in ascending order
    """
    cnts, _ = cv2.findContours(grey_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return sorted(cnts, key=cv2.contourArea)

#TODO Clean and document
def find_eye_angle(img, img2find, bb, eye:int=0) -> int:
    contours = cv2.findContours(img2find, mode=cv2.RETR_EXTERNAL,
                                # method=cv2.CHAIN_APPROX_SIMPLE, #SIMPLE HAS TOO MUCH JITTER
                                method=cv2.CHAIN_APPROX_NONE #NONE IS BEST FOR REDUCING JITTER
                                )
    contours = contours[0]

    try: 
        big_contour = max(contours, key=cv2.contourArea)
        # (xc,yc),(d1,d2),angle = cv2.fitEllipseDirect(big_contour)  
        (xc,yc),(d1,d2),angle = cv2.fitEllipse(big_contour)  

        
        if eye == 0:
            if angle > 90:
                angle = 180 - angle
        else:
            if angle < 90:
                angle = 180 + angle
                    
        cv2.ellipse(img, (round(xc+bb[0]),round(yc+bb[1])), (round(d1/2),round(d2/2)), 
                    angle, 0, 360, (0,255,0), 2, lineType=cv2.LINE_AA) # For visual display of ellipse on img
        # cv2.line(img,(round(xc+bb[0]),round(yc+bb[1])),(round(xc+bb[0]-round(d1)),round(yc+bb[1])),(0,255,0),2)
        nX = d2*np.cos(np.deg2rad(angle))
        nY = d2*np.sin(np.deg2rad(angle))
        cv2.line(img,(round(xc+bb[0]),round(yc+bb[1])),(round(xc+bb[0]-nX),round(yc+bb[1]-nY)),(255,255,0),2, lineType=cv2.LINE_AA)
    except Exception as E:
        print(f'Exception in fish eye filter: {E}')
        angle = 0
    return angle

def find_eye_angles(img, img2find, bb) -> int:
    contours = cv2.findContours(img2find, mode=cv2.RETR_EXTERNAL,
                                # method=cv2.CHAIN_APPROX_SIMPLE, #SIMPLE HAS TOO MUCH JITTER
                                method=cv2.CHAIN_APPROX_NONE #NONE IS BEST FOR REDUCING JITTER
                                )
    contours = contours[0]
    contours = sorted(contours, key=cv2.contourArea)

    def fish_eye_id(angle_1, x_1, angle_2, x_2):
        #potential case of them being equal
        if x_1 < x_2:
            # x_1 == left eye
            # x_2 == right eye
            left_eye = angle_1
            right_eye = angle_2

            # if left_eye > 90:
            #     left_eye = 180 - left_eye
            #     angle_1 = left_eye
            # if right_eye < 90:
            #     right_eye = 180 + right_eye
            #     angle_2 = right_eye
        else:
            # x_1 == right eye
            # x_2 == left eye
            left_eye = angle_2
            right_eye = angle_1

        if left_eye < 90:
            left_eye = 180 + left_eye
        # angle_2 = left_eye
        if right_eye < 90:
            right_eye = 180 + right_eye
        # angle_1 = right_eye
        return angle_1, angle_2, left_eye, right_eye

    try: 
        eye_1 = contours[-1]
        eye_2 = contours[-2]
        # (xc,yc),(d1,d2),angle = cv2.fitEllipseDirect(big_contour)  
        (xc_1,yc_1),(d1_1,d2_1),angle_1 = cv2.fitEllipse(eye_1)  
        (xc_2,yc_2),(d1_2,d2_2),angle_2 = cv2.fitEllipse(eye_2)  

        # EYE filter based on xc
        (angle_1, angle_2, left_eye, right_eye) = fish_eye_id(angle_1,xc_1,angle_2,xc_2)
                    
        cv2.ellipse(img, (round(xc_1+bb[0]),round(yc_1+bb[1])), (round(d1_1/2),round(d2_1/2)), 
                    angle_1, 0, 360, (0,255,0), 2, lineType=cv2.LINE_AA) # For visual display of ellipse on img
        cv2.ellipse(img, (round(xc_2+bb[0]),round(yc_2+bb[1])), (round(d1_2/2),round(d2_2/2)), 
                    angle_2, 0, 360, (0,255,0), 2, lineType=cv2.LINE_AA) # For visual display of ellipse on img

        # cv2.line(img,(round(xc+bb[0]),round(yc+bb[1])),(round(xc+bb[0]-round(d1)),round(yc+bb[1])),(0,255,0),2)
        # nX = d2*np.cos(np.deg2rad(angle))
        # nY = d2*np.sin(np.deg2rad(angle))
        # cv2.line(img,(round(xc+bb[0]),round(yc+bb[1])),(round(xc+bb[0]-nX),round(yc+bb[1]-nY)),(255,255,0),2, lineType=cv2.LINE_AA)
    except Exception as E:
        print(f'Exception in fish eye filter: {E}')
        left_eye = 0 
        right_eye = 0
    return (180 - left_eye, 180 - right_eye)

def find_eye_areas(img, img2find, bb, show_eyes, v_dis_thresh, area_thresh):

    def fish_eye_id(angle_1, x_1, angle_2, x_2):
        #potential case of them being equal
        if x_1 < x_2:
            # x_1 == left eye
            # x_2 == right eye
            left_eye = angle_1
            right_eye = angle_2

        else:
            # x_1 == right eye
            # x_2 == left eye
            left_eye = angle_2
            right_eye = angle_1

        if left_eye < 90:
            left_eye = 180 + left_eye
        # angle_2 = left_eye
        if right_eye < 90:
            right_eye = 180 + right_eye
        # angle_1 = right_eye
        return angle_1, angle_2, left_eye, right_eye

    try: 
        contours = cv2.findContours(img2find, mode=cv2.RETR_EXTERNAL,
                            # method=cv2.CHAIN_APPROX_SIMPLE, #SIMPLE HAS TOO MUCH JITTER
                            method=cv2.CHAIN_APPROX_NONE #NONE IS BEST FOR REDUCING JITTER
                            )
        contours = contours[0]
        contours = sorted(contours, key=cv2.contourArea)
        conts = len(contours)
        nan = ['nan', 'nan']
        if conts == 0: return nan
        if conts == 1: return nan

        eye_1 = contours[-1]
        eye_2 = contours[-2]

        (xc_1,yc_1),(d1_1,d2_1),angle_1 = cv2.fitEllipse(eye_1)  
        (xc_2,yc_2),(d1_2,d2_2),angle_2 = cv2.fitEllipse(eye_2) 

        #check how far appart vertically the eyes are
        if abs(yc_1 - yc_2) > v_dis_thresh:
            return nan

        # eye_area_diff = cv2.contourArea(eye_1)-cv2.contourArea(eye_2)
        eye_1_area = cv2.contourArea(eye_1)
        eye_2_area = cv2.contourArea(eye_2)

        if eye_1_area > area_thresh or eye_2_area > area_thresh:
            return nan
        cv2.rectangle(img, (int(bb[0]), int(bb[1])), \
          (int(bb[0]+bb[2]), int(bb[1]+bb[3])), (255,255,0) , 2)
         
        if show_eyes:

            # EYE filter based on xc
            (angle_1, angle_2, left_eye, right_eye) = fish_eye_id(angle_1,xc_1,angle_2,xc_2)
                        
            cv2.ellipse(img, (round(xc_1+bb[0]),round(yc_1+bb[1])), (round(d1_1/2),round(d2_1/2)), 
                        angle_1, 0, 360, (0,255,0), 1, lineType=cv2.LINE_AA) # For visual display of ellipse on img
            cv2.ellipse(img, (round(xc_2+bb[0]),round(yc_2+bb[1])), (round(d1_2/2),round(d2_2/2)), 
                        angle_2, 0, 360, (0,255,0), 1, lineType=cv2.LINE_AA) # For visual display of ellipse on img
            # Area

        out = [eye_1_area, eye_2_area]
        return out
        # ALIGNMENT Processing
        # print(f'Count:{len(contours)}')
        

    except Exception as E:
        # print(f'Exception in fish eye filter: {E}')
        return ()
    # Return eye data
