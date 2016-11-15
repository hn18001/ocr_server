t0 = os.clock()
require('nn')

require('cutorch')
require('cunn')
require('cudnn')
require('optim')
require('paths')
require('nngraph')

-- Find the module in the dir of '../src'
package.path = package.path .. ";../src/?.lua;"
package.cpath = package.cpath .. ";../src/?.so"

require('libcrnn')
require('utilities')
require('inference')
require('CtcCriterion')
require('DatasetLmdb')
require('LstmLayer')
require('BiRnnJoin')
require('SharedParallelTable')

require('lfs')

local py = require('fb.python')

function getfilelist(path, file_table)
    print('get file list ...')
    local cc = 0
    for file in lfs.dir(path) do
        if file ~= '.' and file ~= '..' then
            cc = cc + 1
            --print(cc,file)
            local uri = path..'/'..file
            --print(cc,uri)
            table.insert(file_table, uri)
        end
    end
    table.sort(file_table)
    return 
end


function make_dict(duri, id2char_tb)
    print('make dict ...')
    fp = io.open(duri, 'r')
    assert(fp)
    cc = 0
    for line in fp:lines() do
        --print(line)
        cc = cc + 1
        id2char_tb[cc] = line
    end
    fp:close()
    print('dict size:',#id2char_tb)
end

print(string.format('time cost load libs: %.2fs\n', os.clock()-t0))
t0 = os.clock()
local dev_id = tonumber(arg[1])
local path = arg[2]
local resuri = arg[3]
local wordlisturi = '../src/word_3567.txt'
local id2char_tb = {}
make_dict(wordlisturi, id2char_tb)
print(string.format('time cost make_dict(): %.2fs\n', os.clock()-t0))
t0 = os.clock()

local img_tb ={}
getfilelist(path, img_tb)  -- get images in path
print('img num:',#img_tb)

cutorch.setDevice(dev_id)
torch.setnumthreads(2)
torch.setdefaulttensortype('torch.FloatTensor')
print(string.format('time cost getfilelist(): %.2fs\n', os.clock()-t0))
t0 = os.clock()

--print('Loading model...')
-- Test 1
--local modelDir = '/data/zhangyg/work_torch/model/crnn/3567_5m_4color_7font_shadow_480'
--paths.dofile(paths.concat(modelDir, 'config.lua'))
--local modelLoadPath = paths.concat(modelDir, 'snapshot_168000.t7')
local modelDir = '../model/'
paths.dofile(paths.concat(modelDir, 'config.lua'))
--local modelLoadPath = paths.concat(modelDir, 'snapshot_174000.t7')i
local modelName = arg[4]
local modelLoadPath = paths.concat(modelDir,modelName) 
print(string.format('time cost dofile(): %.2fs\n', os.clock()-t0))
t0 = os.clock()

gConfig = getConfig()
gConfig.modelDir = modelDir
gConfig.maxT = 0
local model, criterion = createModel(gConfig)

print(string.format('time cost createModel(): %.2fs\n', os.clock()-t0))
t0 = os.clock()
--print(modelLoadPath)
local snapshot = torch.load(modelLoadPath)
--print ('snapshot end')
loadModelState(model, snapshot)
model:evaluate()
--print(string.format('Model loaded from %s', modelLoadPath))

print(string.format('time cost  model:evaluate(): %.2fs\n', os.clock()-t0))
t0 = os.clock()
-- Import python module of OCR location
py.exec([=[
import ocr_loc
]=])
--local ocr_loc_server = py.import('ocr_loc')

print('do predict')
t0 = os.clock()
fpw = io.open(resuri, 'w')
assert(fpw)
for i=1,#img_tb do
    local imagePath = img_tb[i]
    print(imagePath) 
    -- OCR location
    -- Return the loc images
    local img_path = {}
    img_path[1] = imagePath
    local loc_results = py.eval('ocr_loc.detect_one_image(name)', {name=img_path})

    local ocr_results = ""
    for j=1, #loc_results do
        print("loc_result:"..loc_results[j])
        local img = loadAndResizeImage(loc_results[j])
        if img == nil then
            print('invalid: ',loc_results[j]) 
        else
            local text, raw = recognizeImageLexiconFree(model, img)
            local resstr = ''
            ch_tb = split(text, ' ')
         
            for k = 1,#ch_tb do
                cid = tonumber(ch_tb[k])
                if cid ~= nil then
                    local char = id2char_tb[cid-1] --first cid is space
                    resstr = resstr..char
                end
            end
        
            print(resstr)
            ocr_results = ocr_results..resstr..";"
        end
    end
            
    local ind = string.find(imagePath, '/[^/]*$')
    local imgname = string.sub(imagePath, ind+1)
    print(i,imgname, resstr)
    resline = string.format("%s: %s\n", imgname,ocr_results) 
    fpw:write(resline)
end
fpw:close()
print(string.format('time cost: %.2fs\n', os.clock()-t0))
