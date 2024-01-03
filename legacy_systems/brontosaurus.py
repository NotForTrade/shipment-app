import requests
import random
import time
import json

url = 'http://127.0.0.1:80/connector/brontosaurus'

# payload values and unit ranges


weight_units = ["kg", "g", "lb", "oz"]
volume_units = ["L", "m3", "gallon"]
distance_units = ["km", "m", "mi"]
status = ["pending", "completed", "aborted", "ongoing"]
colors = ["blue", "red", "yellow", "pink", "brown", "black", "white"]
package_materials = ["cardboard", "steel", "wood", "plastic"]


def generate_payload(shipment_number):
    


    out = {
        "Package_ID": shipment_number,
        "Package_Weight": f"{random.randint(1,15)} {random.choice(weight_units)}",
        "Package_Volume": f"{random.randint(1,5)} {random.choice(volume_units)}",
        "Emitter": f"Emitter N#{random.randint(0,9999)}",
        "Reciever": f"Reciever N#{random.randint(0,9999)}",
        "Emitter_Address": f"{random.randint(0, 9999)} Street of someplace",
        "Reciever_Address": f"{random.randint(0, 9999)} Street of someplace",
        "Expedition_Date": f"{random.randint(2000, 2023)}-{random.randint(0,12)}-{random.randint(0,31)}",
        "Estimated_Arrival_Date": f"{random.randint(2024, 2035)}-{random.randint(0,12)}-{random.randint(0,31)}",
        "Shipment_distance": f"{random.randint(0, 9000)} {random.choice(distance_units)}",
        "Perishable": random.choice([True, False]),
        "Valuable": random.choice([True, False]),
        "Strong": random.choice([True, False]),
        "GrndTrsp": random.choice([True, False]),
        "Boat": random.choice([True, False]),
        "Plane": random.choice([True, False]),
        "Shipment_Status": random.choice(status)
    }
    if random.choice([True, False]):
        out.update([("Color", random.choice(colors))])
    if random.choice([True, False]):
        out.update([("Package", random.choice(package_materials))])

    return out



while True:

    shipment_number = 0

    payload = generate_payload(shipment_number)
    print(payload)


    try:
        response = requests.post(url, json=payload)  # Use requests.get() for GET requests
        print(f"Sent request. Status code:{response.status_code}")



    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    sleep_time = random.randint(1, 10)  # Random interval between 1 and 10 seconds
    print(f"Waiting for {sleep_time} seconds...")
    time.sleep(sleep_time)


    shipment_number+=1