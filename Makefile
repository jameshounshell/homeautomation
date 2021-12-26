run:
	poetry run python homeautomation/main.py

loop:
	while true; do poetry run python homeautomation/main.py; sleep 30; done

test:
	poetry run ptw homeautomation/main.py -- -s