import sys
import os

# Include tvision directory in path
this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir, "..", ".."))

from src.tvision_proc import start_program, stop_program

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Define program_name and pidfile_name
    program_name = dir_path + "/srv/program"
    pidfile_name = dir_path + "/var/run/program.pid"

    # If not already running, spawn process as instance of program_name, and write it's PID to pidfile_name
    start_program(program_name, pidfile_name)
    # If not already stopped, kill process given by PID in file pidfile_name
    stop_program(pidfile_name)