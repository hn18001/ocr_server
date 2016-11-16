import sys
import os
import time

sys.path.append("./gen-py")
from ocr_server import ocr_server
from ocr_server.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


def main():
    addr = "10.123.16.51"
    port = 6000
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

    images = []
    for root, dir_names, file_names in os.walk("../test2"):
        for file_name in file_names:
            f = open(os.path.join(root,file_name), 'r')
            image = f.read()
            f.close()
            images.append(image)

    start = time.time()
    results = client.scene_ocr(images, True)

    for result in results:
        print result.result

    print("ocr's time:%f" %(time.time()-start))

if __name__ == "__main__":
    main()
