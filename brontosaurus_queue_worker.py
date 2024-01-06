import redis
import json
import os
from pint import UnitRegistry
import pint
import requests


print("Hello world! This is brontosaurus_queue_worker!")


url = 'http://webapp:5000/api/brontosaurus/new-shipment'

# Connect to Redis server
r = redis.Redis(host=os.environ.get('REDIS_HOST'), port=int(os.environ.get("REDIS_PORT")), decode_responses=True)


print("host:", os.environ.get('REDIS_HOST'))
print("port:" , os.environ.get('REDIS_PORT'))



# Define your queue name
queue_name = 'brontosaurus_queue'





# Initialize a unit registry
ureg = UnitRegistry()



# Define a mapping of unit categories to target units
target_units = {
    'length': ureg.kilometer,
    'mass': ureg.kilogram,
    'volume': ureg.meter**3,

    # Add more categories and target units as needed
}



# Function to automatically convert units based on type
def auto_convert_units(input_str):
    # Parse the input string to a Quantity object
    quantity = ureg.parse_expression(input_str)

    # Determine the unit type and get the target unit
    unit_type = quantity.units.dimensionality
    target_unit = None
    for category, unit in target_units.items():
        if unit.dimensionality == unit_type:
            target_unit = unit
            break

    if target_unit:
        # Convert the quantity to the target unit
        return str(quantity.to(target_unit))
    else:
        return str(input_str)


def normalize_brontosaurus(data: dict):
    
    out = dict()

    key_translation = {
        "Emitter": "sender_name",
        "Sender_Address": "sender_address",
        "Reciever_Name": "recipient_name",
        "Recipient_Address": "recipient_address",
        'Expedition_Date': "expedition_date",
        "Wanted_Delivery_Date": "desired_delivery_date",
        "Package_Weight": "weight",
        "Package_Volume": "volume",
        "Perishable": "perishable",
        "Valuable": "high_value",
        "Strong": "fragile",
        "Shipment_Status": "shipment_status"
        }

    for k, v in data.items():
        if not k in key_translation:
            continue
        new_k = key_translation[k]
        if type(v) == type(str):
            try:
                out[new_k] = auto_convert_units(v)
            except pint.errors.UndefinedUnitError:
                out[new_k] = str(v)
        out[new_k] = str(v)
    
    try:
        if out["fragile"] == "True":
            out["fragile"] = "False"
        else:
            out["fragile"] = "True"

        out["brontosaurus Shipment_ID:"] = data["Shipment_ID"]

    except Exception as e:
        print(e)

    out["partner"] = "BRONTOSAURUS"


    # print(out)

    return out


def format_other_data(data: dict):
    return None


# Reading data from the queue
while True:
    # Using BLPOP for blocking pop, replace with LPOP for non-blocking
    message = r.blpop(queue_name, timeout=2)


    if message == None:
        continue

    data = json.loads(message[1])

    if queue_name == "brontosaurus_queue":
        normalized_data = normalize_brontosaurus(data)

    else:
        normalized_data = format_other_data(data)

    if normalized_data != None:

        print("Print before doing the http request!!!")
        response = requests.post(url, json=normalized_data)
    
        print('---------------------------------------------------------------------')
        print(f"HTTP Response: {response.text}")

        #r.hset(f"shipment:{normalized_data["Shipment_id"]}", mapping= normalized_data)