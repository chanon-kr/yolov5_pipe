import requests

# Update Script
url = 'https://github.com/chanon-kr/yolov5_pipe/blob/main/F00_script/'
file_name = ['script.py','func_utilities.py']
for i in file_name :
    print('Update Script {}'.format(i))
    try :
        r = requests.get(url + i, timeout = 20)
        with open('F00_script/{}'.format(i) , 'wb') as f : f.write(r.content)
    except : pass

# Update Dependencies
import subprocess, sys
update_list = [['-qr','https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt']
               ,['-r','F00_script/requirements.txt']]
for i in update_list :
    print('Update Dependencies from ',i[1])
    try : subprocess.check_call([sys.executable, "-m", "pip", "install", i[0], i[1]], timeout = 30)
    except : pass

# Run Script
from py_topping.run_pipeline import run_pipeline
from py_topping.general_use import lazy_LINE

pipeline_line = lazy_LINE('')
_ = run_pipeline(script_list = ['F00_script/script.py']
             , only_error = True
             , line_sending = pipeline_line
             , line_subject = '')
print(_)