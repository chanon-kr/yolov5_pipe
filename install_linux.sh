# Start
sudo apt-get update
sudo apt-get dist-upgrade

# Library
sudo apt install python3-pip
pip3 install --upgrade pip
pip3 install py-topping
pip3 install GitPython

# Open CV
sudo apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get -y install libxvidcore-dev libx264-dev
sudo apt-get -y install qt4-dev-tools libatlas-base-dev
pip3 install opencv-python