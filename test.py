import sys
import hashlib
import timeit
import numpy as np
import pandas as pd
import binascii
import FileReader

#create dataframe:
dfStreamStats = pd.DataFrame(columns = ['count', 'stream'], index = ['hash'])
dfStreamStats.dropna(inplace=True)
dfStreamStats['count'] = dfStreamStats['count'].astype(np.uint32)

f = open(sys.argv[1], "rb")
chunkSize = int(sys.argv[2])

byteStream = f.read(chunkSize)
start = timeit.default_timer()
while len(byteStream) != 0:
  ha = hashlib.sha1(byteStream).hexdigest()

  if ha not in dfStreamStats.index:
    dfStreamStats.loc[ha] = [1, byteStream]
  else:
    dfStreamStats.set_value(ha, 'count', dfStreamStats.loc[ha]['count']+1)

  byteStream = f.read(chunkSize)

dfStreamStats.sort_values('count', ascending=False, inplace=True)
stop = timeit.default_timer()

print("total time:" + str(stop - start))
FileReader.displayStream(dfStreamStats)
