import os
import sys
import time

sys.path.append("./gen-py")
from ocr_server import ocr_server
from ocr_server.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

sys.path.append("./ocr")
import ocr
import get_line_complex_lection as get_line
sys.path.append("./location")
import location

def get_local_ip(ifname):
    import socket
    import fcntl
    import struct
    ip = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', ifname[:15])
        )[20:24])
    except:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.gethostbyname(socket.gethostname())

    return ip

class Handler:
    def __init__(self):
        self.log = {}

    def func1(self):
        print 'fuct1()'

    def scene_ocr(self, images, b_location):
        rlt_results = []
        for image in images:
            total_time = time.time()
            ocr_results = ""
            left = 0
            top = 0
            width = 0
            height = 0

            pid = os.getpid()
            file_prefix = "../result/" + str(pid)
            if not os.path.exists(file_prefix):
                os.system("mkdir " + file_prefix)
            save_name = file_prefix + "/src_img.jpg"
            with open(save_name, 'w') as f:
                f.write(image)
            if b_location == True:
                ocr_results = ocr.seg_and_ocr(save_name)
                left = 0
                top = 0
                width = 0
                height = 0
            else:
                ocr_results = ocr.ocr(save_name)
                # No location, the rect is set to 0
                left = 0
                top = 0
                width = 0
                height = 0

            rlt = ocr_result(result=ocr_results, roi_left=left, roi_top=top, roi_width=width, roi_height=height)
            rlt_results.append(rlt)

            print("total time: %.2fs\n" %(time.time()-total_time))

        return rlt_results

def main():
    handler = Handler()
    processor = ocr_server.Processor(handler)
    #addr = "localhost"
    addr = get_local_ip("eth0")
    port = 6100
    print("Server IP: %s, port: %d" %(addr, port))
    transport = TSocket.TServerSocket(addr, port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    #server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    from thrift.server import TProcessPoolServer
    server = TProcessPoolServer.TProcessPoolServer(processor, transport, tfactory, pfactory) # When there is no call, the sub-thread will not be awaken.
    worker_num = 8
    server.setNumWorkers(worker_num) # Set the number of processes.
    #server = TServer.TForkingServer(processor, transport, tfactory, pfactory)

    print "Starting the server"
    server.serve()

def test_location():
    path = "../test/"

    file_list = []
    for root, dir_names, file_names in os.walk(path):
        for index, file_name in enumerates(file_names):
            file_list = []
            full_name = os.path.join(root, file_name)
            print full_name
            with open(full_name, 'rb') as f:
                buf = f.read()
                file_list.append(buf)

            print "len of file_list: ", len(file_list)
            results, boxes = location.scene_location(file_list)

            for result in results:
                for file in result:
                     print file

if __name__ == "__main__":
    main()
    #test_location()
