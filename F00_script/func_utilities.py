import cv2, os, torch
from git import Repo
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from py_topping.general_use import lazy_LINE, healthcheck
from py_topping.data_connection.database import lazy_SQL
from py_topping.data_connection.gcp import lazy_GCS
from glob import glob

from threading import Thread
import functools

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

def update_local_framework() :
    if not os.path.isdir('ultralytics') : os.makedirs(os.path.join(os.getcwd(),'ultralytics'))
    os.chdir('ultralytics')
    if os.path.isdir('yolov5') : 
        print('Update YOLOv5 from Ultralytics')
        os.chdir('yolov5')
        repo = Repo()
        repo.remotes.origin.pull()
    else :
        print('Clone YOLOv5 from Ultralytics')
        yolov5_url = 'https://github.com/ultralytics/yolov5.git'
        Repo.clone_from(yolov5_url , os.path.join(os.getcwd(),'yolov5'))

def setup_model(model_name, force_reload, device_type, conf, iou, class_detect, local_framework) :
    print('Set up Model')
    if local_framework :
        base_dir = os.getcwd()
        t_update_local_framework = timeout(timeout=30)(update_local_framework)
        os.chdir(base_dir)
        try : t_update_local_framework()
        except : print('Update Fail')
        model = torch.hub.load('ultralytics/yolov5', 'custom', path = model_name
                                , source ='local'
                                , force_reload = force_reload, device = device_type) 
    else :
        model = torch.hub.load('ultralytics/yolov5' , 'custom', path = model_name
                                , force_reload = force_reload, device = device_type) 
    model.conf, model.iou = conf, iou 
    model.classes = class_detect
    return model

def send_heartbeat(process_name_in, table_name_in, heart_beat_config_in, ignore_error_in = False, error_message_in = '') :
    des_sql = lazy_SQL(sql_type = heart_beat_config_in['type'] 
                       , host_name = heart_beat_config_in['host_name']
                       , database_name = heart_beat_config_in['db_name'] 
                       , user = heart_beat_config_in['user']
                       , password = heart_beat_config_in['password'] 
                       , mute = True)
    df_sql = pd.DataFrame(healthcheck())
    df_sql['t_stamp'] = datetime.now()
    df_sql['process_name'] = process_name_in
    df_sql['error_message'] = error_message_in
    if ignore_error_in :
        try : des_sql.sub_dump(df_sql , table_name_in ,'append')
        except : pass
    else : des_sql.sub_dump(df_sql , table_name_in ,'append')

def modify_df(df_in, now_in, fps_in, frame_no_in, start_time_in, slot_time_in, job_name_in, area_detect_in) :
    df_out = df_in.copy()
    x1_in, y1_in = area_detect_in[1]
    df_out['t_stamp'] = now_in.strftime('%Y-%m-%d %H:%M:%S')
    df_out['fps'] = fps_in
    df_out['frame_no'] = frame_no_in
    df_out['start_time'] = start_time_in
    df_out['slot_time'] = slot_time_in
    df_out['job_name'] = job_name_in
    df_out['xmin'] += x1_in
    df_out['xmax'] += x1_in
    df_out['ymin'] += y1_in
    df_out['ymax'] += y1_in
    df_out['area'] = str(area_detect_in)
    return df_out

def cal_fps(now_input, fps_list_input, show = True):
    fps_cal = (datetime.now() - now_input).total_seconds()
    if fps_cal == 0 : fps_cal = 60
    else : fps_cal = 1/fps_cal
    fps_list_input.append(fps_cal)
    fps = round(np.mean(fps_list_input),2)
    if show : print('Average FPS :', fps)
    return fps_list_input, fps

def send_LINE(target_in , line_token_in, path_in) :
    print('Send Line Message\n---\n{}'.format(target_in))
    line = lazy_LINE(line_token_in)
    line.send(target_in, picture = path_in)

