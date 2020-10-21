import face_recognition
import cv2
import numpy as np
import os
import sys 
import pickle
from const.consts import FACE_DISTANCE_THRESHOLD,\
UNKNOWN, FACE_ID_NO_PEOPLE_EXIST, FACE_ID_MORE_THAN_ONE_PEOPLE, FACE_ID_ENCODING_SUCESS
from app import db
from app.database import RegisteredUser

class FaceId:
    def __init__(self):
        return
            

    def _load_face_encodings(self):
        """
        Load face ids from pickle file

        """
        records = RegisteredUser.query.all()
        if len(records) == 0:
            return None
        face_encodings = dict([(user.first_name + " " + user.last_name ,pickle.loads(user.face_encoding)) for user in records])
        return face_encodings
        
        

    def encode_face(self, frame):
        '''
        Encode faces from image folder (if any) under root directory.
        The encoded object will be stored in pickle files.
        Images are expected named with format firstname_lastname.jpg
        {"name0":obj, "name1":obj} 
        '''       
        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame)
        rows, cols, _ = frame.shape
        font = cv2.FONT_HERSHEY_DUPLEX
        if len(face_locations) > 1:
            status_code = FACE_ID_MORE_THAN_ONE_PEOPLE
            cv2.putText(frame, "More than one people in the image", (cols // 2, rows // 2), font, 1.0, (0, 0, 255), 1)
            return status_code, None, frame
        elif len(face_locations) == 0:
            status_code = FACE_ID_NO_PEOPLE_EXIST
            cv2.putText(frame, "No people in the image", (cols // 2, rows // 2), font, 1.0, (0, 0, 255), 1)
            return status_code, None, frame
        else:
            cv2.putText(frame, "Encoding success", (cols // 2, rows // 2), font, 1.0, (0, 255, 0), 1)
            status_code = FACE_ID_ENCODING_SUCESS
        face_encoding = face_recognition.face_encodings(frame)[0]

        return status_code, face_encoding, frame

    def match_faces(self, frame):
        self.face_encodings = self._load_face_encodings()
        if self.face_encodings:
            self.known_face_names = list(self.face_encodings.keys())
            self.known_face_encodings = [self.face_encodings[name] for name in self.known_face_names]
        else:
            return #TODO
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)

            if matches[best_match_index] and face_distances[best_match_index] < FACE_DISTANCE_THRESHOLD:
                name = self.known_face_names[best_match_index]
            else:
                name = UNKNOWN
            face_names.append(name)

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return frame





    

