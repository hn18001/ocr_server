# code for processing sutra lection with opencv.
# auth : Li zhichao
# data : 2016-12-13

# -*- coding:UTF-8 -*-

from __future__ import division
import cv2
import os
import numpy as np

def rotate_imgs(line_imgs):
    from PIL import Image
    for line_img in line_imgs:
        im = Image.open(line_img)
        width, height = im.size
        print width, height
        rotate_img = im.rotate(90, expand = 1).save(line_img)

def get_row_lection(img_path):
    base_name = os.path.basename(img_path)
    img_list = []
    save_path = "../result/%d" %os.getpid()
    if not os.path.exists(save_path):
        os.system("mkdir " + save_path)
    cropped_path = "../cropped_img/"
    # step 1
    src_image, threshold_image = get_threshold_image(img_path)
    # step 2
    #threshold_image = denoise(new_file, threshold_image)
    # step 3
    #crop_src_image, crop_threshold_image = get_lection_position(src_image, threshold_image)
    # step 4
    #middle_point_sum = remove_interfere(threshold_image)
    middle_point_sum = 0
    # step 5
    dilate_image = get_dilate_image(threshold_image, middle_point_sum)
    # step 6
    crop_src_image, line_imgs = get_retangle_contours(base_name, save_path, src_image, dilate_image)
    cv2.imwrite(cropped_path + '/cut_image_%s.jpg' % base_name, crop_src_image)

    rotate_imgs(line_imgs)
    return line_imgs

# 1.gray and threshold image
def get_threshold_image(img_path):
	print 'step 1.gray and threshold image'
	# Load image
	src_image = cv2.imread(img_path)
	# convert image to gray and blur it
	gray_image = cv2.cvtColor(src_image, cv2.COLOR_RGB2GRAY)
	blur_image = cv2.blur(gray_image, (5,5))
	ret, threshold_image = cv2.threshold(blur_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
	cv2.imwrite("./bin.jpg", threshold_image)
	return src_image, threshold_image

# 2.remove noise pixel
def denoise(threshold_image):
	print 'step 2.remove noise pixel'
	# close
	threshold_image_copy = threshold_image.copy()
	close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(50, 50))
	closed_image = cv2.morphologyEx(threshold_image, cv2.MORPH_CLOSE, close_kernel)

	contours, hierarchy = cv2.findContours(closed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	pos_shift = 2
	for count in contours:
		if (len(count) < 50):
			x, y, w, h = cv2.boundingRect(count)
			cv2.rectangle(threshold_image_copy,(x,y),(x+w,y+h),(255,0,0),5)
			threshold_image[y-pos_shift:y+h+pos_shift, x-pos_shift:x+w+pos_shift] = 0

	return threshold_image

# 3.horizontal project and get the lection fixed-position
def get_lection_position(src_image, threshold_image):
	img_height, img_width = threshold_image.shape
	row_sum = []
	up_min_pos = 500
	up_max_pos = 1000
	down_min_pos = 3000
	down_max_pos = 3500
	min_differ = 0
	min_index = 0
	max_differ = 0
	max_index = 0
	for i in range(up_min_pos, up_max_pos):
		sum = 0
		for j in range(img_width):
			sum = sum + threshold_image[i, j]
		if i > up_min_pos:
			pre_sum = cur_sum
			cur_sum = sum
			differ = cur_sum - pre_sum
			if min_differ > differ:
				min_differ = differ
				min_index = i
		else:
			cur_sum = sum

	for i in range(down_min_pos, down_max_pos):
		sum = 0
		for j in range(img_width):
			sum = sum + threshold_image[i, j]
		if i > down_min_pos:
			pre_sum = cur_sum
			cur_sum = sum
			differ = cur_sum - pre_sum
			if max_differ < differ:
				max_differ = differ
				max_index = i
		else:
			cur_sum = sum
	print 'max_index: %d, min_index: %d' % (min_index, max_index)
	crop_shift = 20
	crop_threshold_image = threshold_image[min_index + crop_shift : max_index - crop_shift,:]
	crop_src_image = src_image[min_index + crop_shift : max_index - crop_shift,:].copy()
	return crop_src_image, crop_threshold_image

# 4.vertical project, get rid of interfere factor which results to low pixel.
def remove_interfere(crop_threshold_image):
	print 'step 4.vertical project, get rid of interfere factor which results to low pixel'
	img_height, img_width = crop_threshold_image.shape
	threshold_value = 200
	distance = 100

	width_sum = []
	for j in range(img_width):
		sum = 0
		for i in range(img_height):
			sum = sum + crop_threshold_image[i, j]
		width_sum.append(sum/255)
	width_sum[0] = 0
	flag = 'false'
	change_point = 0
	middle_point_sum = []
	for k in range(1, len(width_sum)):
		if width_sum[k] >= threshold_value:
			width_sum[k] = 1
			if (flag == 'true') and (width_sum[k] != width_sum[k-1]):
				flag = 'false'
				middle_point = int((change_point + k)/2)
				if len(middle_point_sum) >= 1 and middle_point - middle_point_sum[-1] <= distance:
					middle_point_sum[-1] = int((middle_point_sum[-1]+middle_point)/2)
				else:
					middle_point_sum.append(middle_point)
		else:
			width_sum[k] = 0
			if (flag == 'false') and (width_sum[k] != width_sum[k-1]):
				flag = 'true'
				change_point = k
	print 'middle_point: %s' %  middle_point_sum
	return middle_point_sum

# 5.get dilate image
def get_dilate_image(crop_threshold_image, middle_point_sum):
	print 'step 5.get dilate image'
	#cv2.imwrite(new_file + '/5.1-crop_threshold_image.jpg', crop_threshold_image)
	dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1, 100))
	dilate_image = cv2.dilate(crop_threshold_image, dilate_kernel)
	#for i in middle_point_sum:
	#	dilate_image[:,i-5:i+5] = 0
	cv2.imwrite('./dilate.jpg', dilate_image)
	return dilate_image

# 6.get retangle
def get_retangle_contours(img_name, save_path, crop_src_image, dilate_image):
    print 'step 6.get retangle'
    _, contours, hierarchy = cv2.findContours(dilate_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    i = 1
    print("contours' num:%d" %len(contours))
    rlt = []
    for count in contours:
        x, y, w, h = cv2.boundingRect(count)
        if h > 50 and w > 10:
            roi = crop_src_image[y:y+h, x:x+w]
            #roi = 255-roi
            save_name = save_path + "/%s_%02d.jpg" % (img_name, i)
            rlt.append(save_name)
            cv2.imwrite(save_name, roi)
            i = i + 1
            cv2.rectangle(crop_src_image,(x,y),(x+w,y+h),(0,0,255),2)
    print 'len(contours): %d, len(cut): %d\n' % (len(contours),i)
    cv2.imwrite("/home/dzj_user/page_seg.jpg", crop_src_image)
    return crop_src_image, rlt

def main(src_path):
    min_thresh = 100
    max_thresh = 255
    img_path = get_row_lection(src_path)
    print img_path

if __name__ == "__main__":
	src_path = '..//1.jpg'
	main(src_path)
