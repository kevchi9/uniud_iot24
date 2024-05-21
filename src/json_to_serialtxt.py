import pickle
import math
import os

# I would use CONSTANTS for this purpose
ELECTRICS = ['airflowspeed', 'parkingbrake', 'oil', 'engineRunning',
                     'steering', 'abs', 'gear', 'clutch_input', 'throttle_input',
                     'brake_input', 'rpm', 'reverse', 'odometer', 'wheelspeed', 'esc_active',
                     'oil_temperature', 'water_temperature']

# We could do this dynamic to reuse it for other kind of data
def filter_json_electrics(json_data, fields_to_keep):
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

def metriGPS (x, y):
    l = 46.08122267796358
    l_long = 111132.92 - 559.82 * math.cos (2*l) + 1.175 * math.cos(4*l) - 0.0023 * math.cos(6*l)
    l_lat = 111412.84 * math.cos(l) - 93.5 * math.cos(3*l) + 0.118 * math.cos(5*l)
    lat=y/l_lat + 46.08122267796358
    long=x/l_long + 13.212077351133791
    return  lat, long

def convert_to_nmea(lat, lon):
    # Convert latitude
    lat_deg = int(abs(lat))
    lat_min = (abs(lat) - lat_deg) * 60
    lat_dir = 'N' if lat >= 0 else 'S'
    
    # Format latitude as DDMM.MMMM
    lat_nmea = f"{lat_deg:02d}{lat_min:07.4f},{lat_dir}"
    
    # Convert longitude
    lon_deg = int(abs(lon))
    lon_min = (abs(lon) - lon_deg) * 60
    lon_dir = 'E' if lon >= 0 else 'W'
    
    # Format longitude as DDDMM.MMMM
    lon_nmea = f"{lon_deg:03d}{lon_min:07.4f},{lon_dir}"
    
    return lat_nmea, lon_nmea

# Load the JSON data
data_batch = {}
path = 'source_data/pickles/'
for filename in os.listdir(path):
    with open(path + filename, 'rb') as logfile:
        data_batch = data_batch | pickle.load(logfile)


#Electrics
json_list = []

for _, value in data_batch.items():
    json_list.append(filter_json_electrics(value, ELECTRICS))

last = json_list[0]
for entry in json_list:
    for key, value in entry.items():
        if last[key] != value:
            last[key] = value
        else:
            entry[key] = ''    

# Create a new file txt to write the data (each line every 50ms)
with open('source_data/electrics_to_serial.txt', 'w') as f:
    for entry in json_list:
        f.write(append_entry(entry) + '\n')


#GPS
json_list = []

for _, value in data_batch.items():
    json_list.append(value['state']['pos'])

with open('source_data/gps_to_serial.txt', 'w') as f:
    for entry in json_list:
        lat, long = metriGPS(entry[0], entry[1])
        f.write(str(lat) + ',' + str(long) + '\n')


'''
damage_to_keep = ['low_pressure', 'part_damage']
'''