# Intelligent-Checkout-System
Machine Vision Class Project

## Motivation
The barcode based self-checkout system has been widely utilized in grocery stores including Walmart, Target and Kroger. The machine vision based system has a potential to achieve higher efficiency but it has not yet been fully adopted. The software company Mashgin offers a Touchless Checkout System solution using AI. They advertise that their system can identify any items without the need of a barcode, and are 10 times faster than the traditional checkout method. Since it is an industry software, we don’t have access to their implementation. We assume that they are using the object detection model for identifying items by applying face recognition techniques for determining each customer’s identity. Therefore, we are planning to implement this system based on our assumptions.

## Functionality

* Determine the purchased itmes and caculate the subtotal 
* Verify customer identity
* Web-based user interface for both customers and administrators

## Solutions

* Implement object detection using Mask R-CNN model.
* Encode customers' face and save the feature vector to pick file
* Load the pickel file to verify customers' identity using face_recognition libray of python, to protect customers' property security, we are using anti-spoofing model to check if it is a fake face first.
* Build our web-based GUI using Flask, Nginx and Gunicorn

## Dataset

To train the objection detection model, we are going to use MVTec Densely Segmented Supermarket Dataset (MVTec D2S). D2S contains 21,000 high-resolution images that belong to 60 categories. The objects include groceries and everyday products which are exactly what is necessary for this project. The dataset includes images with pixel-wise labels of all object instances which can be used to train the objection recognition model. 

## Progress
* Itegrated face recognition and anti-spoofing :white_check_mark:
* Trained Msk R-CNN on subdataset of D2S. (12 classes) :white_check_mark:
* Build database :x:
* Design web GUI :x:

## Usage

### Clone it from our repository

```
git clone https://github.com/jiamingli9674/Intelligent-Checkout-System.git

```



### Create Virtual Environment (on Windows 10)

```
virtualenv venv --python=3.6
or
conda create -n venv python=3.6

```

### Activate Virtual Environment (on Windows 10)

```
venv\Scripts\activate  
or
conda activate venv

```

### Install required libraries

```
pip install -r requirements.txt 

OR

pip install keras==2.3.1

pip install torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

pip install face_recognition

pip install opencv-python

pip install scikit-image

pip install matplotlib==3.3.0

pip install tensorflow==2.1.0

pip install ipython
```



### Run our face recognition and anti-spoofing test

```
(venv)~/Intelligent-Checkout-System/scripts python app_check_identity.py

```

### Run our Mask R-CNN test

```
(venv)~/Intelligent-Checkout-System/scripts python python python test_RCNN.py 

```
