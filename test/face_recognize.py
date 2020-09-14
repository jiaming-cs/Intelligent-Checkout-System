#import the necessar libraries
import cv2

#Method for generating dataset to recognize a person
def generate_dataset(img, id, img_id):
	#write the image in a data dir
	cv2.imwrite("data/user." + str(id)+"."+str(img_id)+".jpg",img)

#Method that draws a boundary around the detected feature
def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text):
	#Covert image to grayscale
	gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	#detect features in gray-scale, return coordinates, width and height of features
	features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
	coords = []
	#draw rectangle around the feature and label it.
	for (x,y,w,h) in features:
		cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
		cv2.putText(img, text, (x, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
		coords = [x,y,w,h]
	return coords

#Method for detecting the features
def detect(img, faceCascade, img_id):
	color = {"blue":(255,0,0), "red":(0,0,255), "green":(0,255,0), "white":(255,255,255)}
	coords = draw_boundary(img, faceCascade, 1.1, 10, color['blue'], "Face")

	if len(coords)==4:
		#Update region of interest by cropping the image
		roi_img = img[coords[1]:coords[1]+coords[3],coords[0]:coords[0]+coords[2]]
		#Assign a unique id to each user.
		user_id = 1
		#img_id for making name of each unique image.
		generate_dataset(roi_img, user_id, img_id)
	return img

#Load the classifiers
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#Capture real time video stream.
video_capture = cv2.VideoCapture(0)

#Initialize the img_id with 0
img_id = 0

while True:
	if img_id % 50 == 0:
		print("Collected ", img_id, " images")
	#Read image from video stream
	_, img = video_capture.read()
	#Call the method defined above.
	img = detect(img, faceCascade, img_id)
	#Writing processed image in a new window
	cv2.imshow("face detection", img)
	img_id += 1
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

#Turn the webcam off
video_capture.release()
#Destroy the output window
cv2.destroyAllWindows()