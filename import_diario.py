from pelican_import import fields2pelican
import pickle

def to_unicode(o):
    if type(o) is str:
        try:
            return o.decode("utf-8")
        except:
            print o
            raise
    else:
        return o

def decode_fields(fields):
    return map(to_unicode, fields)

items = map(decode_fields, pickle.load(open("./entries.pkl")))

fields2pelican(items, "content-x/")
