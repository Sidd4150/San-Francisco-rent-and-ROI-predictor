"""One feature contract shared by data preparation, training, and inference."""
import math
import numpy as np
import pandas as pd

BASE_FEATURES = ['beds', 'baths', 'footage', 'latitude', 'longitude']
UTILITY_FEATURES = ['waterIncluded', 'gasIncluded', 'electricityIncluded', 'refuseIncluded']
OPTIONAL_FEATURES = ['yearBuilt', 'buildingUnits'] + UTILITY_FEATURES
NUMERIC_FEATURES = BASE_FEATURES + OPTIONAL_FEATURES + [
    'buildingAge', 'logBuildingUnits', 'sqftPerBedroom', 'distanceDowntownKm', 'distanceParkKm'
]
CATEGORICAL_FEATURES = ['neighborhood']
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
LIMITS = {'beds': (0, 5), 'baths': (1, 3), 'footage': (251, 4000),
          'latitude': (37.70, 37.84), 'longitude': (-122.52, -122.35)}


def distance_km(lat, lon, dest_lat, dest_lon):
    lat, lon = np.radians(lat), np.radians(lon)
    dlat, dlon = np.radians(dest_lat) - lat, np.radians(dest_lon) - lon
    a = np.sin(dlat / 2) ** 2 + np.cos(lat) * np.cos(np.radians(dest_lat)) * np.sin(dlon / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def feature_frame(records):
    frame = pd.DataFrame(records).copy()
    for field in BASE_FEATURES + OPTIONAL_FEATURES:
        if field not in frame:
            frame[field] = np.nan
        frame[field] = pd.to_numeric(frame[field], errors='coerce')
    # Match the public source's 250-sq-ft bins rather than inventing precision.
    frame['footage'] = np.floor((frame['footage'] - 1) / 250) * 250 + 125.5
    frame['buildingAge'] = 2026 - frame['yearBuilt']
    frame['logBuildingUnits'] = np.log1p(frame['buildingUnits'])
    frame['sqftPerBedroom'] = frame['footage'] / (frame['beds'] + 1)
    frame['distanceDowntownKm'] = distance_km(frame['latitude'], frame['longitude'], 37.7945, -122.3999)
    frame['distanceParkKm'] = distance_km(frame['latitude'], frame['longitude'], 37.7694, -122.4862)
    if 'neighborhood' not in frame:
        frame['neighborhood'] = 'Unknown'
    frame['neighborhood'] = frame['neighborhood'].fillna('Unknown')
    return frame[FEATURES]


def validate_property(data):
    result = {}
    for field, (low, high) in LIMITS.items():
        value = data.get(field)
        if isinstance(value, bool) or value is None:
            raise ValueError(f'{field} is required and must be numeric')
        value = float(value)
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{field} must be between {low} and {high}')
        if field == 'beds' and not value.is_integer():
            raise ValueError('beds must be a whole number')
        result[field] = value
    for field in OPTIONAL_FEATURES:
        value = data.get(field)
        if value in (None, '', 'unknown'):
            result[field] = None
            continue
        value = float(value)
        low, high = (0, 1) if field in UTILITY_FEATURES else ((1800, 2026) if field == 'yearBuilt' else (1, 10000))
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{field} must be between {low} and {high}')
        if field in UTILITY_FEATURES and value not in (0, 1):
            raise ValueError(f'{field} must be 0, 1, or unknown')
        result[field] = value
    return result


def nearest_neighborhood(latitude, longitude, locations):
    points = np.asarray([[p['latitude'], p['longitude']] for p in locations])
    distances = distance_km(latitude, longitude, points[:, 0], points[:, 1])
    index = int(np.argmin(distances))
    return locations[index]['neighborhood'], float(distances[index])
