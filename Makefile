run:
	poetry run python homeautomation/main.py

loop:
	while true; do poetry run python homeautomation/main.py; sleep 15; done

test:
	poetry run ptw homeautomation/main.py -- -s


service_name = lights.service

# install as systemd service
systemd_install:
	sudo ln -sf $$HOME/git/homeautomation/systemd/$(service_name) /etc/systemd/system/$(service_name)
	sudo systemctl daemon-reload
	sudo systemctl enable $(service_name)
	sudo systemctl start $(service_name)

debug: systemd_reload systemd_restart systemd_logs

systemd_restart:
	sudo systemctl restart $(service_name)

systemd_logs:
	journalctl -u lights.service --since '5 minutes ago' -f

systemd_status:
	sudo systemctl status

systemd_reload:
	sudo systemctl daemon-reload

systemd_uninstall:
	sudo systemctl stop $(service_name)
	sudo systemctl disable $(service_name)
	sudo rm $$HOME/git/homeautomation/systemd/$(service_name)
