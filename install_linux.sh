# Start
sudo apt-get update
sudo apt-get dist-upgrade

# Library
sudo apt install python3-pip
# pip3 install --upgrade pip
# pip3 install py-topping
# pip3 install GitPython

# Open CV
# sudo apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
# sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
# sudo apt-get -y install libxvidcore-dev libx264-dev
# sudo apt-get -y install qt4-dev-tools libatlas-base-dev
# pip3 install opencv-python

# Pytorch
wget https://nvidia.box.com/shared/static/p57jwntv436lfrd78inwl7iml6p13fzh.whl -O torch-1.8.0-cp36-cp36m-linux_aarch64.whl
sudo apt-get install python3-pip libopenblas-base libopenmpi-dev 
pip3 install Cython
pip3 install numpy torch-1.8.0-cp36-cp36m-linux_aarch64.whl


# Torch Vision
sudo apt-get install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev
git clone --single-branch --branch v0.9.0 https://github.com/pytorch/vision torchvision   # see below for version of torchvision to download
cd torchvision
export BUILD_VERSION=0.9.0  # where 0.x.0 is the torchvision version  
python3 setup.py install --user
cd ../
