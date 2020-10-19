import cv2

from face_recog.face_id import FaceId
from anti_spoofing.anti_spoofing import check_authenticity

class VideoCamera(object):
    def __init__(self):
        # 通过opencv获取实时视频流
        # url来源见我上一篇博客
        # self.video = cv2.VideoCapture("../data/test_video_spoofing.mp4")
        self.video = cv2.VideoCapture(0)
        self.faceid = FaceId()
        self.faceid.encode_faces() 
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        is_real, frame_auth = check_authenticity(image.copy())
            
        if is_real:
            frame = self.faceid.match_faces(image.copy())     
            image = frame
        else:
            image = frame_auth
        # 因为opencv读取的图片并非jpeg格式，因此要用motion JPEG模式需要先将图片转码成jpg格式图片
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()