def label_image(frame_in, df_in , area_detect_in ) :
    # Add rectangle of Applied Area
    x1_in, y1_in = area_detect_in[1]
    frame_out = cv2.rectangle(frame_in, area_detect_in[0], area_detect_in[1], (0, 255, 255), 2)
    for i_ in df_in.index :
        # Draw Box
        ymin = int(df_in.loc[i_, 'ymin'] + y1_in)
        xmin = int(df_in.loc[i_, 'xmin'] + x1_in)
        ymax = int(df_in.loc[i_, 'ymax'] + y1_in)
        xmax = int(df_in.loc[i_, 'xmax'] + x1_in)
        frame_out = cv2.rectangle(frame_out, (xmin,ymin), (xmax,ymax), (10, 255, 0), 4) 
        # Draw label
        label = '%s: %d%%' % (df_in.loc[i_, 'name'], int(df_in.loc[i_, 'confidence']*100))
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) 
        label_ymin = max(ymin, labelSize[1] + 10)
        cv2.rectangle(frame_out, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) 
        cv2.putText(frame_out, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    return frame_out

def flush_old(flush, local_record_config_in, temp_table_in) :
    if flush : 
        clean_folder = glob('clip/*')
        for i in clean_folder : os.remove(i)
        sqlite = lazy_SQL(sql_type = local_record_config_in['type'] 
                        , host_name = local_record_config_in['host_name']
                        , database_name = '', user = '', password = '' 
                        , mute = True)
        sqlite.engine.execute("DROP TABLE IF EXISTS {}".format(temp_table_in))

def record_result(df_in, temp_table_in , local_record_config_in ) :
    df_out = df_in.copy()
    sqlite = lazy_SQL(sql_type = local_record_config_in['type'] 
                      , host_name = local_record_config_in['host_name']
                      , database_name = '', user = '', password = '' 
                      , mute = True)
    sqlite.sub_dump(df_out , temp_table_in,'append')


def upload_result(temp_table_in , now_in, db_table_in, local_record_config_in, db_record_config_in, ignore_error_in = False) :
    sqlite = lazy_SQL(sql_type = local_record_config_in['type']
                      , host_name = local_record_config_in['host_name']
                      , database_name = '',user = '',password = ''
                      , mute = True )
    des_sql = lazy_SQL(sql_type = db_record_config_in['type'] 
                       , host_name = db_record_config_in['host_name']
                       , database_name = db_record_config_in['db_name'] 
                       , user = db_record_config_in['user']
                       , password = db_record_config_in['password']
                       , mute = True )
    date_query = [(now_in + timedelta(hours = i)).strftime('%Y-%m-%d %H') for i in [-3,-2,-1,0,1]]
    date_query = str(tuple(date_query))
    condition_statement = """FROM {} WHERE SUBSTR(slot_time ,1, 13) IN {}""".format(temp_table_in, date_query)
    df_sql = sqlite.read("""SELECT * {}""".format(condition_statement), raw = True )
    print('Start Upload Database')
    if ignore_error_in :
        try :
            des_sql.sub_dump(df_sql , db_table_in,'append')
            sqlite.engine.execute("""DELETE {}""".format(condition_statement))
        except : pass
    else :
        des_sql.sub_dump(df_sql , db_table_in,'append')
        sqlite.engine.execute("""DELETE {}""".format(condition_statement))


def upload_clip(video_folder_in, current_video_in, bucket_folder_name_in, bucket_config_in, ignore_error_in = False) :
    gcs = lazy_GCS(project_id = bucket_config_in['project_id']
                   , bucket_name = bucket_config_in['bucket_name']
                   , credential = bucket_config_in['credential'])
    video_file = glob('{}/*'.format(video_folder_in))
    current_video_in
    if current_video_in in video_file : video_file.remove(current_video_in)
    np.random.shuffle(video_file)
    folder_len = 1 + len(video_folder_in)
    print('Start Upload Video')
    for i_ in video_file :
        bucket_file_name = '{}/{}'.format(bucket_folder_name_in , i_[folder_len:])
        if ignore_error_in :
            try :
                gcs.upload(bucket_file = bucket_file_name , local_file = i_)
                os.remove(i_)
            except : pass
        else :
            gcs.upload(bucket_file = bucket_file_name , local_file = i_)
            os.remove(i_)
            
def update_model(model_source_in , model_name_in, model_source_config_in) :
    gcs = lazy_GCS(project_id = model_source_config_in['project_id']
                   , bucket_name = model_source_config_in['bucket_name']
                   , credential = model_source_config_in['credential'])
    gcs.download(bucket_file = model_source_in, local_file = model_name_in)