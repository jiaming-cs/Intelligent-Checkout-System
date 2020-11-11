import os
import sys
import cv2
import numpy as np
import skimage.io
import matplotlib.pyplot as plt

# Root directory of the project
ROOT_DIR = os.path.abspath("../")

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
# Import COCO config
# sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
from mrcnn.config import Config




# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "models", "mask_rcnn_model", "mask_rcnn_d2s_0100.h5")
# Download COCO trained weights from Releases if needed
# if not os.path.exists(COCO_MODEL_PATH):
#     utils.download_trained_weights(COCO_MODEL_PATH)

# Directory of images to run detection on
IMAGE_DIR = os.path.join(ROOT_DIR, "test_img")

class CocoConfig(Config):
    """Configuration for training on MS COCO.
    Derives from the base Config class and overrides values specific
    to the COCO dataset.
    """
    # Give the configuration a recognizable name
    NAME = "coco"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 2

    # Uncomment to train on 8 GPUs (default is 1)
    # GPU_COUNT = 8

    # Number of classes (including background)
    NUM_CLASSES = 1 + 80  # COCO has 80 classes

class InferenceConfig(CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    NAME = "d2s"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 1

    # Uncomment to train on 8 GPUs (default is 1)
    GPU_COUNT = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 12  # D2S has 13 classes
    
class MaskRCNN():
    
    def __init__(self):
        self.config = InferenceConfig()
        self.model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=self.config)
        self.model.load_weights(COCO_MODEL_PATH, by_name=True)
        self.class_names = ["background", "coca", 'coca_cola_light_05', 'avocado', 'banana_bundle', 'banana_single', 'kiwi', 'pear', 'carrot', 'cucumber', 'lettuce', 'roma_vine_tomatoes', 'zucchini']
       
    def draw_result(self, frame, r):
        def get_random_color():
            return np.random.randint(255, size=(3, ))
        for i, bbox in enumerate(r["rois"]):
            color = get_random_color()
            color = (int(color[0]), int(color[1]), int(color[2]))
            class_name = self.class_names[r["class_ids"][i]]
            score = r["scores"][i]
            frame = cv2.rectangle(frame, (bbox[1], bbox[0]), (bbox[3], bbox[2]), tuple(color), 3)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, "{}:{}".format(class_name, score), (bbox[1] - 10, bbox[0] -10), font, 1.0, color, 1)
        return frame
         
    def detect(self, frame):
        results = self.model.detect([frame], verbose=1)

        r = results[0]

        frame = self.draw_result(frame, r)
        
        return frame