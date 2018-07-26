#!/bin/bash

main() {
    # Read configuration file path from input argument
    config_file=$1

    # Run tvision.py script with configuration file path as input argument
    python -m src.tvision $config_file
}

main "$@"