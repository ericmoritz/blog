import logging
from logging import FileHandler, StreamHandler

default_formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")

console_handler = StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(default_formatter)

error_handler = FileHandler("error.log", "a")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(default_formatter)

root = logging.getLogger()
root.addHandler(console_handler)
root.addHandler(error_handler)
root.setLevel(logging.INFO)


log = logging.getLogger()
log.info("Starting experiment")

try:
    raise Exception("I don't know what I'm doing.")
except:
    log.exception("doh.")


