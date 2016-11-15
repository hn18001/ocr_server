local py = require('fb.python')

py.exec([=[
import ocr_loc
]=])

py.eval('ocr_loc.detect_images()')

-- The file is inserted to an array
local file_name = {}
file_name[1] = "./images/1/000807f05a4ebddd2fd71c90f85b5dec_0007.jpg"

print(py.eval('ocr_loc.detect_one_image(name)', {name=file_name}))


local ocr_loc_server = py.import('ocr_loc')
print(py.eval(ocr_loc_server.test("hello")))
--print(file_names[1])
