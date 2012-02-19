import logging
import csv
from redis import StrictRedis

logging.basicConfig()
logging.getLogger("redis.connection").setLevel(logging.DEBUG)

reader = csv.reader(open("./presidents.csv"))
header = reader.next()

client = StrictRedis()

for i, row in enumerate(reader):
    key = "president:%s" % (row[0], )
    doc = dict(zip(header, row))

    # simulate a disconnect every 3 operations
    if i % 3 == 0:
        client.disconnect()

    client.set(key, doc)
