import sys

sys.path.append("./gen-py")
from ocr_server import ocr_server
from ocr_server.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

sys.path.append("./ocr")
import ocr

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
    addr = "10.123.16.51"
    transport = TSocket.TServerSocket(addr, port=6000)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    #server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    from thrift.server import TProcessPoolServer
    server = TProcessPoolServer.TProcessPoolServer(processor, transport, tfactory, pfactory) # When there is no call, the sub-thread will not be awaken.
    #server = TServer.TForkingServer(processor, transport, tfactory, pfactory)

    print "Starting the server"
    server.serve()

if __name__ == "__main__":
    main()
