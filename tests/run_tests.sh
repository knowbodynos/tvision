#!/bin/bash

# Initialize color variables for terminal
declare -r color_start="\033["
declare -r color_red="${color_start}0;31m"
declare -r color_green="${color_start}0;32m"
declare -r color_norm="${color_start}0m"


# Obtain this file directory
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd)


trim_timestamp() {
    # Remove timestamps from output
    sed -i '' 's/\[.*\]//g' $1
}

trim_pid() {
    # Remove PIDs from output
    sed -i '' 's/PID {[0-9]*}/PID {}/g' $1
}


check_result() {
    # Define expected and actual output files, as well as a label for the test
    EXPECTED_OUTPUT=$1
    ACTUAL_OUTPUT=$2
    LABEL=$3

    DIFF_RESULT=$(diff -bB ${ACTUAL_OUTPUT} ${EXPECTED_OUTPUT} | wc -l)
    if [ "${DIFF_RESULT}" -eq "0" ] && [ -f ${ACTUAL_OUTPUT} ]
    then
        echo -e "[${color_green}PASS${color_norm}]: ${LABEL}"
    else
        echo -e "[${color_red}FAIL${color_norm}]: ${LABEL}"
    fi
}


test_process() {
    # Clean up residual PID files and running instance
    rm ${ROOT_DIR}/test_full/var/run/program.pid 2>/dev/null
    instances=$(ps -a | grep "test_process.test_process" | cut -d' ' -f1)
    for instance in $instances
    do
        kill -9 $instance >/dev/null 2>&1
    done

    # Define expected and actual output files
    EXPECTED_OUTPUT="${ROOT_DIR}/test_process/expected_output.txt"
    ACTUAL_OUTPUT="${ROOT_DIR}/test_process/output.txt"

    # Run the test_process file
    python -m test_process.test_process > $ACTUAL_OUTPUT

    # Trim timestamps and PIDs from output
    trim_timestamp "$ACTUAL_OUTPUT"
    trim_pid "$ACTUAL_OUTPUT"

    # Compare expected and actual output
    check_result "$EXPECTED_OUTPUT" "$ACTUAL_OUTPUT" "Process test"

    # Clean up output and PID files
    rm $ACTUAL_OUTPUT
    rm ${ROOT_DIR}/test_process/var/run/program.pid
}


test_socket() {
    # Clean up residual socket files and running instance
    rm ${ROOT_DIR}/test_full/var/run/program.sock 2>/dev/null
    instances=$(ps -a | grep "test_socket.test_socket" | cut -d' ' -f1)
    for instance in $instances
    do
        kill -9 $instance >/dev/null 2>&1
    done

    # Define expected and actual output files
    EXPECTED_OUTPUT="${ROOT_DIR}/test_socket/expected_output.txt"
    ACTUAL_OUTPUT="${ROOT_DIR}/test_socket/output.txt"

    # Run the test_socket file before starting socket server for negative, zero, and positive timeout values
    python -m test_socket.test_socket "-30" > $ACTUAL_OUTPUT 2>&1
    python -m test_socket.test_socket "0" >> $ACTUAL_OUTPUT 2>&1
    python -m test_socket.test_socket "30" >> $ACTUAL_OUTPUT 2>&1

    # Start socket server and capture its PID
    python ${ROOT_DIR}/../src/echo_server.py ${ROOT_DIR}/test_socket/var/run/program.sock >/dev/null &
    server_pid=$!

    # Run the test_socket file after starting socket server for negative, zero, and positive timeout values
    python -m test_socket.test_socket "-30" >> $ACTUAL_OUTPUT 2>&1
    python -m test_socket.test_socket "0" >> $ACTUAL_OUTPUT 2>&1
    python -m test_socket.test_socket "30" >> $ACTUAL_OUTPUT 2>&1

    # Kill the socket server process
    kill -9 "$server_pid"
    # Wait for socket server process to release resources
    wait "$server_pid" 2>/dev/null

    # Trim timestamps and PIDs from output
    trim_timestamp "$ACTUAL_OUTPUT"
    trim_pid "$ACTUAL_OUTPUT"

    # Compare expected and actual output
    check_result "$EXPECTED_OUTPUT" "$ACTUAL_OUTPUT" "Socket test"

    # Clean up output and socket files
    rm $ACTUAL_OUTPUT
    rm ${ROOT_DIR}/test_socket/var/run/program.sock
}


test_full() {
    # Clean up residual PID files, socket files, and running instance
    rm ${ROOT_DIR}/test_full/var/run/program.pid 2>/dev/null
    rm ${ROOT_DIR}/test_full/var/run/program.sock 2>/dev/null
    instances=$(ps -a | grep "test_full.test_full" | cut -d' ' -f1)
    for instance in $instances
    do
        kill -9 $instance >/dev/null 2>&1
    done

    # Define expected and actual output files
    EXPECTED_OUTPUT="${ROOT_DIR}/test_full/expected_output.txt"
    ACTUAL_OUTPUT="${ROOT_DIR}/test_full/output.txt"

    # Start socket server and capture its PID
    python ${ROOT_DIR}/../src/echo_server.py ${ROOT_DIR}/test_full/var/run/program.sock >/dev/null &
    server_pid=$!

    # Run the test_full file
    python -u -m test_full.test_full ${ROOT_DIR}/test_full/config.yaml > $ACTUAL_OUTPUT 2>&1 &
    test_pid=$!

    max_time=500
    elapsed_time=0
    while [ "${elapsed_time}" -le "${max_time}" ]
    do
        percent=$(echo "100*${elapsed_time}/${max_time}" | bc)
        echo -ne "Completed ${percent}% of full test.\r"
        sleep 1
        elapsed_time=$((${elapsed_time}+1))
    done

    # Kill the test process
    kill -9 "$test_pid" 2>/dev/null
    # Wait for test process to release resources
    wait "$test_pid" 2>/dev/null

    # Kill the socket server process
    kill -9 "$server_pid"
    # Wait for socket server process to release resources
    wait "$server_pid" 2>/dev/null

    # Trim timestamps and PIDs from output
    trim_timestamp "$ACTUAL_OUTPUT"
    trim_pid "$ACTUAL_OUTPUT"

    # Compare expected and actual output
    check_result "$EXPECTED_OUTPUT" "$ACTUAL_OUTPUT" "Full test           "

    # Clean up output, PID, and socket files
    rm $ACTUAL_OUTPUT
    rm ${ROOT_DIR}/test_full/var/run/program.pid
    rm ${ROOT_DIR}/test_full/var/run/program.sock
}


run_all_tests() {
    # Run process test
    test_process
    # Run socket test
    test_socket
    # Run full test
    test_full
}


main() {
    # Save current directory and navigate to test directory
    CURR_DIR=$(pwd)
    cd $ROOT_DIR

    # Run tests
    run_all_tests

    # Return to original directory
    cd $CURR_DIR
}

main "$@"