from paramiko import SSHClient, AutoAddPolicy, ChannelFile
from threading import Lock, Thread
from queue import Queue
from time import time, sleep
from dataclasses import dataclass
from typing import Callable

from .env_tools import load_value_from_env

@dataclass
class SSHData:
    output: dict = None
    output_lock: Lock = None
    output_parser: Callable | None = None
    ssh_kwargs: dict | None = None
    ssh_command: str | None = None
    read_logic: Callable | None = None
    # send_interval: float = 0.6
    connected: bool = False
    connected_start_time: float | None = None
    log: list | None = None
    # last_sent = 0
    stdin: ChannelFile = None
    stderr: ChannelFile = None
    stdout: ChannelFile = None
    msg_queue: Queue = Queue()
    client = SSHClient()
    channel_nbytes: int = 16
    encoding: str = 'utf-8'
    code: int = 0
    
    def __init__(self,
                ):
        self.output_lock = Lock()
        self.log = []
        self.ssh_kwargs = load_value_from_env('SSH_RPI_KWARGS', to_dict=True)
        self.ssh_command = load_value_from_env('SSH_COMMAND')   
        self.client.set_missing_host_key_policy(AutoAddPolicy())   

    def get_output(self):
        with self.output_lock:
            return self.output
        
    def set_output(self, out:dict):
        with self.output_lock:
            self.output = out

def ssh_connect(ssh_data: SSHData) -> bool:
    """SSH connection to rpi
    """
    # Wait for connection message from pi
    connected_msg = load_value_from_env('SSH_CONNECT_MSG')
    error_msg = load_value_from_env('SSH_ERROR_MSG')
    try:
        ssh_data.client.connect(**ssh_data.ssh_kwargs)
        ssh_data.stdin, ssh_data.stdout, ssh_data.stderr = ssh_data.client.exec_command(ssh_data.ssh_command, 
                                                                          timeout=5.0)
        while not ssh_data.connected:
            rec = ssh_data.stdout.channel.recv(ssh_data.channel_nbytes).decode(ssh_data.encoding)

            if connected_msg in rec:
                print(f"SUCCESS! Pi @ {ssh_data.ssh_kwargs['hostname']} Connected")
            elif error_msg in rec:
                print(f"ERROR! Pi @ {ssh_data.ssh_kwargs['hostname']} Please kill SSH")
            ssh_data.connected = True
            ssh_data.connected_start_time = time()
    except Exception as E:
        print(f"Warning: {E}")

def ssh_disconnect(ssh_data: SSHData) -> bool:
    if ssh_data.connected == False:
        print(f'SSH @ {ssh_data.ssh_kwargs['hostname']} already disconnected')
        return
    try:
        ssh_data.connected = False
        ssh_data.client.close()
        # ssh_data.stdout.close()
        # ssh_data.stderr.close()
        # ssh_data.stdin.close()
        print(f'SUCCESS! Pi @ {ssh_data.ssh_kwargs['hostname']} '
              f'Disconnected: {(time()-ssh_data.connected_start_time) if ssh_data.connected_start_time is not None else 0.0:.1f}')
    except Exception as E:
        print(f"Warning: {E}")

def ssh_send(send_msg: str,
             ssh_data: SSHData,
             ) -> None:
    send_msg = send_msg.lower()
    if not ssh_data.connected:
        print(f'SSH @ {ssh_data.ssh_kwargs['hostname']} not connected.')
        return

    if validate_msg(send_msg, ssh_data.encoding, ssh_data.channel_nbytes):
        if 'c' in send_msg:
            #Only track command messages
            que_data = {'send_time': time(),
                        'send_msg': send_msg,
                        }
            ssh_data.msg_queue.put(que_data)
        ssh_data.stdin.write(send_msg)
        ssh_data.stdin.flush()
        # print(f'Sent {send_msg}')

def ssh_read(ssh_data: SSHData):
    try:
        rec = ssh_data.stdout.channel.recv(ssh_data.channel_nbytes)
        rec = rec.decode(ssh_data.encoding)
        # print(rec)
        #TODO Figure out a better solution than loading from env everytime
        if load_value_from_env('SSH_DISCONNECT_MSG') in rec: 
            ssh_disconnect(ssh_data)
        if load_value_from_env('SSH_ERROR_MSG') in rec:
            print('Received ERROR SIGNAL: Please kill SSH')
        ssh_data.read_logic(rec, ssh_data)
    except IndexError:
        pass
    except Exception as E:
        print(f"Warning: {E}")

def validate_msg(msg: str, encoding: str, nbytes: int) -> bool:
    if (msg_l := len(msg.encode(encoding))) == nbytes:
        return True
    else:
        print(f'WARNING| msg: {msg} has incorrect length {msg_l}({nbytes})')
        return False  

def setup_ssh(read_logic: Callable):
    #Import necessary subfunctions

    ssh_data = SSHData()
    ssh_data.read_logic = read_logic
    ssh_connect(ssh_data)

    def ssh_thread_function(ssh_data: SSHData):
        while ssh_data.connected:
            ssh_read(ssh_data)

    ssh_thread = Thread(target=ssh_thread_function, 
                        args=[ssh_data],
                        )
    
    return (ssh_data, None, ssh_thread)