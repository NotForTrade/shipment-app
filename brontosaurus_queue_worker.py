import redis
import json
import os
from pint import UnitRegistry
import pint
import requests


print("Hello world! This is brontosaurus_queue_worker!")



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


def normalize_brontausorus(data: dict):
    
    out = dict()

    key_translation = {
        'Package_ID': 'Shipment_id',
        'Package_Weight': 'Weight',
        'Package_Volume': 'Volume',
        'Emitter': 'Emitter',
        'Reciever': 'Recipient',
        'Emitter_Address': 'Emitter_Address',
        'Reciever_Address': 'Recipient_Address',
        'Expedition_Date': 'Expedition_Date',
        'Estimated_Arrival_Date': 'Estimated_Arrival_Date',
        'Shipment_distance': 'Shipment_distance',
        'Perishable': 'Perishable',
        'Valuable': 'High_Value',
        'Strong': 'Fragile',
        'Plane': 'Includes_Air_Transportation',
        'Boat': 'Includes_Water_Transportation',
        'GrndTrsp': 'Includes_Ground_Transportation',
        'Shipment_Status': 'Shipment_Status'
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
        
    return out


def format_other_data(data: dict):
    return None


# Reading data from the queue
while True:
    # Using BLPOP for blocking pop, replace with LPOP for non-blocking
    message = r.blpop(queue_name, timeout=2)

    if message == None:
        continue
    
    print("The following data has been popped from the redis queue:")
    print(message)

    data = json.loads(message[1])

    print(data)
    print(type(data))

    if queue_name == "brontosaurus_queue":
        normalized_data = normalize_brontausorus(data)

    else:
        normalized_data = format_other_data(data)

    if normalized_data != None:

        # print('-----------------------------------------')
        # print(normalized_data)
        # print('-----------------------------------------')


        # utiliser requests 


        r.hset(f"shipment:{normalized_data["Shipment_id"]}", mapping= normalized_data)