import pickle
import math
import os
import json

# I would use CONSTANTS for this purpose
ELECTRICS = ["engineRunning",
    "steering",
    "abs",
    "gear",
    "clutch_input",
    "throttle_input",
    "brake_input",
    "rpm",
    "wheelspeed",
    "oil_temperature",
    "water_temperature"]

IMU = []

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

def filter_json_imu(json_data):
    imu = {}
    
    for entry, value in json_data['imu'].items():
        imu[entry] = value

    return imu

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

if __name__ == '__main__':

    path = 'source_data/pickles/'
    with open(path + 'telemetry.pickle', 'rb') as logfile:
        data_batch = pickle.load(logfile)

    with open('source_data/reference.json', 'w') as f:
        json.dump(next(iter(data_batch.values())), f, indent = 4)

    #Electrics
    json_list = []
    for _, value in data_batch.items():
        json_list.append(filter_json_electrics(value, ELECTRICS))

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

    #IMU
    json_list = []
    for _, value in data_batch.items():
        json_list.append(filter_json_imu(value))

    with open('source_data/imu_to_serial.txt', 'w') as f:
        for entry in json_list:
            f.write(str(entry) + '\n')