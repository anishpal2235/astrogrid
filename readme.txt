The following Python code performs the tasks sequentially:

-Parsing TLE data: Reading the TLE data from the file.
-Propagating the Satellite Positions: Using the sgp4 library to compute the satellite's position and velocity for one day at one-minute intervals.
-Converting ECEF to Latitude, Longitude, and Altitude: Using the pyproj library.
-Filtering based on user-defined latitude/longitude bounds.
-Optimization considerations.

sat_loc.py file which is used for satellite position and velocity calculation, has been modified and the modifications are shown in demo.py file(which contains cupy library)

Required Libraries:
datetime
cupy
pyproj
sgp4
numpy