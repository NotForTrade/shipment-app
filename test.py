import pint
from pint import UnitRegistry

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
        return input_str



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
        try:
           out[k] = auto_convert_units(v)

        except pint.errors.UndefinedUnitError:
            print("Error with pint", k, v)
        except AttributeError:
            print("AttributeError", k, v)

    return out


dic_in = {'Package_ID': 0, 'Package_Weight': '11 lb', 'Package_Volume': '2 m3', 'Emitter': 'Emitter N#841', 'Reciever': 'Reciever N#7242', 'Emitter_Address': '9473 Street of someplace', 'Reciever_Address': '3443 Street of someplace', 'Expedition_Date': '2014-2-11', 'Estimated_Arrival_Date': '2027-1-9', 'Shipment_distance': '2745 mi', 'Perishable': True, 'Valuable': True, 'Strong': False, 'GrndTrsp': False, 'Boat': False, 'Plane': True, 'Shipment_Status': 'completed', 'Color': 'red', 'Package': 'steel'}


print(normalize_brontausorus(dic_in))






