from threading import Thread
from dataclasses import dataclass
from ..Cameras.camera_stream import CamData
from ..Animations.okr_animation import OKRAnimationData
from ..Animations.okr_sin import OKRSinData
from ..Animations.rotating_static_animation import RotatingStaticAnimationData
from ..Processes.pi_car_interface import move_pi
from .ssh_processing import SSHData, ssh_send
from .env_tools import load_value_from_env
from time import time, sleep
from typing import Tuple, Protocol
import datetime
import csv

@dataclass
class TrialData():
    #TODO change into Cam data fo xicam???
    xi_data: CamData | None = None
    cam_data: CamData | None = None
    okr_data: OKRAnimationData | None = None
    okrs_data: OKRSinData | None = None
    rs_data: RotatingStaticAnimationData | None = None
    ssh_data: SSHData | None = None
    ct_data: CamData | None = None
    
    xi_flag = False
    okr_flag = False
    okrs_flag = False
    rs_flag = False
    ssh_flag = False
    ct_flag = False

    #Timing tests
    #Direction
    timed_dir_flag = False
    timed_dir_idx = 0
    timed_dir_list: list | None = None
    dir_list: list | None = None
    #Speed
    timed_speed_flag = False
    timed_speed_idx = 0
    timed_speed_list: list | None = None
    speed_list: list | None = None
    #Gratings
    timed_gratings_flag = False
    timed_gratings_idx = 0
    timed_gratings_list: list | None = None
    gratings_list: list | None = None
    #Grating Width
    timed_width_flag = False
    timed_width_idx = 0
    timed_width_list: list | None = None
    width_list: list | None = None
    #Grating Radius
    timed_radius_flag = False
    timed_radius_idx = 0
    timed_radius_list: list | None = None
    radius_list: list | None = None
    #Grating Thickness
    timed_thickness_flag = False
    timed_thickness_idx = 0
    timed_thickness_list: list | None = None
    thickness_list: list | None = None

    #Store last eye angle(s)
    last_eye_angles: list[float] | None = None
    last_eye_angle_times: list[float] | None = None
    eye_angle_window: int = 2 #TODO check if this number is suitable? CAN't BE 1

    def __post_init__(self):
        self.xi_flag = True if self.xi_data is not None else False
        self.okr_flag = True if self.okr_data is not None else False
        self.okrs_flag = True if self.okrs_data is not None else False
        self.rs_flag = True if self.rs_data is not None else False
        self.ssh_flag = True if self.ssh_data is not None else False
        self.ct_flag = True if self.ct_data is not None else False

        print(f'Flags: {' xi ' if self.xi_flag else ''}'
            f'{' okr ' if self.okr_flag else ''}'
            f'{' okrs ' if self.okrs_flag else ''}'
            f'{' rs ' if self.rs_flag else ''}'
            f'{' ssh ' if self.ssh_flag else ''}'
            f'{' ct ' if self.ct_flag else ''}'
            )

        self.timed_flag_checker('dir_list','timed_dir_list','timed_dir_flag')
        self.timed_flag_checker('speed_list','timed_speed_list','timed_speed_flag')
        self.timed_flag_checker('gratings_list','timed_gratings_list','timed_gratings_flag')
        self.timed_flag_checker('width_list','timed_width_list','timed_width_flag')
        self.timed_flag_checker('radius_list','timed_radius_list','timed_radius_flag')
        self.timed_flag_checker('thickness_list','timed_thickness_list','timed_thickness_flag')

    def timed_flag_checker(self, var_list_name: str, time_list_name: str, flag_name:str):
        try:
            if getattr(self,var_list_name) is None or getattr(self,time_list_name) is None:
                return
            
            if len(getattr(self,var_list_name)) ==  len(getattr(self,time_list_name)):
                setattr(self,flag_name,True)
                print(f'{flag_name.split('_')[1].capitalize()} changes in Trial')
            else:
                print(f'List lengths are not equivalent, ')
        except Exception as AE:
            print(f'Error {AE}')

    def get_header(self) -> list[str]:
        header = []

        # TODO Refactor
        # def check_mod(module, header: list):
        #     if module is not None:
        #         header.extend([*module.get_output()])

        if self.cam_data is not None:
            header.extend([*self.cam_data.get_output()])

        if self.xi_data is not None:
            header.extend([*self.xi_data.get_output()])

        if self.okr_data is not None:
            header.extend([*self.okr_data.get_output()])
        
        if self.okrs_data is not None:
            header.extend([*self.okrs_data.get_output()])

        if self.rs_data is not None:
            header.extend([*self.rs_data.get_output()])

        if self.ssh_data is not None:
            header.extend([*self.ssh_data.get_output()])
        
        if self.ct_data is not None:
            header.extend([*self.ct_data.get_output()])
        return header
    
    def store_eye_angles(self, input = list[float]) -> bool:
        '''Store eye angles if time is not a duplicate [eye angle time, (left_eye, right_eye)]'''
        #TODO Modify for left and right eye angle
        if self.last_eye_angles == None:
            self.last_eye_angle_times = [input[0]]
            self.last_eye_angles = [(input[1],input[2])]
            return True
        
        if self.last_eye_angle_times[-1] != input[1]:
            # print(self.last_eye_angle_times[-1])
            # print(input[0])
            self.last_eye_angle_times.append(input[1])
            self.last_eye_angles.append((input[1],input[2]))
            return True
        
                #Make space in the window
        if len(self.last_eye_angles) > self.eye_angle_window:
            self.last_eye_angle_times.pop(0)
            self.last_eye_angles.pop(0)

        return False
       
    def calculate_eye_angle_delta(self) -> Tuple[float] | None:
        '''Returns (left_delta, right_delta)'''
        #TODO Make into a more general averaging function
        if self.last_eye_angles is None:
            return None
        if len(self.last_eye_angles) < self.eye_angle_window:
            return None
        
        #Take the average of the eye angle window
        # fwd_avg = sum(self.last_eye_angles[:-1])/self.eye_angle_window 
        # bck_avg = sum(self.last_eye_angles[1:])/self.eye_angle_window 
        # bck_avg = self.last_eye_angles[-1]
        # fwd_avg = self.last_eye_angles[-2]
        # delta = bck_avg - fwd_avg

        left_delta = self.last_eye_angles[-1][0] - self.last_eye_angles[-2][0]
        right_delta = self.last_eye_angles[-1][1] - self.last_eye_angles[-2][1]

        #TODO: Saccade filter?
        # if delta > 60:
        #     delta = 0
        # print(f'{bck_avg}, {fwd_avg}, {delta}')
        
        return (left_delta, right_delta)

