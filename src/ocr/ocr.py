import os
import time

import ctypes
lualib = ctypes.CDLL('libluajit.so', mode=ctypes.RTLD_GLOBAL)
import lupa
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)



def load_model():
    lua.eval('require ("load_model")')

def ocr(img_path):
    lua.eval('require ("load_model")')
    lua_ocr = lua.eval('''
        function(img_path)
            require('recognize')
            result = recognize(img_path)

            return result
        end
    ''')
    result = lua_ocr(img_path)
    result = result.encode('utf-8')
    return result


if __name__ == "__main__":
    load_model()
    print ocr("../result/0.jpg")
