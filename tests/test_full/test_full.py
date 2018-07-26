import sys
import os
from time import sleep

# Include tvision directory in path
this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir, "..", ".."))

from src.tvision_io import load_config, write_to_socket
from src.tvision_proc import start_program, stop_program
from src.tvision_time import utc_seconds_now, utc_seconds_timestamp, max_socket_timeout


MOD = 240
TIMEOUT_BUFFER = 30
LOOP_DELAY = 1
CONFIG_RELOAD_DELAY = 200 // LOOP_DELAY


if __name__ == '__main__':
    # Read configuration file path from input argument
    config_path = sys.argv[1]
    # Initialize step number and loop iteration counts since last reload of configuration file
    step_num = 0
    reload_count = 0
    first_seconds = utc_seconds_now()
    # Loop indefinitely until interrupted
    while True:
        now_seconds = (utc_seconds_now() - first_seconds) % MOD
        if reload_count % CONFIG_RELOAD_DELAY == 0:
            # Reload configuration file
            config = load_config(config_path)
            # Using current time, find position in the day's actions
            while (step_num < len(config)) and (now_seconds > utc_seconds_timestamp(config[step_num]['time'])):
                step_num += 1
                now_seconds = (utc_seconds_now() - first_seconds) % MOD
            # Reset loop iteration counts since last reload of configuration file
            reload_count = 0
        elif now_seconds <= utc_seconds_timestamp(config[0]['time']):
            # Reset step number to 0
            step_num = 0
        
        # Check whether it is time to perform the next scheduled action
        if (step_num < len(config)) and (now_seconds >= utc_seconds_timestamp(config[step_num]['time'])):
            step = config[step_num]
            if step['verb'] == 'start':
                # If not already running, spawn process as instance of step['program_name'], and write it's PID to step['pidfile_name']
                start_program(step['program_name'], step['pidfile_name'])
            elif step['verb'] == 'stop':
                # If not already stopped, kill process given by PID in file step['pidfile_name']
                stop_program(step['pidfile_name'])
            elif step['verb'] == 'write':
                # Compute maximum time until next step, padded by timeout_buffer
                timeout = max_socket_timeout(config, step_num, timeout_buffer=TIMEOUT_BUFFER) % MOD
                # Connect to a Unix domain socket step['socket_name'], write a UTF-8 encoded message step['message'], and receive response from server
                write_to_socket(step['socket_name'], step['message'], timeout=timeout)
            step_num += 1
        
        reload_count += 1
        sleep(LOOP_DELAY)