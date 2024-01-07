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

from flask_restx import Api, Resource, fields



#######################################################################################################################################
#                                                    FLASK & SWAGGER INITIALIZATION                                                   #
#######################################################################################################################################

app = Flask(__name__)
api = Api(app=app, version='1.0', title="Shipment-app API", description='The API of Shipment-app, demonstrating the management of shipment informations in a scalable way.')

shipment_model = api.model('Shipment', {
    'shipment_id': fields.String(required=True, description='The shipment identifier'),
    # Add other fields as needed
})

ns_api = api.namespace('api', description='API namespace')



#######################################################################################################################################
#                                                         REDIS INITIALIZATION                                                        #
#######################################################################################################################################

# The Hostname and port of the Redis service are written in the environment variables
redis_host=os.environ.get("REDIS_HOST")
redis_port=os.environ.get("REDIS_PORT")

# Handle if the environment variables are missing
if redis_host != None and redis_port != None:
    r = redis.Redis(host=redis_host, port=int(redis_port), decode_responses=True)
else:
    app.logger.warning("Environment variables are not set!")

# Redis counter
SHIPMENT_COUNTER = "SHIPMENT_COUNTER"


#######################################################################################################################################
#                                                         EXTERNAL CONNECTORS                                                         #
#######################################################################################################################################

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



#######################################################################################################################################
#                                                     API - Redis DataBase routes                                                     #
#######################################################################################################################################

@ns_api.route('/shipments/')
class ShipmentList(Resource):
    @api.doc('list_shipments')
    def get(self):
        '''List all shipments'''
        args = request.args
        out = list()
        try:
            for key in r.scan_iter("shipment:*"):
                row = json.loads(r.get(key))
                row["shipment_id"] = key
                if "partner" in args:
                    if row["partner"] == args["partner"]:
                        out.append(row)        
                else:
                    out.append(row)
        except Exception as e:
            return f"Internal error: {e}", 500
        return out, 200


@ns_api.route('/shipment/<shipment_id>')
class Shipment(Resource):
    @api.doc('get_shipments')
    def get(self, shipment_id):
        '''List all shipments'''
        try:
            shipment_data = r.get(shipment_id)
        except Exception as e:
            return f"Internal error: {e}", 500
        if shipment_data is None:
            return jsonify({"error": "Shipment not found"}), 404
        row = json.loads(shipment_data)
        return jsonify(row), 200




# @app.route('/api/shipment/<shipment_id>', methods=['GET'])
# def api_get_shipment(shipment_id):

#     try:
#         # Retrieve the shipment data from Redis
#         shipment_data = r.get(shipment_id)
#     except Exception as e:
#         return f"Internal error: {e}", 500

#     if shipment_data is None:
#         return jsonify({"error": "Shipment not found"}), 404

#     # Deserialize the JSON string into a Python dictionary
#     row = json.loads(shipment_data)

#     # Return the shipment data
#     return jsonify(row), 200



@app.route('/api/shipping-event', methods=['POST'])
def api_post_shipping_event():

    payload = request.json
    
    shipment_id = payload["shipment_id"]


    try:
        raw_data = r.get(shipment_id)
        
        data = json.loads(raw_data)
    except Exception as e:
        return f"Internal error: {e}", 500

    event = payload["event"]
    match event:
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

        return f"Internal error: {e}", 500


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
        "partner": data_in["partner"],
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




#######################################################################################################################################
#                                                                INDEX                                                                #
#######################################################################################################################################

@app.route("/")
def index():
    return render_template('index.html')



#######################################################################################################################################
#                                                                MAIN                                                                 #
#######################################################################################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)