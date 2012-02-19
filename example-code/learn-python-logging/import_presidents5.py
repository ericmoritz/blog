import config_ini
import logging
import csv
from redis import StrictRedis

# We do not want to use __name__ here because __name__ is "__main__"
log = logging.getLogger("presidents.importer")

try:
    reader = csv.reader(open("./presidents.csv"))
    header = reader.next()

    client = StrictRedis()

    for i, row in enumerate(reader):
        key = "president:%s" % (row[0], )
        doc = dict(zip(header, row))

        # simulate a disconnect every 3 operations
        if i % 3 == 0:
            client.disconnect()

        # simulate a failure
        if row[0] == "37":
            raise Exception("Crook.")

        client.set(key, doc)
except:
    log.exception("Dang it.")
