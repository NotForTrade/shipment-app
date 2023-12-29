import redis
import json
import os


print("Hello world! This is redis-pop")



# Connect to Redis server
r = redis.Redis(host=os.environ.get('REDIS_HOST'), port=int(os.environ.get("REDIS_PORT")), decode_responses=True)


print("host:", os.environ.get('REDIS_HOST'))
print("port:" , os.environ.get('REDIS_PORT'))



# Define your queue name
queue_name = 'my_queue'


def format_brontausorus_data(data: dict):
    out = dict()
    # Format for the new conventional data
    return out


def format_other_data(data: dict):
    out = dict()
    return out


# Reading data from the queue
while True:
    # Using BLPOP for blocking pop, replace with LPOP for non-blocking
    (queue_name, payload) = r.blpop(queue_name, timeout=0)

    data = json.load(payload)

    print("The following data has been popped from the redis queue:")
    print(queue_name, data, sep="\n")

    if queue_name == "brontosaurus_queue":
        format_brontausorus_data(data)
    else:
        format_other_data(data)

    
