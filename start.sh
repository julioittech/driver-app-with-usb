PID=$(sudo lsof -t /dev/gpiochip0)
sudo kill -9 $PID
cd /home/rpi/Documents/driver-app-with-usb
pwd
source .venv/bin/activate
python --version
# python -u final_version.py