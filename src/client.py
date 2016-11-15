import os

import thriftpy
from thriftpy.rpc import client_context
from thriftpy.transport import TFramedTransportFactory

ocr_thrift = thriftpy.load("ocr.thrift", module_name="ocr_thrift")

def main():
    with client_context(ocr_thrift.ocr_server, '127.0.0.1', 6000, trans_factory=TFramedTransportFactory(), socket_timeout=12000) as ocr_server:
        datas = []
        for root, dir_names, file_names in os.walk("./test"):
            for file_name in file_names:
                f = open(os.path.join(root, file_name), 'rb')
                data = f.read()
                datas.append(data)

        results = ocr_server.scene_ocr(datas, True)

        for result in results:
            print result.result, result.roi_left, result.roi_top, result.roi_width, result.roi_height

if __name__ == "__main__":
    main()

