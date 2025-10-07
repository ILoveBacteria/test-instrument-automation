import redis
import os

r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), 
                port=os.environ.get('REDIS_PORT', 6379), 
                decode_responses=True
                )
r.ping()
pubsub = r.pubsub()
pubsub.subscribe('can')
for i in pubsub.listen():
    print(i['data'])

