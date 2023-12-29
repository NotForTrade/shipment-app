from flask import Flask, jsonify, render_template, request, abort
import random
import json
import redis
import os

app = Flask(__name__)


redis_host=os.environ.get("REDIS_HOST")
redis_port=int(os.environ.get("REDIS_PORT"))

if redis_host != None and redis_port != None:
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


## ------------------------------------------------------------------
## External connector

@app.route("/brontosaurus", methods=["POST"])
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

@app.route("/api/shipments")
def api():
    
    data = [
        [5263, '30.20 kg', '8.64 m³', 'Emitter Company 14', 'Recipient Company 115', '5651 Main St, City 200, State 1, USA', '179 Main St, City 154, State 6, USA', '2023-11-03', '2023-12-15', '3171 km', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'In Transit'],
        [7806, '30.30 kg', '1.90 m³', 'Emitter Company 26', 'Recipient Company 182', '2356 Main St, City 120, State 12, USA', '6896 Main St, City 325, State 29, USA', '2023-01-06', '2023-01-19', '2143 km', 'Yes', 'Yes', 'Yes', 'Yes', 'No', 'No', 'Delivered'],
        [5601, '48.14 kg', '5.61 m³', 'Emitter Company 30', 'Recipient Company 161', '7159 Main St, City 35, State 34, USA', '750 Main St, City 281, State 48, USA', '2023-12-06', '2023-12-24', '952 km', 'Yes', 'Yes', 'No', 'No', 'No', 'No', 'Cancelled'],
        [5580, '42.99 kg', '1.92 m³', 'Emitter Company 27', 'Recipient Company 143', '7893 Main St, City 264, State 41, USA', '5528 Main St, City 123, State 24, USA', '2023-06-21', '2023-06-23', '4806 km', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Pending'],
        [2720, '13.94 kg', '4.50 m³', 'Emitter Company 11', 'Recipient Company 109', '7398 Main St, City 157, State 21, USA', '7623 Main St, City 356, State 17, USA', '2023-06-09', '2023-07-25', '4685 km', 'Yes', 'Yes', 'Yes', 'Yes', 'No', 'No', 'In Transit'],
        [5365, '18.42 kg', '2.82 m³', 'Emitter Company 57', 'Recipient Company 183', '627 Main St, City 312, State 34, USA', '1301 Main St, City 330, State 2, USA', '2023-06-27', '2023-07-16', '1718 km', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Cancelled'],
        [4409, '47.24 kg', '1.20 m³', 'Emitter Company 96', 'Recipient Company 111', '8496 Main St, City 49, State 47, USA', '1084 Main St, City 341, State 8, USA', '2023-02-26', '2023-04-09', '2465 km', 'No', 'No', 'Yes', 'No', 'Yes', 'No', 'Pending'],
        [1068, '33.20 kg', '3.74 m³', 'Emitter Company 91', 'Recipient Company 189', '3718 Main St, City 121, State 10, USA', '5570 Main St, City 101, State 28, USA', '2023-08-17', '2023-09-20', '870 km', 'No', 'Yes', 'No', 'Yes', 'Yes', 'No', 'In Transit'],
        [4301, '11.96 kg', '1.07 m³', 'Emitter Company 27', 'Recipient Company 105', '163 Main St, City 331, State 45, USA', '7196 Main St, City 269, State 3, USA', '2023-02-02', '2023-03-29', '1018 km', 'No', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Pending'],
        [2798, '43.77 kg', '6.63 m³', 'Emitter Company 5', 'Recipient Company 191', '5732 Main St, City 177, State 21, USA', '9630 Main St, City 489, State 30, USA', '2023-10-15', '2023-11-15', '4098 km', 'No', 'No', 'No', 'Yes', 'No', 'Yes', 'Delivered']
    ]

    return jsonify(data)


## ------------------------------------------------------------------
## WEBAPP
@app.route("/")
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)