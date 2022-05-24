export HOME=/home/james
export PROJECT=$HOME/git/homeautomation
source $HOME/.secrets
while true; do
  /home/linuxbrew/.linuxbrew/bin/poetry run python $PROJECT/homeautomation/main.py
  sleep 15
sleep 15; done