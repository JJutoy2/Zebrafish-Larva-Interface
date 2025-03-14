import subprocess

def copy_text_to_clipboard(copy_text: str, output_text: str = '---> copied to clipboard'):
    print(output_text)
    return subprocess.run('clip', text=True, input=copy_text)

def increment(var_name: str, 
              variable: float | int | None,
              upper_limit: float | int | None = None,
              lower_limit: float | int | None = None,
              delta: float | int = 1
              ):
    '''Subtracts if given lower limit'''
    if upper_limit is None and lower_limit is not None:
        if variable > lower_limit:
            variable -= delta
    if upper_limit is not None and lower_limit is None:
        if variable < upper_limit:
            variable += delta

    print(f'{var_name}: {variable}')
    return variable