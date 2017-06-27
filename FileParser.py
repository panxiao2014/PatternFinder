#FileParser.py -- read a file from user specific input. Each time read user specific chunk, calculate the hash, count on the hit of each hash,
#and store the result into a user specific file

#example:
#python FileParser.py test.doc 8 testDB
# test.doc: file to be read
# 8: read 8k every time
# testDB: save file info to testDB

import FileReader
import sys
import os
import hashlib
import timeit
import numpy as np
import pickle
from pathlib import Path


#main:
if len(sys.argv) == 1:
  print('         Usage: read a file, parse it, and store parse info into a file\n\
         Example: python FileReader.py test.doc 8192 1000 testDB\n\
           test.doc: file to be read\n\
           8192: read 8k bytes every time\n\
           1000: start offset when reading\n\
           testDB: save parse info to testDB')
  sys.exit(0)

reader = FileReader.FileReader()

reader.fileToBeRead = sys.argv[1]
reader.fileToBeSaved = sys.argv[4]
reader.fileSize = os.path.getsize(sys.argv[1])
reader.chunkSize = int(sys.argv[2])
reader.readStartPos = int(sys.argv[3])
reader.fileHash = np.zeros(reader.tableSize, dtype=np.uint32)
#use this table to store offset of each hit in the fileHash table
reader.offsetTable = []
for i in range(0, reader.tableSize):
  reader.offsetTable.append([])

#open file as binary:
f = open(reader.fileToBeRead, "rb")

#jump to start position:
tempHex = [f.read(1) for i in range(0, reader.readStartPos)]

bytesChunk = np.fromstring(f.read(reader.chunkSize), dtype=np.uint8)

i = 0 
totalSum = 0

start = timeit.default_timer()
while bytesChunk.size != 0:
  tempHash = bytesChunk.sum() % reader.tableSize
  reader.fileHash[tempHash] += 1

  #this is not the real offset, but it can be used to calculate offset:
  reader.offsetTable[tempHash].append(i)

  bytesChunk = np.fromstring(f.read(reader.chunkSize), dtype=np.uint8) #use numpy to do summation is much faster than ordinary array
  i+=1
stop = timeit.default_timer()

print("loop: " + str(i))
print("min:" + str(reader.fileHash.min()) + " max:" + str(reader.fileHash.max()) + " at index:" + str(reader.fileHash.argmax()) +" mean:" + str(reader.fileHash.mean()))
print("cost time: ")
print(stop-start)

#save FileReader to file:
if Path(reader.fileToBeSaved).is_file():
  os.remove(reader.fileToBeSaved)

with open(reader.fileToBeSaved, 'wb') as pickler:
  pickle.dump(reader, pickler, pickle.HIGHEST_PROTOCOL)

f.close()
