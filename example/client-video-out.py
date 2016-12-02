#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append("./gen-py")
from ocr_server import ocr_server
from ocr_server.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import multiprocessing
from multiprocessing import Pool

def make_client():
    addr = "10.123.16.51"
    port = 6001
    print("Linking to: %s:%s" %(addr, port))
    transport = TSocket.TSocket(addr, port)
    # Buffering is critical, Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)
    # Wrap in protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    # Create a client to use the protocol encoder
    client = ocr_server.Client(protocol)
    # Connect!
    transport.open()

    return client

def process(path):
    client = make_client()

    pid = os.getpid()
    print("[%d] process %s" %(pid, path))
    gluster_name = os.path.basename(path)
    image_names = []
    image_bufs = []
    ocr_results = []
    start_time = time.time()
    processed_images_no = 0
    for root, dir_names, file_names in os.walk(path):
        print('[%d] There are %s files.' %(pid, len(file_names)))
        for file_name in file_names:
            print file_name
            image_names.append(file_name)
            f = open(os.path.join(root, file_name), 'rb')
            buf = f.read()
            f.close()
            image_bufs.append(buf)

            process_images_one_time = 5
            if len(image_bufs) == process_images_one_time:
                print("[%d] Start ocr..." %pid)
                results = client.scene_ocr(image_bufs, True)
                processed_images_no += process_images_one_time
                total_time = time.time() - start_time
                print("[%d] processed images: %d, total time: %d, %f images per second" %(pid, processed_images_no, total_time, processed_images_no*1.0/total_time))
                for result in results:
                    ocr_results.append(result)
                image_bufs = []

        if len(image_bufs) != 0:
            results = client.scene_ocr(image_bufs, True)
            for result in results:
                ocr_results.append(result)

    save_file = "./result/" + gluster_name + ".txt"
    f = open(save_file, 'w')
    for i, ocr_result in enumerate(ocr_results):
        print image_names[i], ocr_result.result
        f.write(image_names[i] + "\t" + ocr_result.result + "\n")

    print("[%d] %s saved sucessfully." %(pid, save_file))
    f.close()

if __name__ == "__main__":
    #path = "./test1"
    path = "/data/heneng/work/scene_generator/src/images/"
    '''
    # single process
    for root, dir_names, file_names in os.walk(path):
       for dir_name in dir_names:
           full_path = os.path.join(root, dir_name)
           process(full_path)

    sys.exit(0)
    '''
    # multi process
    start_time = time.time()
    path_list = []
    for root, dir_names, file_names in os.walk(path):
        print root
        for dir_name in dir_names:
            print dir_name
            full_path = os.path.join(root, dir_name)
            path_list.append(full_path)

    print("Start ocr, there are %d files " %len(path_list))
    pool = Pool(processes=10)
    pool.map_async(process, path_list)

    pool.close()
    pool.join()
    print("End, total time: %f" %(time.time()-start_time))
