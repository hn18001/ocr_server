import os
import time

import ctypes
lualib = ctypes.CDLL('libluajit.so', mode=ctypes.RTLD_GLOBAL)
import lupa
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)

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
    file_name = "../result/11267/0_0.jpg"
    print ocr(file_name)
