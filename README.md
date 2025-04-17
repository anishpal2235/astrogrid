# astrogrid

# 🚀 Satellite Tracker with CuPy Acceleration

This project calculates satellite positions from TLE data, converts them to geographic coordinates (latitude, longitude, altitude), and filters them based on a user-defined geographic rectangle — all using **CuPy** for GPU acceleration.

## 📦 Features

- Efficiently reads Two-Line Element (TLE) data
- Uses the SGP4 algorithm to calculate satellite positions
- Accelerated computation with CuPy (GPU)
- Converts ECEF coordinates to geographic LLA (Lat, Lon, Alt)
- Filters satellite positions based on a user-defined rectangle
- Interactive CLI input for date and location bounds

## 🧠 Tech Stack

- Python 3
- [CuPy](https://cupy.dev/) — GPU-accelerated NumPy
- [NumPy](https://numpy.org/)
- [PyProj](https://pyproj4.github.io/pyproj/)
- [SGP4](https://pypi.org/project/sgp4/) — Satellite propagation using TLEs

## 🛠️ Requirements

Install the dependencies:

```bash
pip install cupy numpy pyproj sgp4
