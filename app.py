from flask import Flask, jsonify, render_template, request, abort, Response
import random
import json
import os
import pint
from pint import UnitRegistry
import redis
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query

import time
import datetime

app = Flask(__name__)


redis_host=os.environ.get("REDIS_HOST")
redis_port=int(os.environ.get("REDIS_PORT"))

if redis_host != None and redis_port != None:
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)



SHIPMENT_COUNTER = "SHIPMENT_COUNTER"






shipment_id_increment = 0




## ------------------------------------------------------------------
## External connectors

@app.route("/connector/brontosaurus", methods=["POST"])
def brontosaurus_push_redis():
    payload = json.dumps(request.json)

    queue = "brontosaurus_queue"

    app.logger.warning(f"The following data has been pushed to the redis queue: queue: {queue} payload: {payload}")

    try:
        r.rpush(queue, payload)
    except redis.RequestException:
        abort(500)

    return json.dumps({"status": "OK"})



## ------------------------------------------------------------------
## API - DB



valid_keys = ['Shipment_id', 'Weight', 'Volume', 'Emitter', 'Recipient', 
              'Emitter_Address', 'Recipient_Address', 'Expedition_Date', 
              'Estimated_Arrival_Date', 'Shipment_distance', 'Perishable', 
              'High_Value', 'Fragile', 'Includes_Air_Transportation', 
              'Includes_Water_Transportation', 'Includes_Ground_Transportation', 
              'Shipment_Status']


@app.route('/api', methods=['GET'])
def api_get():

    out = list()
    
    # Collecting the key list of the redis database
    for key in r.scan_iter("shipment:*"):
        
        row = json.loads(r.get(key))
        row["shipment_id"] = key
        out.append(row)
    

    return out, 200




@app.route('/api/shipping-event', methods=['POST'])
def api_post_shipping_event():

    payload = request.json
    
    shipment_id = payload["shipment_id"]


    try:
        raw_data = r.get(shipment_id)
        
        data = json.loads(raw_data)
    except Exception as e:
        return f"Internal error: {e}", 500

    event_type = payload["event_type"]
    match event_type:
        case "DEPOSIT":
            shipment_status = "AT LOCAL PARCEL"
            
        case "IN_TRANSIT":
            shipment_status = "IN TRANSIT"
            data["expedition_date"] = str(datetime.datetime.fromtimestamp(time.time()))
            
        case "PARCEL_CENTER":
            shipment_status = "AT PARCEL CENTER"

        case "SUBMITTED_TO_CUSTOMS":
            shipment_status = "UNDERGOING INSPECTION"

        case "RECIEVED_BY_CUSTOMS":
            shipment_status = "CLEARED BY CUSTOMS"

        case "FINAL_DELIVERY":
            shipment_status = "APPROACHING DESTINATION"

        case "DELIVER":
            shipment_status = "COMPLETED"
            
        case "BROKEN":
            shipment_status = "FAILED - DAMAGED"

        case "LOST":
            shipment_status = "FAILED - LOST"

    
    new_event = dict(
        datetime=str(datetime.datetime.fromtimestamp(time.time())),
        shipment_status=shipment_status,
        shipping_partner_id=payload["shipping_partner_id"]
    )
    
    
    try:
        
        # Check if the shipment is too late
        # perishable = data["perishable"]

        data["shipment_status"] = shipment_status
        data["event_history"].append(new_event)

        app.logger.warning(f"New data: {data}")

        r.set(shipment_id, value=json.dumps(data))

        return "ok", 200

    except Exception as e:

        return f"An internal error occured: {e}", 500


@app.route('/api/brontosaurus/new-shipment', methods=['POST'])
def api_post_brontosaurus_new_shipment():


    out = request.json


    app.logger.warning(f"OUT: {out}")


    global SHIPMENT_COUNTER

    # Increment the key value
    r.incr(SHIPMENT_COUNTER)

    # Set the shipment id to the current counter set on redis
    shipment_id = f"shipment:{r.get(SHIPMENT_COUNTER)}"

    # app.logger.warning(f"out content: {out}")
    # app.logger.warning(f"Shipment_id value: {normalized_data["Shipment_id"]}")
    try:
        r.set(shipment_id, value=json.dumps(out))
    except Exception as e:
        app.logger.error(e)
        abort(500)

    return f"Data created successfully: \n{out}", 201


