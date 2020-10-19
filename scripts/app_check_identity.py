from face_recog.face_id import FaceId
import cv2
from anti_spoofing.anti_spoofing import check_authenticity
from const.consts import SKIP_FRAMES

video_capture = cv2.VideoCapture("../data/test_video_spoofing.mp4")
faceid = FaceId()
faceid.encode_faces()
frame_index = 0

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()
    frame_index += 1
    if not ret:
        break
    if frame_index % SKIP_FRAMES != 0:
        continue
    #frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # Resize frame of video to 1/4 size for faster face recognition processing


    
    is_real, frame_auth = check_authenticity(frame.copy())

    if is_real:
        frame = faceid.match_faces(frame.copy())     
        cv2.imshow("video", frame)
    else:
        cv2.imshow("video", frame_auth)
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()