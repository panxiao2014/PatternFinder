import numpy as np
import pandas as pd
import binascii

#object to store file read and hash info:
class FileReader:
  TableSize = 1024000 #length of the hash table, longer one could reduce hash collision
  TOP_N = 5 #we only want to see some top stream count patterns

  fileToBeRead = []
  fileToBeSaved = []
  fileSize = 0
  chunkSize = 0
  readStartPos = 0
  
  #for each chunk read, simply use sum() % TableSize to get a hash value, use a table to save each the number of each hash hit: 
  chunkHashCounter = np.zeros(TableSize, dtype=np.uint32)

  #use this table to store offset of each hit in the chunkHashCounter table, so each element in this table is a table of offset of the hit for the hash above:
  offsetTable = [[] for i in range(0, TableSize)]

#this function will print out the most frequent streams and their count
def displayStream(dfStreamStats):
  #stream may be large, we only display limited bytes:
  bytesToDisplay = 16

  print("Count           Stream")
  
  for i in range(0, FileReader.TOP_N):
    count = dfStreamStats.iloc[i]['count']
    
    stream = dfStreamStats.iloc[i]['stream']
    stream = stream[0:bytesToDisplay]
    stream = binascii.hexlify(stream)

    print("%-8d        %s" % (count, str(stream)))
