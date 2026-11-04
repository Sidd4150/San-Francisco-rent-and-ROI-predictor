"""Serve the evaluated recent-tenancy model and its data provenance."""
import json
import math
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import joblib
import requests
from threadpoolctl import threadpool_limits

from rental_features import LIMITS, OPTIONAL_FEATURES, feature_frame, nearest_neighborhood, validate_property

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_BUILD = BASE_DIR.parent / 'frontend' / 'build'
app = Flask(__name__, static_folder=str(FRONTEND_BUILD / 'static'))
CORS(app)
MODEL_PATH = BASE_DIR / 'models' / 'rental_model.joblib'
try:
    bundle = joblib.load(MODEL_PATH)
    model = bundle['pipeline']
    report = bundle['report']
    model_loaded = True
    app.logger.info('Loaded evaluated model %s', report['version'])
except Exception:
    app.logger.exception('Unable to load rental model')
    bundle, model, report, model_loaded = None, None, None, False
try:
    market_context = json.loads((BASE_DIR / 'data' / 'market_context.json').read_text())
except (OSError, ValueError):
    market_context = None


def model_summary():
    return dict(version=report['version'], type=report['model'], target=report['target'],
                source=report['data']['source'], source_url=report['data']['source_url'],
                data_as_of=report['data']['data_as_of'], usable_records=report['data']['usable_rows'],
                validation=report['test'], five_feature_baseline=report['five_feature_baseline'],
                improvement_over_five_features_pct=report['improvement_over_five_features_pct'],
                features=report['features'], limitations=report['limitations'])


@app.get('/')
def home():
    if (FRONTEND_BUILD / 'index.html').is_file():
        return send_from_directory(FRONTEND_BUILD, 'index.html')
    return jsonify(message='San Francisco recent-tenancy rent prediction API', model_loaded=model_loaded,
                   endpoints=['/health', '/model-info', '/predict', '/geocode'])


@app.get('/<path:filename>')
def frontend_asset(filename):
    return send_from_directory(FRONTEND_BUILD, filename)


@app.get('/health')
def health():
    return jsonify(status='healthy' if model_loaded else 'unhealthy', model_loaded=model_loaded,
                   model_version=report['version'] if report else None), 200 if model_loaded else 503


@app.get('/model-info')
def model_info():
    if not model_loaded:
        return jsonify(error='Model unavailable'), 503
    return jsonify(**report, market_context=market_context)


def json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError('Request body must be a JSON object')
    return data


@app.post('/geocode')
def geocode_address():
    try:
        address = json_object().get('address')
        if not isinstance(address, str) or not address.strip():
            raise ValueError('A street address is required')
        address = address.strip()
        if 'san francisco' not in address.lower():
            address += ', San Francisco, CA'
        response = requests.get('https://nominatim.openstreetmap.org/search',
                                params={'q': address, 'format': 'json', 'limit': 1},
                                headers={'User-Agent': 'SF-Rent-Predictor/2.0'}, timeout=10)
        response.raise_for_status()
        results = response.json()
        if not results:
            return jsonify(error='Address not found', success=False), 404
        location = results[0]
        latitude, longitude = float(location['lat']), float(location['lon'])
        if not (37.70 <= latitude <= 37.84 and -122.52 <= longitude <= -122.35):
            raise ValueError('Address is outside the supported San Francisco area')
        return jsonify(latitude=latitude, longitude=longitude,
                       display_name=location.get('display_name', address), success=True)
    except ValueError as error:
        return jsonify(error=str(error), success=False), 400
    except requests.Timeout:
        return jsonify(error='Address lookup timed out. Please try again.', success=False), 504
    except requests.RequestException:
        return jsonify(error='Address lookup is temporarily unavailable.', success=False), 502


def investment_inputs(data):
    specs = {'downPaymentPercent': (20, 0, 100), 'interestRate': (7, 0, 30),
             'loanTermYears': (30, 1, 50), 'propertyTaxRate': (1.25, 0, 10),
             'insuranceMonthly': (200, 0, 100000), 'utilitiesMonthly': (150, 0, 100000),
             'maintenancePercent': (1, 0, 100), 'propertyManagementPercent': (8, 0, 100),
             'vacancyRate': (5, 0, 100), 'hoaMonthly': (0, 0, 100000)}
    values = {}
    for field, (default, low, high) in specs.items():
        value = data.get(field)
        value = default if value in (None, '') else float(value)
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{field} must be between {low} and {high}')
        values[field] = value
    purchase_price = data.get('purchasePrice')
    if purchase_price not in (None, ''):
        purchase_price = float(purchase_price)
        if not math.isfinite(purchase_price) or purchase_price <= 0:
            raise ValueError('purchasePrice must be a positive number')
    else:
        purchase_price = None
    return dict(purchasePrice=purchase_price, **values)


@app.post('/predict')
def predict():
    try:
        data = json_object()
        features = validate_property(data)
        investment = investment_inputs(data)
        if not model_loaded:
            return jsonify(error='Prediction model is unavailable. Please try again later.'), 503
        neighborhood, distance = nearest_neighborhood(features['latitude'], features['longitude'], bundle['locations'])
        features['neighborhood'] = neighborhood
        with threadpool_limits(limits=1):
            estimated_rent = float(model.predict(feature_frame([features]))[0])
        if not math.isfinite(estimated_rent):
            raise RuntimeError('Model returned a non-finite result')
        unknown = [field for field in OPTIONAL_FEATURES if features[field] is None]
        radius = bundle['unknown_optional_radius'] if unknown else bundle['calibration_radius']
        warnings = []
        if unknown:
            warnings.append('Some building or utility details are unknown; the range uses the more conservative calibration for missing details.')
        if features['footage'] > 2500 or features['beds'] >= 4:
            warnings.append('Large homes have fewer examples. Luxury rents of $7,000 or more are excluded from this dataset.')
        if distance > .75:
            warnings.append('This location is far from a published inventory point; the inferred neighborhood may be less reliable.')
        if features['beds'] == 5 or features['baths'] == 3:
            warnings.append('The public data groups 5+ bedrooms and 3+ bathrooms together.')
        return jsonify(estimated_rent=round(estimated_rent, 2),
                       input_features=dict(**features, **investment),
                       prediction_interval=dict(lower=round(max(0, estimated_rent - radius), 2),
                                                upper=round(estimated_rent + radius, 2),
                                                nominal_coverage=.8,
                                                observed_test_coverage_pct=report['unknown_optional_test' if unknown else 'test']['interval_coverage_pct'],
                                                unknown_details=bool(unknown),
                                                note='Calibrated on 2025 reported rents; not a guarantee for future or advertised rents.'),
                       model_info=model_summary(), warnings=warnings,
                       market_context=dict(latest=market_context['latest'], source_url=market_context['source_url'],
                                           attribution=market_context['attribution'], note=market_context['note']) if market_context else None)
    except (ValueError, TypeError, OverflowError) as error:
        return jsonify(error=str(error) or 'Please supply valid numeric property details'), 400
    except Exception:
        app.logger.exception('Prediction failed')
        return jsonify(error='Prediction failed. Please try again later.'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
