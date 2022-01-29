# YOLOv5_Pipe
## Python Code to Deploy YOLOv5 

## For Windows
1. Create Virtual Environment or just use WinPython
2. Install Git to your Windows
3. Download or Clone this repository<br>
```git clone https://github.com/chanon-kr/yolov5_pipe.git```
4. Install dependencies as listed in install_windows.txt <br>
```pip install -r install_windows.txt```<br>
5. In folder "F01", remove prefix "blank_" of every file
6. Place your model in folder "F02" or on your Cloud
7. Change config in "F01/config.xlsx" as describe in that file
8. Run "main.py", it will download and install everythings for you

## For Jetson Nano (Still Testing)
1. Install Jetpack from NVIDIA's page : https://developer.nvidia.com/embedded/jetpack
2. Run NVIDIA's ML Docker : https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-ml <br>
```
sudo docker run -it --gpus all --rm --runtime nvidia --network host -e DISPLAY=:0 -v /home/user/project:/home nvcr.io/nvidia/l4t-ml:r32.6.1-py3
```
3. Install nano for text editor
```apt-get install nano```
4. Change to that Directory and Clone this Repository
```
cd home
git clone https://github.com/chanon-kr/yolov5_pipe.git
cd yolov5_pipe
```
5. Install other dependencies (Current at here)
```
pip3 install tqdm
```