# YOLOv5_Pipe
## Python Code to Deploy YOLOv5 

## For Windows
1. Create Virtual Environment or just use WinPython
2. Install Git to your Windows
3. Download or Clone this repository
```git clone https://github.com/chanon-kr/yolov5_pipe.git```
4. Install dependencies as listed in install_windows.txt <br>
```pip install -r install_windows.txt```<br>
5. In folder "F01", remove prefix "blank_" of every file
6. Place your model in folder "F02" or on your Cloud
7. Change config in "F01/config.xlsx" as describe in that file
8. Run "main.py", it will download and install everythings for you

## For Jetson Nano (Testing)
```
sudo docker run -it --rm --runtime nvidia --network host -v /home/user/project:/home nvcr.io/nvidia/l4t-ml:r32.6.1-py3
cd home
git clone https://github.com/chanon-kr/yolov5_pipe.git
cd yolov5_pipe
...
```