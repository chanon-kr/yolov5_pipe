import requests

# Update Script
url = 'https://github.com/chanon-kr/yolov5_pipe/blob/main/F00_script/'
file_name = ['script.py','func_utilities.py']
for i in file_name :
    try :
        print('Update Script {}'.format(i))
        r = requests.get(url + i, timeout = 20)
        with open('F00_script/{}'.format(i) , 'wb') as f : f.write(r.content)
    except : pass

# Update Libraries
import subprocess, sys


# Run Script
from py_topping.run_pipeline import run_pipeline
run_pipeline(script_list = ['F00_script/script.py']
             , only_error = True
             , line_sending = ''
             , line_subject = '')