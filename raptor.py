"""
Raptor.py is an external system using the APIs of shipment-app to push new data and updates
It is using the main frame: /api/new-shipment and /api/

"""


import requests
import json
import random
import time



with open("raptor.json") as f:
    word_dataset = json.load(f)



def post_new_shipment():

    # POST URL
    url = 'http://api:5000/api/new-shipment'

    # Generate a random value
    if random.choice([True, False]):
        value = str(random.randint(500, 50000))
    else:
        value = "False"

    # generate the payload
    data = {
    "sender_name": f"{random.choice(word_dataset["names"])} {random.choice(word_dataset["last_names"])}",
    "sender_address": random.choice(word_dataset["addresses"]),
    "recipient_name": f"{random.choice(word_dataset["names"])} {random.choice(word_dataset["last_names"])}",
    "recipient_address": random.choice(word_dataset["addresses"]),
    "desired_delivery_date": f"{random.randint(2025, 2030)}-{random.randint(1, 12)}-{random.randint(1, 31)}",
    "weight": str(random.randint(1, 1000)),
    "volume": str(random.randint(1, 1000)),
    "perishable": random.choice(["True", "False"]),
    "high_value": value,
    "fragile": random.choice(["True", "False"])
    }


    response = requests.post(url, json=data)

    return response.text

    
if __name__ == '__main__':


    while True:
        print(post_new_shipment())

        time.sleep(random.randint(2, 5))

