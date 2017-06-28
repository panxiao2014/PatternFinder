import numpy as np

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

  #use this table to store offset of each hit in the chunkHashCounter table, so each element in this table is a table of offset of the hit for the hash:
  offsetTable = []

