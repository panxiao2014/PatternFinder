#PatternFinder.py -- Retrieve a stored object generated by FileParser, find data patterns in it

import FileReader
import sys
import pickle
import numpy as np
import pandas as pd
import timeit
import hashlib
import pickle
import os
from pathlib import Path

#main:
if len(sys.argv) == 1:
  print('         Usage: read a file, parse it and find data patterns in it\n\
         Example: python PatternFinder.py test.doc 8192 1000 testDB \n\
           test.doc: file to be read and parsed\n\
           8192: read chunk\n\
           1000: offset for the read to begin\n\
           testDB: file that saves the parse result')
  sys.exit(0)

reader = FileReader.FileReader()

reader.fileToBeRead = sys.argv[1]
reader.fileToBeSaved = sys.argv[4]
reader.fileSize = os.path.getsize(sys.argv[1])
reader.chunkSize = int(sys.argv[2])
reader.readStartPos = int(sys.argv[3])


#open file as binary:
f = open(reader.fileToBeRead, "rb")

#jump to start position:
f.seek(reader.readStartPos, 0)

bytesChunk = np.fromstring(f.read(reader.chunkSize), dtype=np.uint32)

i = 0 
start = timeit.default_timer()
while bytesChunk.size != 0:
  #in preprocessing, simply use sum() % TableSize to get hash
  #use numpy to do summation is much faster than ordinary array:
  tempHash = bytesChunk.sum() % reader.TableSize
  reader.chunkHashCounter[int(tempHash)] += 1

  #this is not the real offset, should multiply by chunk size to get the offset:
  reader.offsetTable[int(tempHash)].append(i)

  try:
    bytesChunk = np.fromstring(f.read(reader.chunkSize), dtype=np.uint32)
  except ValueError:
    break
    
  i+=1

f.close()

print("======================Preprocessing=======================")
print("File size:" + str(reader.fileSize) + " Read chunk size:" + str(reader.chunkSize) + " Start offset:" + str(reader.readStartPos))
print("Read loop: " + str(i))
print("Hash max count:" + str(reader.chunkHashCounter.max()) + " at index:" + str(reader.chunkHashCounter.argmax()) +" mean count:" + str(reader.chunkHashCounter.mean()))
print("==========================================================\n\n")


#create pandas DataFrame:
dfFilePreprocess = pd.DataFrame(pd.Series(reader.chunkHashCounter))
dfFilePreprocess.rename(columns={0:'count'}, inplace=True)

#add offset table to dataframe as another column:
dfFilePreprocess['offset'] = pd.Series(reader.offsetTable)

#sort table by using 'count' column:
dfFilePreprocess.sort_values(['count'], ascending=[False], inplace=True)

#change table index to become a column 'hash_val', it represents the preprocessing hash value for each row:
dfFilePreprocess.reset_index(inplace=True)
dfFilePreprocess.rename(columns={'index':'hash_val'}, inplace=True)

print("====================Preprocessing result==================")
#The output of DataFrame has the following form:
#   hash_val  count        offset
#0       381      4  [0, 2, 6, 9]
#1         0      2        [4, 5]
#2      1660      2        [1, 7]
#3      1549      1          [10]
#4      1591      1           [8]
print(dfFilePreprocess.head())
print("==========================================================\n\n")

#For the top N hash count, get each byte chunk by using the offset. This time use sha to get hash value and use it as index to count the same byte stream pattern: 
topBytesStats = {}

def parseAndGetBytesCount(topBytesStats, dfRow):
  #open file, and jump to the start offset:
  f = open(reader.fileToBeRead, "rb")
  f.seek(reader.readStartPos, 0)

  offset = 0
  for i, val in enumerate(dfRow['offset']):
    if i == 0:
      offset = val * reader.chunkSize
    else:
      offset = (val - dfRow['offset'][i-1] - 1) * reader.chunkSize

    f.seek(offset, 1)
    byteStream = f.read(reader.chunkSize)
  
    #get sha hash value, so hash collision will be low possibility:
    ha = hashlib.sha1(byteStream).hexdigest()

    if ha not in topBytesStats:
      topBytesStats[ha] = {'stream': byteStream, 'count': 1}
    else:
      topBytesStats[ha]['count'] += 1

  f.close()


for i in range(0, reader.TOP_N):
  parseAndGetBytesCount(topBytesStats, dfFilePreprocess.iloc[i])


#create panda DataFrame, to save final result:
dfStreamStats = (pd.DataFrame(topBytesStats)).transpose()
dfStreamStats.sort_values(['count'], ascending=[False], inplace=True)
dfStreamStats.index.names = ['hash']

stop = timeit.default_timer()

#temp DataFrame for printing:
print("=======================Final result=======================")
print("Cost time: " + str(stop-start) + "\n")
FileReader.displayStream(dfStreamStats)
print("==========================================================\n")

#add stats to FilerReader, so we can load and parse it:
reader.dfFilePreprocess = dfFilePreprocess
reader.dfStreamStats = dfStreamStats

#save it:
if Path(reader.fileToBeSaved).is_file():
  os.remove(reader.fileToBeSaved)
with open(reader.fileToBeSaved, 'w+b') as pickler:
  pickle.dump(reader, pickler, pickle.HIGHEST_PROTOCOL)

