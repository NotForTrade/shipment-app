import requests
import random
import redis

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
        url = 'http://127.0.0.1/api/shipment-event'
        response = requests.post(url, json=payload)
        return response.text, payload
    except Exception as e:
        return e

raptor_counter = 0
if __name__ == '__main__':

    print(post_shipping_event())

