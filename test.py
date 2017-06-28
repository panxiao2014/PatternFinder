import sys
import hashlib
import timeit

f = open(sys.argv[1], "rb")
chunkSize = int(sys.argv[2])

byteStream = f.read(chunkSize)
start = timeit.default_timer()
while len(byteStream) != 0:
  ha = hashlib.sha256(byteStream).hexdigest()
  byteStream = f.read(chunkSize)

stop = timeit.default_timer()

print("total time:" + str(stop - start))
