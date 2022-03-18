
import cv2, warnings, os, traceback, json
from pandas.core.dtypes import dtypes
import pandas as pd
from glob import glob
from datetime import datetime
from F00_script.func_utilities import *

warnings.filterwarnings("ignore")

def main_script() :
    # --Prep. Phase--

    # INPUT
    print('Reading Input')
    input_df = pd.read_excel('F01_config/config.xlsx', sheet_name = 'config'
                            , dtype = str, index_col='parameter')[['value']].fillna('')
    input_df = input_df[input_df['value'] != '']['value'].to_dict()

    ## Basic
    job_name = input_df.get('job_name','')
    show_fps = int(input_df.get('show_fps','0'))
    video_source = input_df.get('video_source','0')
    if video_source.replace('.','',1).isdigit() : video_source = int(video_source)
    show_size = float(input_df.get('show_size','0.5'))
    if show_size > 0 :
        display_output = True
        if show_size == 1 : resize_show = False
        else : resize_show = True
    else : display_output, resize_show  = False, False
    reconnect_video = int(input_df.get('reconnect_video','1'))

    ## MODEL
    model_source = input_df.get('model_source','')
    model_name = os.path.join('F02_model', input_df['model_name'])
    predict_size = int(input_df.get('predict_size','416'))
    device_type = input_df.get('device_type','cpu')
    conf = float(input_df.get('conf','0.25'))
    iou = float(input_df.get('iou','0.4'))
    y1 = float(input_df.get('y1','0'))
    y2 = 1 - float(input_df.get('y2','0'))
    assert (y1 < y2), 'Please recheck y1,y2'
    x1 = float(input_df.get('x1','0'))
    x2 = 1 - float(input_df.get('x2','0'))
    assert (x1 < x2), 'Please recheck x1,x2'

    ## Class
    class_detect = pd.read_excel('F01_config/config.xlsx', sheet_name = 'class_detect'
                                , index_col = 'class' , dtype = str)
    if class_detect.loc['all','detect'] == '1' : class_detect = None
    else : 
        class_detect = class_detect.iloc[1:,:].reset_index()
        class_detect = class_detect[class_detect['detect'] == '1']
        class_detect = list(class_detect.index)
        if class_detect == [] : class_detect = None

    ## Alert Logic
    line_token = input_df.get('line_token','')
    alert_conf = float(input_df.get('alert_conf','0.7'))
    alert_frame = int(input_df.get('alert_frame','3'))
    decision_frame = int(input_df.get('decision_frame','5'))

    ## Local Data
    flush = int(input_df.get('flush','1'))
    temp_table = input_df.get('temp_table','temp_table')
    record_fps = int(input_df.get('record_fps','5'))
    resize = float(input_df.get('resize','1'))
    video_expire_after = int(input_df.get('video_expire_after','5'))
    detected_saveforever = int(input_df.get('detected_saveforever','0'))
    ## Cloud Upload
    db_table = input_df.get('db_table','')
    bucket_folder_name = input_df.get('bucket_folder_name','')
    ignore_error = int(input_df.get('ignore_error','0'))

    ## Slot
    slot_minute = int(input_df.get('slot_minute','1'))
    restart_minute = int(input_df.get('restart_minute','60'))
    upload_minute = int(input_df.get('upload_minute','10'))

    

    ## Advance Parameter
    with open('F01_config/advance_config.json') as f :
        input_json = json.load(f)

    local_framework = int(input_json.get('framework',{}).get('local_framework','0'))
    force_reload = int(input_json.get('framework',{}).get('force_reload','1'))
    local_record_config = input_json.get('local_record_config',{"type": "sqlite","host_name": "local_result.db"})
    db_record_config = input_json.get('db_record_config','')
    storage_config = input_json.get('storage_config','')
    model_source_config = input_json.get('model_source_config','')
    heart_beat_config = input_json.get('heart_beat_config','')
    heart_table_name = input_json.get('heart_beat_config',{}).get('heart_table_name','')
    error_token = input_json.get('error_token','')

    # On/Off
    ## User config
    turn_on_line = (line_token != '')
    turn_on_update_model = (model_source != '') & (model_source_config != '')
    ## Upload config
    turn_on_upload_db = (db_table != '') & (db_record_config != '')
    turn_on_upload_clip = (bucket_folder_name != '') & (storage_config != '')
    ## Advanace config
    turn_on_heartbeat = (heart_beat_config != '') & (heart_table_name != '')
    turn_on_local_record = (local_record_config != '')
    turn_on_upload_db = (turn_on_local_record & turn_on_upload_db)


    # Start!!!
    if turn_on_heartbeat : 
        start_message = json.dumps({'basic' : input_df , 'advance' : input_json})
        send_heartbeat('Start Prep Phase', heart_table_name, heart_beat_config, ignore_error_in = ignore_error, job_name_in = job_name, message_in = start_message)
        del start_message
    del input_df, input_json

    # Update Model
    if turn_on_update_model : update_model(model_source , model_name, model_source_config)

    # Model
    model = setup_model(model_name, force_reload, device_type, conf, iou, class_detect, local_framework)

    # Ensure Folder
    if not os.path.isdir('F03_clip') : os.mkdir('F03_clip')
    if detected_saveforever :
        folder_detected_saveforever = os.path.join('F03_clip','detected')
        if not os.path.isdir(os.path.join(folder_detected_saveforever)) : os.mkdir(folder_detected_saveforever)

    # Flush Old Data if needed
    flush_old(flush, local_record_config, temp_table)

    # RUN
    video = cv2.VideoCapture(video_source)

    # Video Size
    imW = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    imH = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Set Area
    if [y1,y2,x1,x2] == [0,1,0,1] : area_detection = False
    else : area_detection = True
    y1,y2,x1,x2 = int(imH*y1),int(imH*y2), int(imW*x1),int(imW*x2)

    # Cal Resize
    resize_width, resize_height = int(int(imW)*resize) , int(int(imH)*resize)
    resize_width_show, resize_height_show = int(int(imW)*show_size) , int(int(imH)*show_size)

    # Utility
    fps_list,now, frame_no = [],datetime.now(), 0
    df_all = pd.DataFrame()
    start_time, slot_time, upload_time = now, now, now
    callback_trigger = False
    create_detected_saveforever = 0

    # Create Video
    current_video = os.path.join('F03_clip','clip_{}.avi'.format(slot_time.strftime('%Y%m%d_%H%M')))
    out_video = cv2.VideoWriter(current_video, cv2.VideoWriter_fourcc(*'DIVX')  ,record_fps  ,(resize_width, resize_height))

    if turn_on_heartbeat : send_heartbeat('Start Loop Phase', heart_table_name, heart_beat_config, ignore_error_in = ignore_error, job_name_in = job_name)

    # --Loop Phase--
    print('Start Main Loop')
    try :
        read_temp_video, record_temp = True, True
        temp_video = None
        while(video.isOpened()):
            # Begin
            now = datetime.now()
            ret, frame = video.read()
            if not ret:
                if read_temp_video  :
                    video.release()
                    video = cv2.VideoCapture(video_source)
                    record_temp = True
                    continue
                elif reconnect_video : continue
                else :
                    print('Reached the end of the video!')
                    break

            # Temp Video
            temp_video_name = 'tempvideo.avi'
            temp_fps = 15
            temp_length = 60
            if read_temp_video & record_temp :
                if temp_video is None :
                    print('create temp video')
                    temp_begin = datetime.now()
                    temp_video = cv2.VideoWriter(temp_video_name, cv2.VideoWriter_fourcc(*'DIVX')  , temp_fps, (int(imW), int(imH)))
                if (datetime.now() - temp_begin).total_seconds() < temp_length :
                    temp_video.write(frame)
                else : 
                    temp_video.release()
                    temp_video = None
                    record_temp = False
                    video.release()
                    print('read temp video')
                    video = cv2.VideoCapture(temp_video_name)
                continue

            # Inference
            results = model(frame[y1:y2,x1:x2], size = predict_size)

            # Save for cal fps
            fps_list = fps_list[-decision_frame:]
            fps_list, fps = cal_fps(now, fps_list, show = show_fps)

            # Set output df
            df = results.pandas().xyxy[0]
            df = modify_df(df, now, fps, frame_no, start_time, slot_time, job_name, [(x2,y2), (x1,y1)])
            df_all = df_all.append(df)
            df_all = df_all[df_all['frame_no'] >= (frame_no - decision_frame)]
            current_found = list(df['name'].unique())

            # Set image output
            show_image = frame[:] # Try
            show_image[y1:y2,x1:x2] = results.render()[0] # Try
            cv2.rectangle(show_image, (x2,y2), (x1,y1), (0, 255, 255), 2) # Try
            # if area_detection : show_image = label_image(frame , df, [(x2,y2), (x1,y1)])
            # else : show_image = results.render()[0]
            if display_output :
                if resize_show :
                    resize_image = cv2.resize(show_image, (resize_width_show, resize_height_show))
                    cv2.imshow('Object detector', resize_image)
                else : cv2.imshow('Object detector', show_image)

            # Save result
            record_result(df, temp_table, local_record_config)
            resize_image = cv2.resize(show_image, (resize_width, resize_height))
            out_video.write(resize_image)

            # Notification
            for i in current_found :
                if detected_saveforever : create_detected_saveforever = 1
                frame_found = ((df_all['name'] == i) & (df_all['confidence'] >= alert_conf)).sum()
                if frame_found >= alert_frame :
                    # Save Image
                    cv2.imwrite('send_noti.jpg' , resize_image)
                    # Send LINE
                    if turn_on_line : send_LINE('\n---\n{}\n---\nFound {}'.format(job_name, i) , line_token, 'send_noti.jpg')
                    # Flush DF
                    df_all = df_all[df_all['name'] != i]

            # Slot check
            slot_check = (now - slot_time).total_seconds()/60
            if slot_check > slot_minute :
                # End current video and start new
                out_video.release()
                # Save detected video
                if create_detected_saveforever :
                    shutil.copy(current_video , current_video.replace('F03_clip', folder_detected_saveforever))
                    create_detected_saveforever = 0
                # Start New Video
                slot_time = now
                current_video = os.path.join('F03_clip','clip_{}.avi'.format(slot_time.strftime('%Y%m%d_%H%M')))
                out_video = cv2.VideoWriter(current_video, cv2.VideoWriter_fourcc(*'DIVX')  ,record_fps  ,(resize_width, resize_height))
                # Upload video
                upload_check = (now - upload_time).total_seconds()/60
                if upload_check > upload_minute :
                    print('--- Start Upload ---')
                    upload_time = now
                    if turn_on_heartbeat : send_heartbeat('Start Upload', heart_table_name, heart_beat_config, ignore_error_in = ignore_error, job_name_in = job_name)
                    if turn_on_upload_db : upload_result(temp_table , now, db_table, local_record_config, db_record_config, ignore_error )
                    if turn_on_upload_clip : upload_clip('F03_clip', current_video, bucket_folder_name, storage_config, ignore_error , video_expire_after = video_expire_after)
                    if turn_on_heartbeat : send_heartbeat('End Upload', heart_table_name, heart_beat_config, ignore_error_in = ignore_error, job_name_in = job_name)
                    print('--- Finish Upload ---')
                # Restart
                restart_check = (now - start_time).total_seconds()/60
                if restart_check > restart_minute : break

            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'): break
            # Count Frame
            frame_no += 1

    # Create Callback Phase
    except Exception as e :
        error_message, callback_trigger = str(e), True
        long_error = str(traceback.format_exc())

    if turn_on_heartbeat : send_heartbeat('Start Release Phase', heart_table_name, heart_beat_config, ignore_error_in = ignore_error, job_name_in = job_name)

    # --Release Phase--
    print('Start Release Phase')
    out_video.release()
    video.release()
    cv2.destroyAllWindows()

    # --Callback Phase--
    if callback_trigger :
        print(long_error)
        print(error_message)
        error_df = pd.DataFrame({'t_stamp' : datetime.now() , 'error' : [error_message]})
        record_result(error_df, 'error_log', local_record_config)
        if turn_on_heartbeat : send_heartbeat('Callback Phase', heart_table_name, heart_beat_config, ignore_error_in = ignore_error, job_name_in = job_name, message_in = long_error)
        send_LINE('\n---\n{}\n---\n{}'.format(job_name, error_message) , error_token, '')

main_script()
