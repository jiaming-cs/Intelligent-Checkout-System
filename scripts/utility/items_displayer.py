import cv2
import numpy as np
def display_items(img_path, result, class_label):
    def get_random_color():
        return tuple(np.random.randint(0, 256, size=3))
    def to_tuple_point(point_array):
        return tuple([point_array[1], point_array[0]])

    items_num = result['rois'].shape[0]
    img = cv2.imread(img_path)
    for i in range(items_num):
        color = list(np.random.random(size=3) * 256)
        color = [int(x) for x in color] 
        print(tuple(result['rois'][i, 0:2]))
        img = cv2.rectangle(img, to_tuple_point(result['rois'][i, 0:2]), to_tuple_point(result['rois'][i, 2:4]), color, 2)
        text = class_label[result['class_ids'][i]] + " " + str(result['scores'][i])
        cv2.putText(img, text, to_tuple_point(result['rois'][i, 0:2] + np.array([20, 20])), cv2.FONT_HERSHEY_SIMPLEX, 2, color)
    img = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
    cv2.imshow("result", img)
    cv2.waitKey(0)

