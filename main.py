from py_topping.run_pipeline import run_pipeline
from py_topping.data_connection.database import lazy_GCS
import json

try :
    with open('F00_script/root_config.json') as f :
        input_json = json.load(f)
    gcs = lazy_GCS(project_id = input_json['project_id']
                    , bucket_name = input_json['bucket_name']
                    , credential = input_json['credential'])
    gcs.download(bucket_file = input_json['bucket_file']
                , local_file = 'F00_script/script.py')
except : pass

run_pipeline(script_list = ['F00_script/script.py']
             , only_error = True
             , line_sending = input_json['error_token']
             , line_subject = input_json['error_subject'])