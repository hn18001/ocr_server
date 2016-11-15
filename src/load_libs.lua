require('nn')

start = os.clock()
require('cutorch')
require('cunn')
require('cudnn')
require('optim')
require('paths')
require('nngraph')

print(os.clock() - start)
start = os.clock()
package.path = package.path..";../src/?.lua"
package.cpath = package.cpath..";../src/?.so" 
require('libcrnn')
require('utilities')
require('inference')
require('CtcCriterion')
require('DatasetLmdb')
require('LstmLayer')
require('BiRnnJoin')
require('SharedParallelTable')


require('lfs')
print(os.clock() - start)
