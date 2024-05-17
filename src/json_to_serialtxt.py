import pickle

# I would use CONSTANTS for this purpose
ELECTRICS = ['airflowspeed', 'parkingbrake', 'oil', 'engineRunning',
                     'steering', 'abs', 'gear', 'clutch_input', 'throttle_input',
                     'brake_input', 'rpm', 'reverse', 'odometer', 'wheelspeed', 'esc_active',
                     'oil_temperature', 'water_temperature']

# We could do this dynamic to reuse it for other kind of data
def filter_json(json_data, fields_to_keep):
    electrics = {}
    
    for entry, value in json_data['electrics'].items():
        if entry in fields_to_keep:
            electrics[entry] = value

    for tyre, value in json_data['electrics']['wheelThermals'].items():
        electrics[tyre + '_CoreTemperature'] = value['brakeCoreTemperature']
        electrics[tyre + '_SurfaceTemperature'] = value['brakeSurfaceTemperature']

    return electrics

def append_entry(json):
    string = ''
    for _, value in json.items():
        string = string + str(value) + ','
    return string

# Load the JSON data
with open('../source_data/batch0.pickle', 'rb') as logfile:
    data_batch = pickle.load(logfile)

# Create a new file txt to write the data (each line every 50ms)
with open('../source_data/to_serial.txt', 'w') as f:
    for _, value in data_batch.items():
        value = filter_json(value, ELECTRICS)
        f.write(append_entry(value) + '\n')