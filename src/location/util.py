import sys
sys.path.append('/usr/lib/python2.7/dist-packages/')
import cv2
import os

def get_bounding_boxes(src_img):
    gray_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2GRAY)
    #gray_img = 255 - gray_img

    connectivity = 4

    output = cv2.connectedComponentsWithStats(gray_img, connectivity, cv2.CV_32S)

    num_labels = output[0]

    labels = output[1]

    stats = output[2]
    centroids = output[3]

    b_boxes = []
    for i in range(1, num_labels): # The first rect is the whole image, it's not needed
        result = {}
        left = stats[i][0]
        top = stats[i][1]
        width = stats[i][2]
        height = stats[i][3]
        area = stats[i][4]

        right = left + width
        bottom = top + height

        #rect_img = cv2.rectangle(src_img, (left, top), (right, bottom), (0, 0, 255), 3)

        result["left"] = left
        result["top"]  = top
        result['width'] = width
        result['height'] = height
        result['area'] = area

        b_boxes.append(result)

    #cv2.imwrite("./rect.jpg", rect_img)

    return b_boxes

def remove_area(img_width, img_height, b_boxes):
    area_thresh = 1000
    width_thresh = 20

    possible_scenes = []
    print b_boxes
    for b_box in b_boxes:
        left = b_box['left']
        width = b_box['width']
        area = b_box['area']

        width_middle = left + width / 2
        width_gap = img_width / 2 - width_middle

        print width_gap
        if abs(width_gap) < width_thresh and area > area_thresh:
            possible_scenes.append(b_box)

    return possible_scenes

def get_scene_box(src_img):
    #src_img = cv2.imread(img_name, cv2.IMREAD_COLOR)

    b_boxes = get_bounding_boxes(src_img)

    img_width = src_img.shape[0]
    img_height = src_img.shape[1]
    possible_scenes = remove_area(img_width, img_height, b_boxes)

    print "possible scenes:", len(possible_scenes)
    for box in possible_scenes:
        left = box['left']
        top = box['top']
        width = box['width']
        height = box['height']

        right = left + width
        bottom = top + height

        src_img = cv2.rectangle(src_img, (left, top), (right, bottom), (0, 0, 255), 3)

    cv2.imwrite("./scene_img.jpg", src_img)

    return possible_scenes

if __name__ == "__main__":
    img_name = "2a9c418035365058470958302f7649e6_269_0.jpg"
    img_name = "./mask/" + img_name

    src_img = cv2.imread(img_name, cv2.IMREAD_COLOR)
    get_scene_box(src_img)


