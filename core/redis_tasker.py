import redis
from rq import Queue

r = redis.StrictRedis()
redis_queue = Queue(connection=r)