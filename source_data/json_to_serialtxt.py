import json
import pickle


# Load the JSON data
with open('batch0.pickle', 'rb') as logfile:
    data_batch = pickle.load(logfile)

def filter_json(json_data):
    electrics = {}
    electrics_to_keep = ['airflowspeed', 'parkingbrake', 'oil', 'engineRunning',
                     'steering', 'abs', 'gear', 'clutch_input', 'throttle_input',
                     'brake_input', 'rpm', 'reverse', 'odometer', 'wheelspeed', 'esc_active',
                     'oil_temperature', 'water_temperature']
    for entry, value in json_data['electrics'].items():
        for save_entry in electrics_to_keep:
            if entry == save_entry:
                electrics[save_entry] = value

    for tyre, value in json_data['electrics']['wheelThermals'].items():
        electrics[tyre + '_CoreTemperature'] = value['brakeCoreTemperature']
        electrics[tyre + '_SurfaceTemperature'] = value['brakeSurfaceTemperature']
    return electrics

def append_entry(json):
    string = ''
    for key, value in json.items():
        string = string + str(value) + ','
    return string

# Create a new file txt to write the data (each line every 50ms)
with open('to_serial.txt', 'w') as f:
    for key, value in data_batch.items():
        value = filter_json(value)
        f.write(append_entry(value) + '\n')