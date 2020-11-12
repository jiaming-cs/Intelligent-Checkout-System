import os
import sys
import cv2
import numpy as np
import skimage.io
import matplotlib.pyplot as plt
from app import db
from app.database import Product
from numpy.core.fromnumeric import product


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
        font = cv2.FONT_HERSHEY_DUPLEX
        for i, bbox in enumerate(r["rois"]):
            color = get_random_color()
            color = (int(color[0]), int(color[1]), int(color[2]))
            class_name = self.class_names[r["class_ids"][i]]
            score = r["scores"][i]
            frame = cv2.rectangle(frame, (bbox[1], bbox[0]), (bbox[3], bbox[2]), tuple(color), 3)
            cv2.putText(frame, "{}:{:.2f}".format(class_name, score), (bbox[1] - 10, bbox[0] -10), font, 1.0, color, 1)
        subtotal_text = self.get_subtotal_text([i for i in r["class_ids"]])
        
        position = (30, 30)
        font_scale = 0.75
        color = (255, 0, 0)
        thickness = 3
        font = cv2.FONT_HERSHEY_SIMPLEX
        line_type = cv2.LINE_AA
        text_size, _ = cv2.getTextSize(subtotal_text, font, font_scale, thickness)
        line_height = text_size[1] + 5
        x, y0 = position
        for i, line in enumerate(subtotal_text.split("\n")):
            y = y0 + i * line_height
            cv2.putText(frame,
                        line,
                        (x, y),
                        font,
                        font_scale,
                        color,
                        thickness,
                        line_type)
        
        
        return frame
         
    def detect(self, frame):
        results = self.model.detect([frame], verbose=1)
        r = results[0]
        frame = self.draw_result(frame, r)
        return frame
    
    def get_subtotal_text(self, product_ids):
        
        price_table = {}
        product_list , product_prices = [], []
        if not product_ids:
            return "No Items Found"
        products = Product.query.all()
        
        for pro in products:
            price_table[pro.product_code] = (pro.product_name, pro.product_discount * pro.product_unit_price)
       
        for id_ in product_ids:
            name, price = price_table[id_]
            product_list.append(name)
            product_prices.append(price)
            
        subtoatl_text = ""
        subtotal = 0
        for name, price in zip(product_list, product_prices):
            subtoatl_text += "{}    x1    {:.2f}$".format(name, price)
            subtoatl_text += "\n"
            subtotal += price
        subtoatl_text += "Subtotal : {:.2f}".format(subtotal)
        
        return subtoatl_text
            
            
        
            
    