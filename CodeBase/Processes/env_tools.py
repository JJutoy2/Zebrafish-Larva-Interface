from dotenv import load_dotenv, set_key, get_key
import json
import os

def load_env(env_file_name_path: str = None):
    #TODO include file path logic so different environments can be loaded
    try:
        load_dotenv()
    except TypeError:
        print("Environment not loaded")
        return

def load_list_from_env(key: str, env_path:str = '.env', text:bool=False, flt:bool=False) -> list | None:
    '''Loads a list from environment variables'''
    try:
        if text:
            return [x for x in get_key(env_path,key).split(',')]
        if flt:
            return [float(x) for x in get_key(env_path,key).split(',')]
        return [int(x) for x in get_key(env_path,key).split(',')]
    except Exception as e:
        print(e)
        return None

def load_value_from_env(key: str, env_path:str = '.env', to_dict: bool = False) -> any:
    #TODO Add param to choose how to output value ie: str/int/float etc.
    '''Loads a list from environment variables'''
    try:
        if to_dict:
            return json.loads(get_key(env_path, key)) 
        return get_key(env_path, key)
    except Exception as e:
        print(e)
        return None
    
def save_list_to_env(key: str, input_list: list, env_path:str = '.env'):
    value = ','.join([str(v) for v in input_list])
    print(f'Saved {input_list} to {key}')
    set_key(env_path, key, value)

def save_value_to_env(key: str, value: any, env_path:str = '.env'):
    print(f'Saved {value} to {key}')
    set_key(env_path, key, f'{value}')