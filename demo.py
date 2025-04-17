import datetime
import pyproj
import cupy as cp
from sgp4.api import Satrec, jday
import numpy as np

# 1. Efficiently read TLE and create satellite objects using synchronous I/O
def read_tle(file_path):
    satellites = []
    with open(file_path, 'r') as file:
        while True:
            line1 = file.readline()
            line2 = file.readline()
            if not line2:
                break
            sat = Satrec.twoline2rv(line1.strip(), line2.strip())
            satellites.append(sat)
    return satellites

# Load the TLE data
satellites = read_tle('30sats.txt')

# 2. Calculate satellite positions using CuPy for acceleration
def calculate_positions(satellites, start_date, minutes_interval=1):
    jd_start, fr = jday(start_date.year, start_date.month, start_date.day, 0, 0, 0)
    jd_times = jd_start + np.arange(0, 1440, minutes_interval) / 1440.0
    time_deltas_seconds = np.arange(0, 1440, minutes_interval) * 60 * minutes_interval

    results = []
    for satellite in satellites:
        jd_times_gpu = cp.asarray(jd_times)
        time_deltas_seconds_gpu = cp.asarray(time_deltas_seconds)
        
        # Convert fr to a NumPy array to ensure compatibility with sgp4_array
        fr_array = np.array([fr] * len(jd_times))  
        
        e, r, v = satellite.sgp4_array(jd_times, fr_array)  # Pass the NumPy array version of fr
        
        e = cp.asarray(e)
        r = cp.asarray(r)
        v = cp.asarray(v)
        valid_indices = cp.where(e == 0)[0]  # Get the first element of the tuple
        
        # Handle datetime operations using NumPy
        start_date_np = np.datetime64(start_date)
        time_deltas_seconds_np = np.array([np.timedelta64(int(delta), 's') for delta in time_deltas_seconds[valid_indices.get()]], dtype='timedelta64[s]')
        times_np = start_date_np + time_deltas_seconds_np
        
        # Convert results back to NumPy arrays
        times = times_np.astype('datetime64[s]')
        positions = np.column_stack((r[valid_indices].get(), v[valid_indices].get()))
        results.append((times, positions))
    
    times_combined = np.concatenate([res[0] for res in results])
    positions_combined = np.concatenate([res[1] for res in results])
    
    return times_combined, positions_combined

# 3. Get start date from user
def get_start_date():
    date_str = input("Enter the start date in YYYY-MM-DD format: ")
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
        return get_start_date()

# Get start date and calculate positions
start_date = get_start_date()
times, positions = calculate_positions(satellites, start_date)
print(f"Calculated positions for {len(times)} satellite data points.")

# 4. Optimize ECEF to LLA conversion with CuPy
def ecef2lla(positions):
    ecef = pyproj.CRS.from_proj4("+proj=geocent +ellps=WGS84 +datum=WGS84")
    lla = pyproj.CRS.from_proj4("+proj=latlong +ellps=WGS84 +datum=WGS84")
    transformer = pyproj.Transformer.from_crs(ecef, lla, always_xy=True)

    pos_x = cp.array(positions[:, 0])
    pos_y = cp.array(positions[:, 1])
    pos_z = cp.array(positions[:, 2])

    lon, lat, alt = transformer.transform(pos_x.get(), pos_y.get(), pos_z.get(), radians=False)

    return lon, lat, alt

# Convert positions from ECEF to LLA
longitudes, latitudes, altitudes = ecef2lla(positions)
result_A = list(zip(longitudes, latitudes, altitudes))
print(f"Converted {len(result_A)} positions to LLA coordinates.")

# 5. Get user-defined rectangle
def get_user_rectangle():
    print("Please enter the latitude and longitude for the four corners of the rectangle:")
    coords = []
    for i in range(4):
        lat = float(input(f"Enter latitude for corner {i + 1}: "))
        lon = float(input(f"Enter longitude for corner {i + 1}: "))
        coords.append((lat, lon))
    return coords

# Get rectangle bounds
def get_rectangle_bounds(coords):
    lats = [coord[0] for coord in coords]
    lons = [coord[1] for coord in coords]

    return {
        'min_lat': min(lats),
        'max_lat': max(lats),
        'min_lon': min(lons),
        'max_lon': max(lons)
    }

# 6. Filter positions by user-defined rectangle
def filter_positions_by_rectangle(longs, lats, bounds):
    min_lat, max_lat = bounds['min_lat'], bounds['max_lat']
    min_lon, max_lon = bounds['min_lon'], bounds['max_lon']

    # Use CuPy for filtering operations
    longs_gpu = cp.asarray(longs)
    lats_gpu = cp.asarray(lats)
    mask = (min_lat <= lats_gpu) & (lats_gpu <= max_lat) & (min_lon <= longs_gpu) & (longs_gpu <= max_lon)
    filtered_positions = cp.column_stack((longs_gpu[mask], lats_gpu[mask]))

    return filtered_positions.get()

# Get the rectangle coordinates from the user
rectangle_coords = get_user_rectangle()
bounds = get_rectangle_bounds(rectangle_coords)

# Filter positions within the rectangle
filtered_positions = filter_positions_by_rectangle(longitudes, latitudes, bounds)

# Output the filtered positions
print("Filtered positions within the rectangle:")
for pos in filtered_positions:
    print(f"Longitude: {pos[0]}, Latitude: {pos[1]}")