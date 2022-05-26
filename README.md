Home Automation
===============
Python code for manipulated smart devices integrated with SmartThings Hub by Samsung.

Requirements
------------
- python3
- poetry
- `SMARTTHINGS_PERSONAL_ACCESS_TOKEN` as an environment variable in a file called ~/.secrets

Running
-------
- `make run` will run the code on a 15-second loop.

Development
-----------
`make test` to run tests

systemd
-------
To run the process on startup, install the program as a service.  
Run `make systemd_install` to place and enable `lights.service`  
See Makefile and systemd folder for more info.