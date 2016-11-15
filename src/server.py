import thriftpy
from thriftpy.rpc import make_server
from thriftpy.transport import TFramedTransportFactory
import sys
sys.path.append("./ocr/")
import ocr

ocr_thrift = thriftpy.load("ocr.thrift", module_name="ocr_thrift")

class Dispatcher(object):
    def __init__(self):
        print "load_model..."
        #ocr.load_model()

    def scene_ocr(self, images, b_location):
        for index, image in enumerate(images):
            print index
            save_name = "./result/" + str(index) + ".jpg"
            f = open(save_name, 'w')
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
    server = make_server(ocr_thrift.ocr_server, Dispatcher(),
                        "127.0.0.1", 6000,
                        trans_factory=TFramedTransportFactory())
    print("serving...")
    server.serve()

def test_ocr():
    file_name = "./result/0.jpg"
    result = ocr.ocr(file_name)
    print result

if __name__ == "__main__":
    main()
