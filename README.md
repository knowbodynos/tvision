# TVision Insights Device Team Coding Exercise

----
## To Use
1. Navigate to the main directory: `cd tvision`

2. Edit the file *config.yaml* to reflect the daily actions that should be performed.

3. Run your own Unix domain socket server or the one given in  *src/echo_server.py* using the socket path given in *config.yaml*:

 `python  src/echo_server.py /var/run/release-bunnies.sock`

4. Run the script: `./run.sh config.yaml`

----
## To Test
1. Navigate to the test directory: `cd tvision/tests`

2. To test process start/stop behavior, socket writing behavior, and full behavior with an example *config.yaml* file, run the test script: `./run_tests.sh`