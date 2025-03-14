from ..Animations.animations import*
from threading import Lock
import numpy as np

@dataclass
class RotatingStaticAnimationData(AnimationData):
    fish_roi_radius: int = 8
    fish_roi_radius_display: bool = True 
    fish_roi_color: Tuple[int,int,int] = (255,255,255)
    static_display: bool = True
    static_direction: int = 1
    static_color: Tuple[int,int,int] = (255,255,255)
    static_omega: float = 60.0 #Degreees per second
    static_angle: float = 0.0
    static_prob: float = 0.5
    static_prob_delta: float = 0.01
    static_img: np.ndarray | None = None
    static_center: Tuple[int] | None = None
    output: dict | None = None
    output_lock: Lock = Lock()

    def get_output(self):
        with self.output_lock:
            return self.output
        
    def set_output(self, out:dict):
        with self.output_lock:
            self.output = out

    def update(self):
        if self.static_img is None:
            r = int(np.sqrt(((self.canvas.shape[0])/2)**2 + ((self.canvas.shape[1])/2)**2))
            d = 2 * r
            self.static_img = cv2.resize(self.canvas, (d,d)) 
            self.static_center = (r, r)
        img = self.static_img
        img[...] = np.array(self.background_color).astype(np.uint8) #Important to clear canvas!
        
        #Vectorized instead of for loop!
        randomized_img = np.random.random((img.shape[1],img.shape[0]))
        img[randomized_img > 1-self.static_prob] = 255


        # img[...] = randomized_img 

    # def __repr__(self):
    #     return (f'data.fish_roi_color = {self.fish_roi_color}\n'
    #             f'data.fish_roi_radius = {self.fish_roi_radius}\n'
    #             f'data.grating_color = {self.static_color}\n'
    #             f'data.grating_radius = {self.grating_radius}\n'
    #             f'data.grating_omega = {self.static_omega}\n'
    #             f'data.grating_space = {self.grating_space}\n'
    #             f'data.gratings = {self.gratings}\n'
    #             )
    # def save_settings(self):
    # def load_settings(self):


def okr_animation(animation_var: Tuple[float, int], data: RotatingStaticAnimationData):

    if data.static_display:

        #Calculate the change in angle based on the change in time
        delta_theta = data.static_direction * data.static_omega * animation_var[0]

        #Calculate and save current angle of the statics
        data.static_angle += delta_theta

        # MODIFY if other values are required
        out_dict = {'static_angle': data.static_angle,
                    'static_omega': data.static_omega,
                    }
        data.set_output(out_dict)

        #Create rotation matrix
        M = cv2.getRotationMatrix2D((data.static_center),data.static_angle,1) #Takes angles in degrees

        img = data.static_img
        rotated_img = cv2.warpAffine(img,M,(data.static_img.shape[0],data.static_img.shape[1])) 
        
        #Prevent variable from reaching limit
        if (a_ang:= abs(data.static_angle)) > 360:
            data.static_angle = a_ang - data.static_direction*360

        #Fit the rotated image into the cavases dimensions
        x_i = (data.static_img.shape[1] - data.canvas.shape[1]) / 2
        x_f = x_i + data.canvas.shape[1]
        y_i = (data.static_img.shape[0] - data.canvas.shape[0]) / 2
        y_f = y_i + data.canvas.shape[0]
        img = rotated_img[int(y_i):int(y_f),int(x_i):int(x_f)] #slices rotated static img to canvas size
    else:
        img = data.canvas
        img[...] = np.array(data.background_color).astype(np.uint8) #Important to clear canvas!

    #Fish Radius Circle
    if data.fish_roi_radius > 0 and data.fish_roi_radius_display: 
        cv2.circle(img, data.center, 
                    data.fish_roi_radius, 
                    data.fish_roi_color, 
                    -1, 
                    lineType=cv2.LINE_AA)
    return img

def setup_rotating_static(window_parms: WindowParameters | None = None, 
                          ) -> Tuple[RotatingStaticAnimationData, WindowParameters, Thread]:
    '''Quick creation of okr animation that returns its settings, window, and animate function'''

    from ..Bindings.rotating_static_bindings import rotating_static_binds #importing here prevents import loop
    from ..Processes.env_tools import load_list_from_env
    
    try: 
        loc = load_list_from_env('LOC_RS')
    except: 
        loc: Tuple[int,int] = (0,0)
    window_parms = window_parms if window_parms is not None else WindowParameters('Rotating Static Frame', loc)
    data = RotatingStaticAnimationData()
    animate = okr_animation
    bindings = rotating_static_binds
    
    animation_thread = animate_canvas(data=data, 
                            animate=animate,
                            window_parms=window_parms,
                            bindings=bindings 
                            )
    return (data, window_parms, animation_thread)

if __name__ == '__main__':
    setup_rotating_static()[2].start()