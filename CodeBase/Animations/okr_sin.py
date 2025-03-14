from typing import Any
from ..Animations.animations import *
from threading import Lock
from dataclasses import field


@dataclass
class OKRSinData(AnimationData):
    fish_roi_radius: int = 16
    fish_roi_radius_display: bool = True 
    fish_roi_color: Tuple[int,int,int] = (255,255,255)
    grating_display: bool = True
    grating_direction: int = 1
    grating_angle: float = 0.0 #Degrees
    grating_omega: float = 1.0 #Degreees per second
    gratings: int = 5
    grating_radius: Tuple[int, int] = (240, 240)
    grating_color: Tuple[int,int,int] = (255,255,255)
    grating_space: float = 0.5 #0.0 - 1.0 value representing fraction of a gratings angle filled
    grating_theta_amp: float = 30.0
    output: dict | None = None
    output_lock: Lock = Lock()
    okr_img: np.ndarray | None = None
    update_list: list[str] = field(default_factory=lambda: ['grating_radius', 'gratings', 'grating_space', 'grating_color'])
    t_time: float = 0.0

    def update(self):
        if self.okr_img is None:
            self.okr_img = np.copy(self.canvas)
        img = self.okr_img
        img[...] = np.array(self.background_color).astype(np.uint8) #Important to clear canvas!

    
        for arc in range(self.gratings):
            cv2.ellipse(self.okr_img,
                        self.center,
                        self.grating_radius,
                        arc*360/self.gratings,
                        0,
                        360/self.gratings*self.grating_space,
                        self.grating_color,
                        -1,
                        lineType=cv2.LINE_AA)     
            
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if self.canvas is not None:
            if name in self.update_list:
                self.update()
        return

    def get_output(self):
        with self.output_lock:
            return self.output
        
    def set_output(self, out:dict):
        with self.output_lock:
            self.output = out
           
    def __repr__(self):
        return (f'data.fish_roi_color = {self.fish_roi_color}\n'
                f'data.fish_roi_radius = {self.fish_roi_radius}\n'
                f'data.grating_color = {self.grating_color}\n'
                f'data.grating_radius = {self.grating_radius}\n'
                f'data.grating_omega = {self.grating_omega}\n'
                f'data.grating_space = {self.grating_space}\n'
                f'data.gratings = {self.gratings}\n'
                )
    # def save_settings(self):
    # def load_settings(self):


def okr_sin_animation(animation_var: Tuple[float, int], data: OKRSinData):
        
    if data.grating_display:
        #Calculate the change in angle based on the change in time
        data.t_time += animation_var[0]
        grating_angle = data.grating_theta_amp * np.sin(data.grating_omega * data.t_time * (2 * np.pi))
        data.grating_angle = grating_angle
        # print(data.t_time)
        #Calculate and save current angle of the gratings
        # data.grating_angle = delta_theta

        #Create rotation matrix
        M = cv2.getRotationMatrix2D((data.center),data.grating_angle,1) #Takes angles in degrees
        
        #Prevent variable from overloading
        # if (a:= abs(data.grating_angle)) > 360:
        #     data.grating_angle = a - 360 if data.grating_angle > 0 else -1 * (a - 360)
        
        img = data.okr_img
    
        display_img = cv2.warpAffine(img,M,data.size) 
    else:
        display_img = data.canvas
        display_img[...] = np.array(data.background_color).astype(np.uint8) #Important to clear canvas!

    #Fish Radius Circle
    if data.fish_roi_radius > 0 and data.fish_roi_radius_display: 
        cv2.circle(display_img, data.center, 
                    data.fish_roi_radius, 
                    data.fish_roi_color, 
                    -1, 
                    lineType=cv2.LINE_AA)
    
    cv2.putText(display_img, 
                f't={data.grating_angle:.0f}', 
                (int(data.center[0]*2*.8), data.center[1]*2-90), 
                cv2.FONT_HERSHEY_PLAIN,  
                2, 
                (255,255,255), 
                2, 
                cv2.LINE_AA) 
    
    cv2.putText(display_img, 
                f'o={data.grating_omega:.2f}', 
                (int(data.center[0]*2*.8), data.center[1]*2-60), 
                cv2.FONT_HERSHEY_PLAIN,  
                2, 
                (255,255,255), 
                2, 
                cv2.LINE_AA) 
    
    cv2.putText(display_img, 
            f'A={data.grating_theta_amp}', 
            (int(data.center[0]*2*.8), data.center[1]*2-30), 
            cv2.FONT_HERSHEY_PLAIN,  
            2, 
            (255,255,255), 
            2, 
            cv2.LINE_AA) 
        
        
    # MODIFY if other values are required
    out_dict = {'grating_angle': data.grating_angle,
                'grating_omega': data.grating_omega,
                }
    data.set_output(out_dict)

    return display_img

def setup_okr_sin(window_parms: WindowParameters | None = None,
              ) -> Tuple[OKRSinData, WindowParameters, Thread]:
    '''Quick creation of okr animation that returns its settings, window, and animate function'''

    from ..Bindings.okr_sin_bindings import okr_sin_binds #importing here prevents import loop
    from ..Processes.env_tools import load_value_from_env, load_list_from_env
    try: 
        loc = load_list_from_env('LOC_OKR')
    except: 
        loc: Tuple[int,int] = (0,0)
    
    window_parms = window_parms if window_parms is not None else WindowParameters('OKR Frame', loc)
    window_parms.fullscreen = bool(int(load_value_from_env('OKR_FULLSCREEN')))
    data = OKRSinData()
    data.grating_display = False
    data.fish_roi_radius = int(load_value_from_env('OKR_FIS_RAD'))
    
    animate = okr_sin_animation
    bindings = okr_sin_binds
    
    animation_thread = animate_canvas(data=data, 
                            animate=animate,
                            window_parms=window_parms,
                            bindings=bindings 
                            )
    return (data, window_parms, animation_thread)

