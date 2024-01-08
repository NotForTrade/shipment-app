import requests
import random
import redis

def get_shipments():

    # url = 'http://api:5000/api/shipments?partner=RAPTOR'

    url = 'http://127.0.0.1/api/shipment/1'

    response = requests.get(url)

    return response.json()

# WIP
def post_shipping_event():

    url = 'http://127.0.0.1/api/shipment-event'

    data = get_shipments()

    updatable_status = {
        "ACKNOWLEDGED": ["PICKED_UP"],
        "IN TRANSIT": ["PARCEL_CENTER", "CUSTOMS", "DELIVERED"],
        "AT PARCEL CENTER": ["PICKED_UP"],
        "UNDERGOING INSPECTION": ["PICKED_UP"]
    }

    updatable_shipments = list()
    for shipment in data:
        if data["shipment_status"] in updatable_status:
            updatable_shipments.append(shipment)

    chosen_shipment = random.choice(updatable_shipments)

    shipment_id = chosen_shipment["shipment_id"]

    
    # payload = dict(shipment_id=)

    # response = requests.post(url, payload)



if __name__ == '__main__':
    # post_shipping_event()

    # print(get_shipments())

    r = redis.Redis(host='127.0.0.1', port=30000, decode_responses=True)

    print(r.get(f'shipment:{1}'))