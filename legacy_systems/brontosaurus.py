import requests
import random
import time
import json

url = 'http://127.0.0.1:80/connector/brontosaurus'

# payload values and unit ranges
distance_units = ["km", "m", "mi"]
colors = ["blue", "red", "yellow", "pink", "brown", "black", "white"]
package_materials = ["cardboard", "steel", "wood", "plastic"]
status= ["IN TRANSIT", "AT PARCEL CENTER", "UNDERGOING INSPECTION",
         "CLEARED BY CUSTOMS", "COMPLETED", "FAILED"]

def generate_payload(shipment_number):
    
    high_value = random.choice([True, False])
    if high_value:
        value = str(random.randint(500, 1000000))
    else:
        value = ""

    out = {
        "Shipment_ID": f"P0{shipment_number}",
        "Emitter": f"Brontosaurus_emitter_{random.randint(0, 9999)}",
        "Sender_Address": "---",
        "Reciever_Name": f"Brontosaurus_reciever_{random.randint(0, 9999)}",
        "Recipient_Address": "---",
        'Expedition_Date': f"{random.randint(2012, 2023)}-{random.randint(0,12)}-{random.randint(0,31)}",
        "Wanted_Delivery_Date": f"{random.randint(2024, 2035)}-{random.randint(0,12)}-{random.randint(0,31)}",
        "Package_Weight": f"{random.randint(1,100)}",
        "Package_Volume": f"{random.randint(1, 10)}",
        "Perishable": str(random.choice([True, False])),
        "Valuable": value,
        "Strong": str(random.choice([True, False])),
        "Shipment_distance": f"{random.randint(0, 9000)} {random.choice(distance_units)}",
        "Shipment_Status": random.choice(status)
        }
    if random.choice([True, False]):
        out.update([("Color", random.choice(colors))])
    if random.choice([True, False]):
        out.update([("Package", random.choice(package_materials))])
    return out





shipment_number = 0

while True:
    
    payload = generate_payload(shipment_number)
    print(payload)


    try:
        response = requests.post(url, json=payload)
        print(f"Sent request. Status code:{response.status_code}")



    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    sleep_time = random.randint(1, 10)  # Random interval between 1 and 10 seconds
    print(f"Waiting for {sleep_time} seconds...")
    time.sleep(sleep_time)


    shipment_number+=1