import cv2

from face_recog.face_id import FaceId
from anti_spoofing.anti_spoofing import check_authenticity

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture("../data/test_video_spoofing.mp4")
        #self.video = cv2.VideoCapture(0)
        self.faceid = FaceId()
        self.faceid.encode_faces() 
    
    def __del__(self):
        self.video.release()
    
    def check_identity(self):
        rtvl, image = self.video.read()
        is_real, frame_auth = check_authenticity(image.copy())
            
        if is_real:
            frame = self.faceid.match_faces(image.copy())     
            image = frame
        else:
            image = frame_auth
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def encode_face(self):
        rtvl, image = self.video.read()
        status, face_encoding = self.faceid.encode_face(image)
        return status, face_encoding

    