require('nn')

require('cutorch')
require('cunn')
require('cudnn')
require('optim')
require('paths')
require('nngraph')

--Find the module in the dir of '../src'
package.path = package.path .. ";/data/heneng/work/QYDnnOCR/trunk/src/?.lua;/data/heneng/work/QYDnnOCR/trunk/third_party/lmdb-lua-ffi/src/?.lua;"
package.cpath = package.cpath .. ";/data/heneng/work/QYDnnOCR/trunk/src/?.so"

require('libcrnn')
require('utilities')
require('inference')
require('CtcCriterion')
require('DatasetLmdb')
require('LstmLayer')
require('BiRnnJoin')
require('SharedParallelTable')

require('lfs')

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

start = os.clock()
arg = {}
arg[1] = 3
arg[2] = "/data/heneng/images/baidu-gt/sample_baidu_subtitle/loc_test/"
arg[3] = "./result.txt"
arg[4] = "snapshot_138000.t7"
local dev_id = tonumber(arg[1])
local path = arg[2]
local resuri = arg[3]
local wordlisturi = '/data/heneng/work/QYDnnOCR/trunk/src/word_3567.txt'
id2char_tb = {}
make_dict(wordlisturi, id2char_tb)

local img_tb ={}

cutorch.setDevice(dev_id)
torch.setnumthreads(4)
torch.setdefaulttensortype('torch.FloatTensor')

print("make_dict(): "..(os.clock() - start))
start = os.clock()
--print('Loading model...')
-- Test 1
--local modelDir = '/data/zhangyg/work_torch/model/crnn/3567_5m_4color_7font_shadow_480'
--paths.dofile(paths.concat(modelDir, 'config.lua'))
--local modelLoadPath = paths.concat(modelDir, 'snapshot_168000.t7')
local modelDir = '/data/heneng/work/QYDnnOCR/trunk/model/'
paths.dofile(paths.concat(modelDir, 'config.lua'))
--local modelLoadPath = paths.concat(modelDir, 'snapshot_174000.t7')i
local modelName = arg[4]
local modelLoadPath = paths.concat(modelDir,modelName) 
print("dofile config.lua: ".. (os.clock() - start))
start = os.clock()

gConfig = getConfig()
gConfig.modelDir = modelDir
gConfig.maxT = 0
model, criterion = createModel(gConfig)
--print(modelLoadPath)
local snapshot = torch.load(modelLoadPath)
--print ('snapshot end')

print("createModel: ".. (os.clock() - start))
start = os.clock()
loadModelState(model, snapshot)
model:evaluate()
--print(string.format('Model loaded from %s', modelLoadPath))

print("model:evaluate(): ".. (os.clock() - start))
print("Load model finished.")
