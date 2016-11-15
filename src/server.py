import sys
import socket
import fcntl
import struct

sys.path.append("./gen-py")
from ocr_server import ocr_server
from ocr_server.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

sys.path.append("./ocr")
import ocr

def get_local_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])

class Handler:
    def __init__(self):
        self.log = {}

    def func1(self):
        print 'fuct1()'

    def scene_ocr(self, images, b_location):
        ocr_results = []
        for index, image in enumerate(images):
            save_name = "../result/"+ str(index) + ".jpg"
            f=open(save_name, 'w')
            f.write(image)

            result = ocr.ocr(save_name)
            #print ocr_result
            ocr_results.append(result)

        results = []
        for result in ocr_results:
            rlt = ocr_result(result=result, roi_left=10, roi_top=10, roi_width=100, roi_height=100)
            results.append(rlt)

        #result = ocr_result(result="234", roi_left=10, roi_top=10, roi_width=100, roi_height=100)
        #results.append(result)
        #print "results:", results
        return results

def main():
    handler = Handler()
    processor = ocr_server.Processor(handler)
    #addr = "localhost"
    addr = get_local_ip("eth0")
    port = 6000
    print("Server IP: %s, port: %d" %(addr, port))
    transport = TSocket.TServerSocket(addr, port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    #server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    from thrift.server import TProcessPoolServer
    server = TProcessPoolServer.TProcessPoolServer(processor, transport, tfactory, pfactory) # When there is no call, the sub-thread will not be awaken.
    server.setNumWorkers(3) # Set the number of processes.
    #server = TServer.TForkingServer(processor, transport, tfactory, pfactory)

    print "Starting the server"
    server.serve()

if __name__ == "__main__":
    main()
