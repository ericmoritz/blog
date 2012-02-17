import logging.config
import logging

logging.config.fileConfig("logging.ini")

log = logging.getLogger()

log.info("Starting experiment")

try:
    raise Exception("I don't know what I'm doing.")
except:
    log.exception("doh.")


