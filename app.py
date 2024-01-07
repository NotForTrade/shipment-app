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

ns_api = api.namespace('api', description='Operations for API')


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
#                                                  MODELS FOR SWAGGER DOCUMENTATION                                                   #
#######################################################################################################################################

shipping_event_model = api.model('ShippingEvent', {
    'shipment_id': fields.String(required=True, description='''With N being an integer, the shipment_id is in the following format:\n
    shipment:N\n''', example='shipment:1'),
    'event': fields.String(required=True, description='''Event occuring during the delivery of the shipment.\nThe valid events are:\n
    DEPOSIT
    IN_TRANSIT
    PARCEL_CENTER
    SUBMITTED_TO_CUSTOMS
    RECIEVED_BY_CUSTOMS
    FINAL_DELIVERY
    DELIVER
    BROKEN
    LOST''', example='DEPOSIT'),
    'shipping_partner_id': fields.String(required=True, description='''An identifier from the shipment partner that pushed the update of the shipment.\nExamples:\n
    UPS
    Customs of France frontier
    Laposte
    etc.''', example='UPS')})

new_shipment_model = api.model('NewShipment', {
    "sender_name": fields.String(required=True, description='The name of the sender.', example='Martin Dupont'),
    "sender_address": fields.String(required=True, description='The address of the sender.', example='42 rue des Lilas, 75014 Paris, France'),
    "recipient_name": fields.String(required=True, description='The name of the recipient.', example='Quentin Dupieux'),
    "recipient_address": fields.String(required=True, description='The address of the sender.', example='58 Rue de la Clef, 59800 Lille, France'),
    "desired_delivery_date": fields.String(required=False, description='Used to check if perishable shipments are late.', example='2024-09-25'),
    "weight": fields.String(required=True, description='The weight of the package in kg.', example='100'),
    "volume": fields.String(required=True, description='The volume of the package in cubic meter.', example='1'),
    "perishable": fields.String(required=True, description='Says if the shipment is perishable or not.', example='True'),
    "high_value": fields.String(required=True, description='The price of the shipment in $.', example='500'),
    "fragile": fields.String(required=True, description='Says if the shipment is fragile.', example='True'),
    "partner": fields.String(required=True, description='The partner\'s id used to collect shipments by partners.', example='RAPTOR')})


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
        '''Look for one shipment based on <shipment_id>'''
        try:
            shipment_data = r.get(shipment_id)
            if shipment_data is None:
                return jsonify({"error": "Shipment not found"}), 404
        except Exception as e:
            return f"Internal error: {e}", 500    
        row = json.loads(shipment_data)
        return jsonify(row), 200

@ns_api.route('/shipment-event')
class ShippingEvent(Resource):
    @api.expect(shipping_event_model)
    def post(self):
        '''Post a new shipment event'''
        payload = request.json
        shipment_id = payload["shipment_id"]
        try:
            raw_data = r.get(shipment_id)
            data = json.loads(raw_data)
            event = payload["event"]
            match event:
                case "DEPOSIT":
                    shipment_status = "AT LOCAL PARCEL"
                case "IN_TRANSIT":
                    shipment_status = "IN TRANSIT"
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
            if shipment_status == "IN TRANSIT":
                data["expedition_date"] = str(datetime.datetime.now())
            new_event = {
                "datetime": str(datetime.datetime.now()),
                "shipment_status": shipment_status,
                "shipping_partner_id": payload["shipping_partner_id"]
            }
            data["shipment_status"] = shipment_status
            data["event_history"].append(new_event)
            app.logger.warning(f"New data: {data}")
            r.set(shipment_id, json.dumps(data))
            return f"Shipment event <{new_event}> posted! The shipment status has been updated to <{shipment_status}>", 200
        except Exception as e:
            return f"Internal error: {e}", 500

@ns_api.route('/new-shipment')
class NewShipment(Resource):
    @api.expect(new_shipment_model)
    def post(self):
        '''Post a new shipment'''
        data_in = request.json
        global SHIPMENT_COUNTER
        try:
            out = {
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
            r.incr(SHIPMENT_COUNTER)
            shipment_id = f"shipment:{r.get(SHIPMENT_COUNTER)}"
            r.set(shipment_id, value=json.dumps(out))
            return f"Data created successfully: \n{out}", 201
        except Exception as e:
            return e, 500


#######################################################################################################################################
#                                                                INDEX                                                                #
#######################################################################################################################################

@app.route("/index")
def index():
    return render_template('index.html')


#######################################################################################################################################
#                                                                MAIN                                                                 #
#######################################################################################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)