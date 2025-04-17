from sgp4.api import Satrec, jday
import numpy as np
import datetime
#1 Calculate the position and velocity
def read_tle(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        satellites = []
        for i in range(0, len(lines), 3):
            sat = Satrec.twoline2rv(lines[i+1].strip(), lines[i+2].strip())
            satellites.append(sat)
        return satellites

satellites = read_tle('30sats.txt')
def calculate_positions(satellites, start_date, minutes_interval=1):
    results = []
    jd_start, fr = jday(start_date.year, start_date.month, start_date.day, 0, 0, 0)
    
    for satellite in satellites:
        for minute in range(0, 1440, minutes_interval): 
            jd = jd_start + minute / 1440.0
            e, r, v = satellite.sgp4(jd, fr)
            if e == 0: 
                time = start_date + datetime.timedelta(minutes=minute)
                results.append((time, r[0], r[1], r[2], v[0], v[1], v[2]))
    return results

import datetime

def get_start_date():
    date_str = input("Enter the start date in YYYY-MM-DD format: ")
    try:
        start_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return start_date
    except ValueError:
        print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
        return get_start_date()
start_date = get_start_date()
positions = calculate_positions(satellites, start_date)
#print(positions)

import pyproj
def ecef2lla(i, pos_x, pos_y, pos_z):
    ecef = pyproj.CRS.from_proj4("+proj=geocent +ellps=WGS84 +datum=WGS84")
    lla = pyproj.CRS.from_proj4("+proj=latlong +ellps=WGS84 +datum=WGS84")
    transformer = pyproj.Transformer.from_crs(ecef, lla, always_xy=True)
    
    lona, lata, alta = transformer.transform(pos_x[i], pos_y[i], pos_z[i], radians=False)
    return lona, lata, alta

pos_x = [pos[1] for pos in positions]
pos_y = [pos[2] for pos in positions]
pos_z = [pos[3] for pos in positions]

longitudes, latitudes, altitudes = [], [], []
for i in range(len(pos_x)):
    lon, lat, alt = ecef2lla(i, pos_x, pos_y, pos_z)
    longitudes.append(lon)
    latitudes.append(lat)
    altitudes.append(alt)

result_A = list(zip(longitudes, latitudes, altitudes))
#print(result_A)

def get_user_rectangle():
    print("Please enter the latitude and longitude for the four corners of the rectangle:")
    coords = []
    for i in range(4):
        lat = float(input(f"Enter latitude for corner {i + 1}: "))
        lon = float(input(f"Enter longitude for corner {i + 1}: "))
        coords.append((69.7))
    
    return coords

rectangle_coords = get_user_rectangle()

def get_rectangle_bounds(coords):
    lats = [coord[0] for coord in coords]
    lons = [coord[1] for coord in coords]
    
    min_lat = min(lats)
    max_lat = max(lats)
    min_lon = min(lons)
    max_lon = max(lons)
    
    return {'min_lat': min_lat, 'max_lat': max_lat, 'min_lon': min_lon, 'max_lon': max_lon}

bounds = get_rectangle_bounds(rectangle_coords)

def filter_positions_by_rectangle(longs, lats, bounds):
    filtered_positions = []
    for i in range(len(longs)):
        if bounds['min_lat'] <= lats[i] <= bounds['max_lat'] and bounds['min_lon'] <= longs[i] <= bounds['max_lon']:
            filtered_positions.append((longs[i], lats[i]))
    return filtered_positions
filtered_positions = filter_positions_by_rectangle(longitudes, latitudes, bounds)

print("Filtered positions within the rectangle:")
for pos in filtered_positions:
    print(f"Longitude: {pos[0]}, Latitude: {pos[1]}")

