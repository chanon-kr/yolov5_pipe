from py_topping.general_use import timeout
import git
# Update Script
print('Update script from GitHub')
@timeout(30)
def update_yolov5_pipe() :
    repo = git.Repo()
    repo.remotes.origin.pull()
try : update_yolov5_pipe()
except : print('Update script from GitHub Fail')

# Update Dependencies
import subprocess, sys
update_list = [['-r','https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt']
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
print(_['run_result'][0])