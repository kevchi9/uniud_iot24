import math

# Do we need to keep this?

l = 46.08122267796358
l_long = 111132.92 - 559.82 * math.cos (2*l) + 1.175 * math.cos(4*l) - 0.0023 * math.cos(6*l)
l_lat = 111412.84 * math.cos(l) - 93.5 * math.cos(3*l) + 0.118 * math.cos(5*l)

def metriGPS (x, y):
    lat=y/l_lat + 46.08122267796358
    long=x/l_long + 13.212077351133791
    return  lat, long


print(metriGPS(0,70))