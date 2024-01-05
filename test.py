import requests
import json

def test_post_api(url, data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")


def post_test():
    # URL of your API
    api_url = "http://127.0.0.1:80/api"

    # Sample data payload
    # Modify this dictionary with the data structure expected by your API
    sample_data = {
        "Weight": 30,
        "Volume": 31.44,
        "Emitter": "Emitter_36",
        "Recipient": "Recipient_94",
        "Emitter_Address": "123 Emitter St, City 24",
        "Recipient_Address": "456 Recipient Ave, City 23",
        "Expedition_Date": "2024-01-04",
        "Estimated_Arrival_Date": "2024-01-10",
        "Shipment_distance": 537.57,
        "Perishable": True,
        "High_Value": True,
        "Fragile": True,
        "Includes_Air_Transportation": True,
        "Includes_Water_Transportation": False,
        "Includes_Ground_Transportation": True,
        "Shipment_Status": "Lost"
    }


    # Call the function to test POST request
    test_post_api(api_url, sample_data)



def test_put_api(url, data):
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, data=json.dumps(data), headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")



if __name__ == "__main__":

    


    post_test()



    # # Sample data payload
    # # Modify this dictionary with the data structure expected by your API
    # sample_data = {
    #     "Shipment_id": "1",
    #     "Weight": 869.43,
    #     "Volume": 31.44,
    #     "Emitter": "Emitter_36",
    #     "Recipient": "Recipient_94",
    #     "Emitter_Address": "123 Emitter St, City 24",
    #     "Recipient_Address": "456 Recipient Ave, City 23",
    #     "Expedition_Date": "2024-01-04",
    #     "Estimated_Arrival_Date": "2024-01-10",
    #     "Shipment_distance": 537.57,
    #     "Perishable": True,
    #     "High_Value": True,
    #     "Fragile": True,
    #     "Includes_Air_Transportation": True,
    #     "Includes_Water_Transportation": False,
    #     "Includes_Ground_Transportation": True,
    #     "Shipment_Status": "In Transit"
    # }


    # # Call the function to test POST request
    # test_put_api(api_url, sample_data)