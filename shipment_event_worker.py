import redis
import json
import os
from pint import UnitRegistry
import pint
import requests

print("Initialized shipment event worker")

api_fw_url = 'http://api-internal:5000/api/internal/shipment-event'

r = redis.Redis(host=os.environ.get('REDIS_HOST'), port=int(os.environ.get("REDIS_PORT")), decode_responses=True)

print("host:", os.environ.get('REDIS_HOST'))
print("port:" , os.environ.get('REDIS_PORT'))

# Define your queue name
queue_name = 'shipment_event_queue'

# Reading data from the queue
while True:
    # Using BLPOP for blocking pop, replace with LPOP for non-blocking
    message = r.blpop(queue_name, timeout=2)

    if message == None:
        continue

    # NB: payload is at 2nd position, 1 being the
    # parsing so that requests.post sets the content type correclty
    data = json.loads(message[1])

    print('---------------------------------------------------------------------')
    print("Got a new event, about to forward it to the internal API")

    response = requests.post(api_fw_url, json=data)

    print(f"HTTP Response: {response.text}")