@app.route('/api/new-shipment', methods=['POST'])
def api_post_new_shipment():

    data_in = request.json

    out ={
        "shipment_status": "ACKNOWLEDGED",
        "sender_name": data_in["sender_name"], #str()
        "sender_address": data_in["sender_address"], #str()
        "recipient_name": data_in["recipient_name"], #str()
        "recipient_address": data_in["recipient_address"], #str()
        "creation_time": str(datetime.datetime.fromtimestamp(time.time())),
        "expedition_date": "-",
        "desired_delivery_date": data_in["desired_delivery_date"], #datetime.date()
        "weight": data_in["weight"], #int()
        "volume": data_in["volume"], #int()
        "perishable": data_in["perishable"], #datetime.date() | None
        "high_value": data_in["high_value"], #int() | None
        "fragile": data_in["fragile"], #bool()
        "event_history": []
    }

    global SHIPMENT_COUNTER

    # Increment the key value
    r.incr(SHIPMENT_COUNTER)

    # Set the shipment id to the current counter set on redis
    shipment_id = f"shipment:{r.get(SHIPMENT_COUNTER)}"

    # app.logger.warning(f"out content: {out}")
    # app.logger.warning(f"Shipment_id value: {normalized_data["Shipment_id"]}")
    
    r.set(shipment_id, value=json.dumps(out))

    return f"Data created successfully: \n{out}", 201



ureg = UnitRegistry()