@dataclass
class ProcessData:
    #Maybe just combine this into data_in?
    start_time: float | None = None
    last_time: float | None = None
    last_sent_time: float | None = None
    last_sent_duration: float = 0.05
    default_duration: float = 0.08
    current_time: float = None
    end_time: float = None

    eye_angle: float = None
    previous_eye_anlge: float = None
    delta_eye_angle: float = None

    status: bool = True

def create_trial_run_str(post_str: str = 'trial') -> str:
    '''Function to create timestamped title for csv output'''
    current_day_time = datetime.datetime.now()
    time_portion = f'{current_day_time.hour}-{current_day_time.minute}-{current_day_time.second}'
    out_str = f'{current_day_time.date()} {time_portion} {post_str}'
    return out_str

def timed_changes(data: ProcessData, 
                    data_in: TrialData,
                    flag_name: str,
                    index_name: str,
                    var_list_name: str,
                    timed_list_name: str,
                    ) -> any:
    
    if (t_d:=data.current_time - data.start_time) > (t:=getattr(data_in,timed_list_name)[(idx:=getattr(data_in, index_name))]):
        output = getattr(data_in,var_list_name)[idx]
        print(f'{flag_name.split('_')[1].capitalize()} change @ t{t_d:.2f}: {output}')
        setattr(data_in,index_name,idx+1)
        if idx+1 == len(getattr(data_in,timed_list_name)):
            setattr(data_in,index_name,0)
            setattr(data_in,flag_name,False) 
        return output

#TODO Generalize into processing tool?
def processing_module_okr_IO_simple(position: float | int,
                                    direction_change_threshold: float = 80,
                                    direction_threshold: float = 20,
                                    ) -> int:
    '''Calculates whether stimuli should change direction'''
    #TODO determine required calculations? do I need to create temp arrays?
    if position > direction_change_threshold + direction_threshold:
        direction = 1
    elif position < direction_change_threshold - direction_threshold:
        direction = -1
    else:
        direction = 0
    
    return direction

