import pandas as pd
import cv2

# Read Input File
input_df = pd.read_excel('F01_config/config.xlsx', sheet_name = 'config'
                        , dtype = str, index_col='parameter')[['value']].fillna('')
input_df = input_df[input_df['value'] != '']['value'].to_dict()

# Get Video Source
video_source = input_df.get('video_source','0')
if video_source.replace('.','',1).isdigit() : video_source = int(video_source)
reconnect_video = int(input_df.get('reconnect_video','1'))

# Read Video
video = cv2.VideoCapture(video_source)

while(video.isOpened()):
    # Check
    ret, frame = video.read()
    if not ret:
        if reconnect_video : continue
        else :
            print('Reached the end of the video!')
            break
    # Show
    frame = cv2.resize(frame, (400, 400))
    cv2.imshow('Object detector', frame)
    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'): break

# Clean Up
video.release()
cv2.destroyAllWindows()