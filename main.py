from py_topping.run_pipeline import run_pipeline
from py_topping.general_use import lazy_LINE, timeout
from git import Repo
import subprocess, sys

@timeout(30)
def update_yolov5_pipe() :
    repo = Repo()
    repo.remotes.origin.pull()

def update_all() :
    # Update Script
    print('Update script from GitHub')
    try : update_yolov5_pipe()
    except : print('Update script from GitHub Fail')

    # Update Dependencies
    update_list = [['-r','https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt']
                  ,['-r','F00_script/requirements.txt']]
    for i in update_list :
        print('Update Dependencies from ',i[1])
        try : subprocess.check_call([sys.executable, "-m", "pip", "install", i[0], i[1]], timeout = 30)
        except : pass
    return 1

def main() :
    _ = update_all()
    # Run Script
    pipeline_line = lazy_LINE('')
    _ = run_pipeline(script_list = ['F00_script/script.py']
                , only_error = True
                , line_sending = pipeline_line
                , line_subject = '')
    print(_['run_result'][0])

if __name__ == '__main__':
    main()