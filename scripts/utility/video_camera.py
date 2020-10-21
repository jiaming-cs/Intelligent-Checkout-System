import cv2

from face_recog.face_id import FaceId
from anti_spoofing.anti_spoofing import check_authenticity

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture("../data/test_video_spoofing.mp4")
        #self.video = cv2.VideoCapture(0)
        self.faceid = FaceId()
        
    
    def __del__(self):
        self.video.release()
    
    def check_identity(self):
        rtvl, frame = self.video.read()
        is_real, frame_auth = check_authenticity(frame.copy())
            
        if is_real:
            frame = self.faceid.match_faces(frame.copy())     
        else:
            frame = frame_auth
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def encode_face(self):
        rtvl, frame = self.video.read()
        status, face_encoding, frame = self.faceid.encode_face(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)

        return status, face_encoding, jpeg.tobytes()

    