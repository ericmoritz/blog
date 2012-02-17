import logging
from logging import FileHandler, StreamHandler, Formatter

redis_conn_handler = StreamHandler() # FileHandler("/tmp/redis.connection.log")
redis_conn_handler.setFormatter(Formatter('%(asctime)s:%(levelname)s:%(message)s'))

redis_log = logging.getLogger("redis.connection")
redis_log.addHandler(redis_conn_handler)
redis_log.setLevel(logging.DEBUG)
