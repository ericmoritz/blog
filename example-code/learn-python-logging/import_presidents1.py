import csv
from redis import StrictRedis

reader = csv.reader(open("./presidents.csv"))
header = reader.next()

client = StrictRedis()

for row in reader:
    key = "president:%s" % (row[0], )
    doc = dict(zip(header, row))

    client.set(key, doc)
