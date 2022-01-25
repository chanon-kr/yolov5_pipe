# YOLOv5_Pipe
## Python Code to Deploy YOLOv5 

## For Windows
1. Create Virtual Environment or just use WinPython
2. Install Git to your Windows
3. Install dependencies as listed in install_windows.txt <br>
```pip install -r install_windows.txt```<br>
4. Download or Clone this repository
5. In folder "F01", remove prefix "blank_" of every file
6. Place your model in folder "F02"
7. Change config in "F01/config.xlsx" as describe in that file

## For Jetson Nano (Testing)
```
git clone https://github.com/chanon-kr/yolov5_pipe.git
cd yolov5_pipe
bash install_linux.sh
```