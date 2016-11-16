# -*- coding: utf-8 -*-

import traceback,sys
import time
import os
import numpy as np
import thriftpy
from thriftpy.transport import TFramedTransportFactory
from thriftpy.rpc import make_client
CNN_i2i_thrift = thriftpy.load('CNN_image2image.thrift', module_name="CNN_image2image_thrift")
import multiprocessing
from multiprocessing import Pool
from PIL import Image
sys.path.append("/usr/lib/python2.7/dist-packages/")
import cv2

class CNNClient:
    def __init__(self, ip="10.15.208.61", port=6800):
        self.ip = ip
        self.port = port
        try:
            self.client = make_client(CNN_i2i_thrift.CNNPredictService,
                    ip, port,trans_factory=TFramedTransportFactory(), timeout=12000) ## timeout ms
            print ip+':'+str(port)

        except Exception as  err:
            print err
            traceback.print_exc()

        return

    def DoPostProcess(self, datalst):
        reqlst = []
        for data in datalst:
            req = CNN_i2i_thrift.Request()
            req.inputImage = data
            reqlst.append(req)

        ret = []
        try:
            print '----'
            reslst = self.client.predict(reqlst)
            print '----', len(reslst)
            #print res
            for i in range(len(reslst)):
                roiimglst = []
                ## get mask image
                maskres = reslst[i].maskResult
                print type(maskres.outputImage), len(maskres.outputImage)
                print maskres.imageChannel
                print maskres.imageWidth
                print maskres.imageHeight
                roiimglst.append(maskres.outputImage)

                ## get roi image
                roilist = reslst[i].roiResults
                for k in range(len(roilist)):
                    roi = roilist[k]
                    val = roi.outputImage
                    resc= roi.imageChannel
                    resw= roi.imageWidth
                    resh= roi.imageHeight
                    print 'c,h,w',resc,resh,resw
                    print 'size:',len(val)

                    roiimglst.append(val)
                ret.append(roiimglst)

        except Exception as err:
            try:
                self.client = make_client(CNN_i2i_thrift.CNNPredictService,
                        self.ip, self.port,trans_factory=TFramedTransportFactory(), timeout=12000) ## timeout ms
            except Exception as  err:
                traceback.print_exc()
                print err
            print err
            traceback.print_exc()
        return ret

def create_opencv_image_from_stream(stream):
    img_array = np.asarray(bytearray(stream), dtype=np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

def create_pil_image_from_buffer(buf):
    import cStringIO
    im = Image.open(cStringIO.StringIO(buf))
    return im

def save_scene_boxes(file_stream_list, index, scene_boxes):
    src_img = create_pil_image_from_buffer(file_stream_list[index])
    print "image size:", src_img.size

    results = []

    border = 0
    for i, box in enumerate(scene_boxes):
        left = box['left']
        top = box['top'] + border
        width = box['width']
        height = box['height'] - border

        left = left / 500.0 * src_img.size[0]
        top = top / 500.0 * src_img.size[1]
        width = width / 500.0 * src_img.size[0]
        height = height / 500.0 * src_img.size[1]
        crop_img = src_img.crop((left, top, left + width, top + height))

        import os
        pid = os.getpid()
        path_prefix = "../result/" + str(pid)
        if not os.path.exists(path_prefix):
            os.system("mkdir " + path_prefix)

        save_name = path_prefix + "/" + str(index) + "_" + str(i) + ".jpg"
        print save_name
        crop_img.save(save_name)

        results.append(save_name)

    return results

def scene_location(file_list, index):
    print "Entering scene_location()..."
    hd = CNNClient(ip="10.15.208.61", port=6800)

    print len(file_list)
    retlist = hd.DoPostProcess(file_list)

    print "len of retlist: ", len(retlist)
    results = []
    for j in range(len(retlist)):
        ret = retlist[j]
        for i in range(len(ret)):
            roi = ret[i]
            save_dir = ""
            save_all_path = ""
            if i == 0:
                import util
                img = create_opencv_image_from_stream(roi)
                print img.shape
                cv2.imwrite("./mask.jpg", img)
                scene_boxes = util.get_scene_box(img)
                print "scene boxes' len:", len(scene_boxes)
                files = save_scene_boxes(file_list, j, scene_boxes)
                results.append(files)

    return results

def crop_img(file_name):
    from PIL import Image
    im = Image.open(file_name)
    width, height = im.size

    crop_im = im.crop((0, 2*height/3, width, height))
    basename = os.path.basename(file_name)
    tempfile = "./temp/" + basename
    crop_im.save(tempfile)
    return tempfile
