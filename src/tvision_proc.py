import os
from subprocess import Popen
from signal import SIGTERM
from time import sleep
from .tvision_io import print_log

def pid_running(pid):
    """Check whether a process specified by PID pid is running."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def start_program(program_name, pidfile_name):
    """If not already running, spawn a background process given by program_name,
    and store its PID in pidfile_name."""
    # If file exists, read PID from pidfile_name
    try:
        with open(pidfile_name, "r") as pidfile_stream:
            try:
                pid = int(pidfile_stream.readline())
            except ValueError as ve:
                pid = None
                print_log("{} (Invalid PID stored in {{{}}}.)".format(ve, pidfile_name))
    except FileNotFoundError:
        pid = None
        print_log("Existing PID file {{{}}} not found.".format(pidfile_name))
    else:
        print_log("Clearing existing PID file {{{}}}.".format(pidfile_name))   
    # If it can be read, check whether PID pid is running
    if (pid is None) or (not pid_running(pid)):
        try:
            # Spawn new process as instance of program_name
            proc = Popen(program_name.split())
        except Exception as e:
            print_log("{} (Program {{{}}} not found.)".format(e, program_name))
        else:
            print_log("Program {{{}}} started with PID {{{}}}.".format(program_name, proc.pid))
            with open(pidfile_name, "w") as pidfile_stream:
                pidfile_stream.write(str(proc.pid))
                print_log("PID {{{}}} for program {{{}}} logged in {{{}}}.".format(proc.pid, program_name, pidfile_name))
    else:
        print_log("Program {{{}}} already running with PID {}.".format(program_name, pid))


def stop_program(pidfile_name):
    """If process with PID stored in pidfile_name is running, kill it."""
    # If file exists, read PID from pidfile_name
    try:
        with open(pidfile_name, "r") as pidfile_stream:
            try:
                pid = int(pidfile_stream.readline())
            except ValueError as ve:
                pid = None
                print_log("{} (Invalid PID stored in {{{}}}.)".format(ve, pidfile_name))
    except FileNotFoundError:
        pid = None
        print_log("Existing PID file {{{}}} not found.".format(pidfile_name))
    # If it can be read, check whether PID pid is running
    if (pid is None) or (not pid_running(pid)):
        print_log("Process with PID {{{}}} already finished.".format(pid))
    else:
        # Attempt to kill parent process with PID pid
        try:
            os.kill(pid, SIGTERM)
        except ProcessLookupError as ple:
            print_log("{} (Process with PID {{{}}} does not exist.)".format(ple, pid))
        else:
            # Attempt to release child process resources and avoid zombie processes
            sleep(0.1)
            try:
                os.waitpid(pid, 0)
            except OSError as oe:
                print_log("{} (Exit status for process with PID {{{}}} not yet received.)".format(oe, pid))
            except ChildProcessError as cpe:
                print_log("{} (Child processes for process with PID {{{}}} have been terminated.)".format(cpe, pid))
        print_log("Process with PID {{{}}} stopped.".format(pid))