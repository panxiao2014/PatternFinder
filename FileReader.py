#object to store file read and hash info:
class FileReader:
  fileToBeRead = []
  fileToBeSaved = []
  fileSize = 0
  chunkSize = 0
  readStartPos = 0
  tableSize = 1024000 #length of the hash table, longer one could reduce hash collision