#TODO: Move to its own processing library
def okr_processes(data: ProcessData, data_in: TrialData, display_func):
    direction = None
    if data_in.ssh_flag:
        if (pi_x:= data_in.ssh_data.get_output()['pi_x']) is not None:
            if pi_x != 999:
                direction = display_func(pi_x)


    #Timed Changes
    #Make this to a function so it can be dynamic and involve changing other params too like color, slices, etc
    if data_in.timed_dir_flag:
        direction = timed_changes(data=data,
                        data_in=data_in,
                        flag_name='timed_dir_flag',
                        index_name='timed_dir_idx',
                        var_list_name='dir_list',
                        timed_list_name='timed_dir_list',
                        )

    if data_in.timed_speed_flag:
        spd = timed_changes(data=data,
                    data_in=data_in,
                    flag_name='timed_speed_flag',
                    index_name='timed_speed_idx',
                    var_list_name='speed_list',
                    timed_list_name='timed_speed_list',
                    )
        if spd is not None:
            data_in.okr_data.grating_omega = spd

    if data_in.timed_gratings_flag:
        gratings = timed_changes(data=data,
                    data_in=data_in,
                    flag_name='timed_gratings_flag',
                    index_name='timed_gratings_idx',
                    var_list_name='gratings_list',
                    timed_list_name='timed_gratings_list',
                    )
        if gratings is not None:
            data_in.okr_data.gratings = gratings

    if data_in.timed_width_flag:
        width = timed_changes(data=data,
                    data_in=data_in,
                    flag_name='timed_width_flag',
                    index_name='timed_width_idx',
                    var_list_name='width_list',
                    timed_list_name='timed_width_list',
                    )
        if width is not None:
            data_in.okr_data.grating_space = width

    if data_in.timed_radius_flag:
        radius = timed_changes(data=data,
                    data_in=data_in,
                    flag_name='timed_radius_flag',
                    index_name='timed_radius_idx',
                    var_list_name='radius_list',
                    timed_list_name='timed_radius_list',
                    )
        if radius is not None:
            data_in.okr_data.grating_radius = (radius, radius)

    if data_in.timed_thickness_flag:
        thickness = timed_changes(data=data,
                    data_in=data_in,
                    flag_name='timed_thickness_flag',
                    index_name='timed_thickness_idx',
                    var_list_name='thickness_list',
                    timed_list_name='timed_thickness_list',
                    )
        if thickness is not None:
            data_in.okr_data.grating_thickness = thickness
            
    if data_in.okr_flag:
        if direction is not None:
            data_in.okr_data.grating_direction = direction
            if direction == 0:
                if data_in.okr_data.grating_display == True:
                    data_in.okr_data.grating_display = False
            else:
                if data_in.okr_data.grating_display == False:
                    data_in.okr_data.grating_display = True

    if data_in.rs_flag: 
        if data_in.rs_data.static_display == False: 
            data_in.rs_data.static_display = True
        if direction is not None:
            data_in.rs_data.static_direction = direction
#TODO Create care module IO
# def processing_module_car_out_IO():
    

