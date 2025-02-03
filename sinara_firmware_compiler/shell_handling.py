import os
import subprocess
import sys


def shell_wrapper(
    command : str,
    strict  : bool, # if True, raise exception when subprocess.run().returncode != 0
    cwd     : str = None, # can be a relative path, command will be executed inside that directory
    output_to_terminal : bool = False, # output will not be captured by python and will only appear
                       # in the terminal, provided that you ran a python script from the terminal
):
    if cwd != None:
        cwd = os.path.realpath(cwd, strict=True)
    opt = {"capture_output" : True}
    if output_to_terminal:
        opt = {"stdout" : sys.stdout, "stderr" : sys.stderr}
    r = subprocess.run(
        args  = command,
        cwd   = cwd,
        shell = True,
        text  = True,
        **opt
    )
    if strict and r.returncode != 0:
        if cwd == None:
            cwd = os.path.realpath(".", strict=True)
        message = f"Error when running the following shell command with sinara.shell_wrapper() -> subprocess.run():" \
        + f"\ncd \"{cwd}\" && {command}" \
        + f"\nreturncode: {r.returncode}\nstdout: {r.stdout}\nstderr: {r.stderr}"
        raise Exception(message)
    return r