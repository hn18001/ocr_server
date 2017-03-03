import os
import time

import ctypes
lualib = ctypes.CDLL('libluajit.so', mode=ctypes.RTLD_GLOBAL)
import lupa
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)

import sys
sys.path.append("./ocr")
import get_line_complex_lection as get_line

def seg_and_ocr(img_path):
    line_imgs = get_line.get_row_lection(img_path)

    ocr_results = ""
    for line_img in line_imgs:
        ocr_result = ocr(line_img)
        if len(ocr_result) > 0:
            ocr_results = ocr_results + ocr_result + "\n"

    return ocr_results
def ocr(img_path):
    # Attention: the path of load_model and recognize!!!
    lua.eval('require ("./ocr/load_model")')
    lua_ocr = lua.eval('''
        function(img_path)
            require('./ocr/recognize')
            result = recognize(img_path)

            return result
        end
    ''')
    result = lua_ocr(img_path)
    result = result.encode('utf-8')
    return result

if __name__ == "__main__":
    file_name = "./1.jpg"
    ocr_results = seg_and_ocr(file_name)
    fp=open("./result.txt", 'w')
    fp.write(ocr_results)
    fp.close()