def setup_processing(data_in: TrialData,
                     data: ProcessData = None,
                     file_name: str = 'Default Run', 
                     run_time: float = 120.0,
                     sampling_rate: float = 25.0,
                     ) -> Thread:
    '''Processes data and pushes writes values into an output file
    run_time is in terms of seconds
    '''
    import os
    from functools import partial
    
    relative_file_path: str = f'{os.getcwd()}\\data\\'

    module_okr_IO_simple_partial = partial(processing_module_okr_IO_simple, 
                                           direction_change_threshold = int(load_value_from_env('OKR_DIR_CHANGE_THRESH')),
                                           direction_threshold = int(load_value_from_env('OKR_DIR_THRESH')))
    
    data = data if data is not None else ProcessData()
    def thread_function(data: ProcessData, data_in: TrialData, sampling_rate: float):
        data.start_time = time()
        count = 0
        with open(relative_file_path+file_name+'.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            
            #Prime headers of csv:
            #Note that .writerow requires an iteratable and putting a str will iterate through chars
            header = ['time',
                    #   'delta_theta'
                      ]
            # for data_module in data_in:
            #     header.extend([*data_module.get_output().keys()])
            header.extend(data_in.get_header())
            writer.writerow(header)
            
            if data_in.ssh_flag:
                right_thresh = float(load_value_from_env('RHT_THRESH'))
                left_thresh = float(load_value_from_env('LFT_THRESH'))

            if data_in.okr_flag:
                #Resets okr angle to 0
                data_in.okr_data.grating_angle = 0

                if data_in.okr_data.grating_display == False:
                    data_in.okr_data.grating_display = True

            if data_in.okrs_flag:
                #Resets okr angle to 0
                data_in.okrs_data.t_time = 0

                if data_in.okrs_data.grating_display == False:
                    data_in.okrs_data.grating_display = True

            # sleep(0.1)

            while data.status:
                data.current_time = time()
                count += 1

                #Data extraction
                ##Extract eye angle
                if data_in.xi_flag:
                    eye_angle_temp: list[float] = [*data_in.xi_data.get_output().values()]
                else:
                    eye_angle_temp: list[float] = [*data_in.cam_data.get_output().values()]
                

                #IO Modules
                ##OKR Signal
                #TODO check what thresholds are
                if (data_in.okr_flag or data_in.rs_flag):
                    okr_processes(data=data, data_in=data_in, display_func=module_okr_IO_simple_partial)                    

                ##Drive Signal
                eye_angle_delta = data_in.calculate_eye_angle_delta()
                if data_in.ssh_flag:
                    if eye_angle_delta is not None:
                        if data.last_sent_time is None:
                            delta_time = data.default_duration
                        else:
                            #delta_time should never be greater than 9.99 seconds
                            delta_time = time() - data.last_sent_time
                        
                        #TODO fix inputs to move pi
                        mv_msg = move_pi(left_delta = eye_angle_delta[0],
                                         left_thresh = left_thresh,
                                         right_delta = eye_angle_delta[1],
                                         right_thresh = right_thresh,
                                         dur = delta_time,
                                         )
                        
                        if data_in.ssh_data.msg_queue.qsize() < 3:
                            ssh_send(f'{data_in.ssh_data.code:8d}{mv_msg}', data_in.ssh_data)
                            data_in.ssh_data.code += 1
                        #TODO Manage q
                        # else:
                        #     print('q too big')
                        data.last_sent_time = time()

                #Check and store data
                if data_in.store_eye_angles(eye_angle_temp):
                    data_in.cam_data.get_output()
                    data_line = [round(data.current_time-data.start_time,4)]
                    # data_line.extend([eye_angle_delta] if eye_angle_delta is not None else [0])
                    data_line.extend(eye_angle_temp)
                    if data_in.okr_flag: data_line.extend([*data_in.okr_data.get_output().values()])
                    if data_in.okrs_flag: data_line.extend([*data_in.okrs_data.get_output().values()])
                    if data_in.ssh_flag: data_line.extend([*data_in.ssh_data.get_output().values()])
                    if data_in.ct_flag: data_line.extend([*data_in.ct_data.get_output().values()])
                    writer.writerow(data_line)

                #Sleep at sampling rate - elapsed time to get close to sampling rate
                if data.last_time is not None:
                    elapsed_time = data.current_time-data.last_time
                    if elapsed_time < (1/sampling_rate):
                        delay = (1/sampling_rate)-elapsed_time
                        sleep(delay)
                else:
                    sleep(1/sampling_rate)
                
                data.last_time = time()

                #Terminating condition
                if data.current_time - data.start_time >= run_time:
                    break

            #Trial Post Process
            if data_in.okr_flag:
                data_in.okr_data.grating_display = False 
            if data_in.okrs_flag:
                data_in.okrs_data.grating_display = False 
            if data_in.rs_flag:
                data_in.rs_data.static_display = False 
            if data_in.ssh_flag:
                ssh_send(f'{data_in.ssh_data.code:8d}{'C X 0.05'}', data_in.ssh_data)

            #Display Trial Stats
            data.end_time = data.last_time
            sampling_rate = count/(data.end_time - data.start_time)
            print(f'Data Sampled: {count}')
            print(f'Average Sampling Rate: {sampling_rate:.2f}')
            
    processing_thread = Thread(target=thread_function, 
                               kwargs={'data_in': data_in,
                                       'data': data,
                                       'sampling_rate': sampling_rate,
                                       }
                                       )
    # processing_thread.start()
    return processing_thread

if __name__ == "__main__":
    print(create_trial_run_str('Fish 0 Omega 1'))