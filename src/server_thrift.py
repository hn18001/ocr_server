import sys

from ocr_server import ocr_server
from ocr_server.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class Handler:
    def __init__(self):
        self.log = {}

    def func1(self):
        print 'fuct1()'

    def scene_ocr(self, images, b_location):
        for index, image in enumerate(images):
            print index
            save_name = "./result/"+ str(index) + ".jpg"
            f=open(save_name, 'w')
            f.write(image)
            print save_name
            ocr.load_model()
            result = ocr.ocr(save_name)
            print result

        results = []
        result = ocr_thrift.ocr_result(result="hello", roi_left=10, roi_top=10, roi_width=100, roi_height=100)
        results.append(result)

        return results

def main():
    handler = Handler()
    processor = ocr_server.Processor(handler)
    transport = TSocket.TServerSocket(port=6000)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print "Starting the server"
    server.serve()

if __name__ == "__main__":
    main()