# Define a mapping of unit categories to target units
target_units = {
    'length': ureg.kilometer,
    'mass': ureg.kilogram,
    'volume': ureg.meter**3,
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





def check_data_is_normalized(data: dict):

    global valid_keys
    # Check no key is missing from data
    app.logger.warning(f"The 2 sets are: {set(data.keys())} {set(valid_keys)}")


    if set(data.keys()) != set(valid_keys): # We exclude Shipment_id as we add it
        return None
    
    # Convert the unit of values in data to ensure they're normalized
    keys_with_unit = {'Weight', 'Volume', 'Shipment_distance'}

    out = dict()

    for k, v in data.items():
        if not k in keys_with_unit:
            out[k] = str(v)
            continue
        if type(v) == type(str):
            try:
                out[k] = auto_convert_units(v)
            except pint.errors.UndefinedUnitError:
                out[k] = str(v)
        out[k] = str(v)

    return out


def process_post_data(data):

    global shipment_id_increment

    shipment_id_increment += 1
    data["Shipment_id"] = shipment_id_increment
    
    normalized_data = check_data_is_normalized(data)

    if normalized_data != None:
        app.logger.warning(f"normalized_data content: {normalized_data}")
        app.logger.warning(f"Shipment_id value: {normalized_data["Shipment_id"]}")
        r.hset(f"shipment:{normalized_data["Shipment_id"]}", mapping= normalized_data)
        result = True
    else:
        result = False
    return result


@app.route('/api', methods=['POST'])
def api_post():

    data = request.json  # or request.form for form data
    if not data:
        return "No data provided", 400

    success = process_post_data(data)

    if success:
        return "Data created successfully", 201
    else:
        return "An error occurred", 500


# @app.route('/api', methods=['PUT'])
# def api_put():

#     return "1", 200


@app.route('/api', methods=['PUT'])
def api_put():

    app.logger.warning(f"json: {request.json}")


    updated_data = request.json
    if not updated_data:
        return "No data provided", 400

    if not "Shipment_id" in updated_data:
        return "Shipment ID is required", 400

    shipment_id = updated_data["Shipment_id"]
    if not shipment_id:
        return "There is no value for Shipment_id", 400


    # Check if the shipment exists
    redis_key = f'shipment:{shipment_id}'
    if not r.exists(redis_key):
        return "Shipment not found", 404

    # Update the data
    success = update_shipment_data(shipment_id, updated_data)

    if success:
        return "Data updated successfully", 200
    else:
        return "An error occurred", 500

def update_shipment_data(shipment_id, updated_data):
    redis_key = f'shipment:{shipment_id}'
    try:
        for key, value in updated_data.items():
            if key in valid_keys:
                r.hset(redis_key, key, value)
        return True
    except Exception as e:
        app.logger.error(f"Error updating shipment: {e}")
        return False



# @app.route("/api/shipments")
# def api():
    
#     data = [
#         [5263, '30.20 kg', '8.64 m³', 'Emitter Company 14', 'Recipient Company 115', '5651 Main St, City 200, State 1, USA', '179 Main St, City 154, State 6, USA', '2023-11-03', '2023-12-15', '3171 km', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'In Transit'],
#         [7806, '30.30 kg', '1.90 m³', 'Emitter Company 26', 'Recipient Company 182', '2356 Main St, City 120, State 12, USA', '6896 Main St, City 325, State 29, USA', '2023-01-06', '2023-01-19', '2143 km', 'Yes', 'Yes', 'Yes', 'Yes', 'No', 'No', 'Delivered'],
#         [5601, '48.14 kg', '5.61 m³', 'Emitter Company 30', 'Recipient Company 161', '7159 Main St, City 35, State 34, USA', '750 Main St, City 281, State 48, USA', '2023-12-06', '2023-12-24', '952 km', 'Yes', 'Yes', 'No', 'No', 'No', 'No', 'Cancelled'],
#         [5580, '42.99 kg', '1.92 m³', 'Emitter Company 27', 'Recipient Company 143', '7893 Main St, City 264, State 41, USA', '5528 Main St, City 123, State 24, USA', '2023-06-21', '2023-06-23', '4806 km', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Pending'],
#         [2720, '13.94 kg', '4.50 m³', 'Emitter Company 11', 'Recipient Company 109', '7398 Main St, City 157, State 21, USA', '7623 Main St, City 356, State 17, USA', '2023-06-09', '2023-07-25', '4685 km', 'Yes', 'Yes', 'Yes', 'Yes', 'No', 'No', 'In Transit'],
#         [5365, '18.42 kg', '2.82 m³', 'Emitter Company 57', 'Recipient Company 183', '627 Main St, City 312, State 34, USA', '1301 Main St, City 330, State 2, USA', '2023-06-27', '2023-07-16', '1718 km', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Cancelled'],
#         [4409, '47.24 kg', '1.20 m³', 'Emitter Company 96', 'Recipient Company 111', '8496 Main St, City 49, State 47, USA', '1084 Main St, City 341, State 8, USA', '2023-02-26', '2023-04-09', '2465 km', 'No', 'No', 'Yes', 'No', 'Yes', 'No', 'Pending'],
#         [1068, '33.20 kg', '3.74 m³', 'Emitter Company 91', 'Recipient Company 189', '3718 Main St, City 121, State 10, USA', '5570 Main St, City 101, State 28, USA', '2023-08-17', '2023-09-20', '870 km', 'No', 'Yes', 'No', 'Yes', 'Yes', 'No', 'In Transit'],
#         [4301, '11.96 kg', '1.07 m³', 'Emitter Company 27', 'Recipient Company 105', '163 Main St, City 331, State 45, USA', '7196 Main St, City 269, State 3, USA', '2023-02-02', '2023-03-29', '1018 km', 'No', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Pending'],
#         [2798, '43.77 kg', '6.63 m³', 'Emitter Company 5', 'Recipient Company 191', '5732 Main St, City 177, State 21, USA', '9630 Main St, City 489, State 30, USA', '2023-10-15', '2023-11-15', '4098 km', 'No', 'No', 'No', 'Yes', 'No', 'Yes', 'Delivered']
#     ]

#     return jsonify(data)



## ------------------------------------------------------------------
## WEBAPP
@app.route("/")
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)