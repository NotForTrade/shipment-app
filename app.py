from flask import Flask, jsonify, render_template, request, abort
import json
import os
import redis
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
ns_connector = api.namespace('connector', description='Connectors to support monolithic applications')

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
#                                                  MODELS FOR SWAGGER DOCUMENTATION                                                   #
#######################################################################################################################################

shipping_event_model = api.model('ShipmentEvent', {
    'shipment_id': fields.String(required=True, description='''With N being an integer, the shipment_id is in the following format:\n
    shipment:N\n''', example='shipment:1'),
    'event': fields.String(required=True, description='''Event occuring during the delivery of the shipment.\nThe valid events are:\n
    PICKED_UP
    PARCEL_CENTER
    CUSTOMS
    DELIVERED
    DAMAGED
    LOST''', example='PICKED_UP'),
    'shipping_partner_id': fields.String(required=True, description='''An identifier from the shipment partner that pushed the update of the shipment.''', example='TECHNOLOGIX SOLUTION DRIVER')})

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
    @api.doc('get_shipment')
    def get(self, shipment_id):
        '''Look for one shipment based on <shipment_id>'''
        try:
            shipment_data = r.get(f"shipment:{shipment_id}")
            if shipment_data == None:
                return jsonify({"error": "Shipment not found"}), 404
            row = json.loads(shipment_data)
            return row, 200
        except Exception as e:
            return f"Internal error: {e}", 500

@app.route("/api/internal/shipment-event", methods=["POST"])
def shipment_event_internal():
        payload = request.json
        shipment_id = payload["shipment_id"]
        try:
            raw_data = r.get(f"shipment:{shipment_id}")
            data = json.loads(raw_data)
            event = payload["event"]
            if event == "PICKED_UP":
                shipment_status = "IN TRANSIT"
            elif event == "PARCEL_CENTER":
                shipment_status = "AT PARCEL CENTER"
            elif event == "CUSTOMS":
                shipment_status = "UNDERGOING INSPECTION"
            elif event == "DELIVERED":
                shipment_status = "COMPLETED"
            elif event == "DAMAGED":
                shipment_status = "FAILED - DAMAGED"
            elif event == "LOST":
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
            r.set(f"shipment:{shipment_id}", json.dumps(data))
            return f"Shipment event <{new_event}> posted! The shipment status has been updated to <{shipment_status}>", 201
        except Exception as e:
            return f"Internal error: {e}", 500

@ns_api.route('/shipment-event')
class ShipmentEvent(Resource):
    @api.expect(shipping_event_model)
    def post(self):
        '''Post a new shipment event'''
        try:
            payload = request.json
            payload_str = json.dumps(request.json)
            queue = "shipment_event_queue"
            app.logger.warning(f"The following data is going to be pushed to the redis queue: queue: {queue} payload: {payload_str}")
            r.rpush(queue, payload_str)
            return f"Shipment event posted! The shipment status has been updated", 201
        except redis.RequestException as e:
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
                "sender_name": data_in["sender_name"],
                "sender_address": data_in["sender_address"],
                "recipient_name": data_in["recipient_name"],
                "recipient_address": data_in["recipient_address"],
                "creation_time": str(datetime.datetime.fromtimestamp(time.time())),
                "expedition_date": "-",
                "desired_delivery_date": data_in["desired_delivery_date"],
                "weight": data_in["weight"],
                "volume": data_in["volume"],
                "perishable": data_in["perishable"],
                "high_value": data_in["high_value"],
                "fragile": data_in["fragile"],
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
#                                                         EXTERNAL CONNECTORS                                                         #
#######################################################################################################################################

@app.route("/connector/brontosaurus", methods=["POST"])
def brontosaurus_push_redis():
    payload = json.dumps(request.json)
    queue = "brontosaurus_queue"
    try:
        r.rpush(queue, payload)
    except redis.RequestException:
        abort(500)
    return json.dumps({"status": "OK"})


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