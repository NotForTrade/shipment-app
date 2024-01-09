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
    "fragile": random.choice(["True", "False"]),
    "partner": "RAPTOR"
    }


    response = requests.post(url, json=data)

    return response.text

def get_shipments():
    url = 'http://api:5000/api/shipments?partner=RAPTOR'
    response = requests.get(url)
    return response.json()


def post_shipping_event():
    data = get_shipments()

    try:
        # Exclude all the shipments that are either completed or failed
        status_update_table = {
            "ACKNOWLEDGED": ["PICKED_UP"],
            "IN TRANSIT": ["PARCEL_CENTER", "CUSTOMS", "DELIVERED"],
            "AT PARCEL CENTER": ["PICKED_UP"],
            "UNDERGOING INSPECTION": ["PICKED_UP"]
        }
        updatable_shipments = list()
        for shipment in data:
            if shipment["shipment_status"] in status_update_table.keys():
                updatable_shipments.append(shipment)
        chosen_shipment = random.choice(updatable_shipments)

        print(chosen_shipment)
        input()
        # shipment_id is in the format 'shipment:N', we want to only retrieve the N
        shipment_id = chosen_shipment["shipment_id"].split(':')[1]
        shipment_status = chosen_shipment["shipment_status"]

        # Generating the event
        if shipment_status == "ACKNOWLEDGED":
            event = "PICKED_UP"
        elif random.int(1, 20) == 20:
            event = random.choice(["BROKEN", "LOST"])
        else:
            event = random.choice(status_update_table[shipment_status])
        
        # Generating the shipping_partner_id based on the event
        broken_partner_table = {
            "IN TRANSIT": f"RAPTOR_DELIVERYMAN{random.randint(0,100)}",
            "AT PARCEL CENTER": f"RAPTOR_WHAREHOUSEMAN{random.randint(0,100)}",
            "UNDERGOING INSPECTION": f"CUSTOMS{random.randint(0,100)}"
        }
        shipping_partner_table = {
            "PICKED_UP": f"RAPTOR_DELIVERYMAN{random.randint(0,100)}",
            "PARCEL_CENTER": f"RAPTOR_WHAREHOUSEMAN{random.randint(0,100)}",
            "CUSTOMS": f"CUSTOMS{random.randint(0,100)}",
            "DELIVERED": f"RAPTOR_DELIVERYMAN{random.randint(0,100)}",
        }
        if event in ["BROKEN", "LOST"]:
            shipping_partner_id = broken_partner_table[shipment_status]
        else:
            shipping_partner_id = shipping_partner_table[event]

        # Compiling the shipment_id, event and shipping_partner_id in the payload
        payload = dict(shipment_id=shipment_id, event=event, shipping_partner_id=shipping_partner_id)

        # Posting the new event
        url = 'http://api:5000/api/shipment-event'
        response = requests.post(url, json=payload)

        return response, event
    
    except Exception as e:
        return e




    
if __name__ == '__main__':

    raptor_count = 0
    while True:
        
        if raptor_count < 10:
            if random.choice([True, False]):
                post_new_shipment()
                raptor_count +=1
            else:
                (response, event) = post_shipping_event()
                if event in ["DELIVERED", "BROKEN", "LOST"]:
                    raptor_count -= 1
                else:
                    raptor_count += 1
        else:
            (response, event) = post_shipping_event()
            if event in ["DELIVERED", "BROKEN", "LOST"]:
                raptor_count -= 1
            else:
                raptor_count += 1

        time.sleep(random.randint(2, 5))

