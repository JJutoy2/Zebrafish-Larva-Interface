# Movement
# w - forward
# s - backward
# a - wide turn left
# d - wide turn right
# q - rotate ccw
# e - rotate cw
from queue import Queue
from .ssh_processing import SSHData, time

def move_pi(left_delta: float,
            left_thresh: float,
            right_delta: float,
            right_thresh: float, 
            dur: float | None
            ) -> str:
    f_spec = '.2f' #Duration should always be less than 4 characters

    if dur is None :
        dur = 0.05
    dur = f'{dur:{f_spec}}'
    if len(dur) > 4: #length characters
        return None
    
    str_root = 'C'

    if abs(left_delta) < left_thresh and abs(right_delta) < right_thresh:
        out = f'{str_root} W {dur}'
    elif left_delta > 0 and right_delta > 0:
        out = f'{str_root} Q {dur}'
    elif left_delta < 0 and right_delta < 0:
        out = f'{str_root} E {dur}'
    else:
        out = f'{str_root} W {dur}'

    print(out)
    return out

# def move_pi(delta_theta: float, 
#             dur: float | None, 
#             fwd_thresh: float = 0.2) -> str:
#     f_spec = '.2f' #Duration should always be less than 4 characters

#     if dur is None :
#         dur = 0.05
#     dur = f'{dur:{f_spec}}'
#     if len(dur) > 4: #length characters
#         return None
    
#     str_root = 'C'
#     if abs(delta_theta) < fwd_thresh:
#         out = f'{str_root} W {dur}'
#     elif delta_theta > 0: 
#         out = f'{str_root} E {dur}'
#     elif delta_theta < 0: 
#         out = f'{str_root} Q {dur}'
#     print(out)
#     return out
    
def pi_car_read_logic(rec: str, ssh_data: SSHData):

    rec = rec.lower()
    # print(rec)
    # print(f'first letter {rec[0]}')
    if rec[0] == 't':
        #Command message signature: 
        #coordinate @ time : ( t _ _ _ _ . _ _ x _ _ _ y _ _ _ )
        split_text = rec.split('x') 
        pi_time = float(split_text[0].removeprefix('t'))
        pi_x = int(split_text[1].split('y')[0])
        pi_y = int(split_text[1].split('y')[1])
        output = {'pi_time': pi_time,
                  'pi_x': pi_x,
                  'pi_y': pi_y
                  }
        ssh_data.set_output(output)
        # print(output)
    elif 'c' in rec:
        #If not a status message, it must be a command validation message
        #go through msg queue and check if it matches with msg received
        # msg IO : ( _ _ _ _ _ _ _ _ C * _ * _ _ _ _ )
        #Assuming nothing gets lost:
        
        msg_item: dict = ssh_data.msg_queue.get()
        # print(f'msg {msg_item['send_msg']}')
        # print(f'same? {str(rec) == str(msg_item['send_msg'])}')
        
        if rec.lower() == msg_item['send_msg'].lower():
            rec_time = time()
            dur = msg_item['send_msg'].split('c')[-1]
            dur = float(dur.split(' ')[-1])
            # print(f'{delta_time}, {data_in.ssh_data.code}')
            # print(f'{rec_time - float(msg_item['send_time']) - dur:.4f}')
            temp_log = {'msg_latency' : f'{rec_time - float(msg_item['send_time']) - dur:.4f}',
                            'msg_rec_time' : f'{rec_time:.2f}',
                            }
            temp_log.update(msg_item)
            ssh_data.log.append(temp_log)
            
            
            



