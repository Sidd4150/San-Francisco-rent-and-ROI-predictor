"""
Flask API using your ACTUAL trained Gradient Boosting model
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from pathlib import Path
import requests
from urllib.parse import quote

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load your REAL trained model
MODEL_PATH = Path("models/gradient_boosting_model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print("🎯 SUCCESS: Your ACTUAL trained Gradient Boosting model loaded!")
    print(f"Model type: {type(model)}")
    
    # Print model details to confirm it's YOUR model
    if hasattr(model, 'n_estimators'):
        print(f"✅ Model parameters:")
        print(f"   - n_estimators: {model.n_estimators}")
        print(f"   - learning_rate: {model.learning_rate}")
        print(f"   - max_depth: {model.max_depth}")
        print(f"   - Feature importances: {model.feature_importances_}")
    
    model_loaded = True
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    model_loaded = False

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to SF Rent Prediction API",
        "model_status": "REAL Gradient Boosting Model (81.2% accuracy)" if model_loaded else "Model not loaded",
        "endpoints": {
            "/predict": "POST - Predict rent for a property",
            "/health": "GET - Health check"
        }
    })

@app.route('/geocode', methods=['POST'])
def geocode_address():
    """Convert address to latitude/longitude coordinates."""
    try:
        data = request.get_json()
        address = data.get('address', '')
        
        if not address:
            return jsonify({"error": "Address is required"}), 400
        
        # Add "San Francisco, CA" if not already in address
        if "san francisco" not in address.lower():
            address = f"{address}, San Francisco, CA"
        
        # Use Nominatim (free OpenStreetMap geocoding)
        encoded_address = quote(address)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1"
        
        # Add user agent header (required by Nominatim)
        headers = {'User-Agent': 'SF-Rent-Predictor/1.0'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            results = response.json()
            if results:
                location = results[0]
                lat = float(location['lat'])
                lon = float(location['lon'])
                
                # Verify it's within SF bounds
                if 37.6 <= lat <= 37.9 and -122.6 <= lon <= -122.3:
                    return jsonify({
                        "latitude": lat,
                        "longitude": lon,
                        "display_name": location.get('display_name', address),
                        "success": True
                    })
                else:
                    return jsonify({
                        "error": "Address is outside San Francisco bounds",
                        "success": False
                    }), 400
            else:
                return jsonify({
                    "error": "Address not found",
                    "success": False
                }), 404
        else:
            return jsonify({
                "error": "Geocoding service error",
                "success": False
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": f"Geocoding error: {str(e)}",
            "success": False
        }), 500

@app.route('/health')
def health():
    model_details = {}
    if model_loaded and hasattr(model, 'n_estimators'):
        model_details = {
            "n_estimators": model.n_estimators,
            "learning_rate": model.learning_rate,
            "max_depth": model.max_depth,
            "n_features": model.n_features_in_,
            "feature_importances": model.feature_importances_.tolist()
        }
    
    return jsonify({
        "status": "healthy",
        "model_loaded": model_loaded,
        "model_type": "REAL Gradient Boosting Model (81.2% accuracy)" if model_loaded else "No model loaded",
        "model_parameters": model_details
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Debug log the entire request payload
        print("\n🔍 DEBUG: Full request payload:")
        print(data)
        
        # Validate required fields
        required_fields = ['beds', 'baths', 'footage', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Extract and validate features
        beds = float(data['beds'])
        baths = float(data['baths'])
        footage = float(data['footage'])
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        
        # Optional investment analysis fields
        purchase_price = data.get('purchasePrice', None)
        if purchase_price and purchase_price != '':
            purchase_price = float(purchase_price)
        else:
            purchase_price = None
        
        # Investment analysis parameters (optional) - convert to float and provide defaults
        investment_params = {
            'downPaymentPercent': float(data.get('downPaymentPercent', 20)),
            'interestRate': float(data.get('interestRate', 7.0)),
            'loanTermYears': int(data.get('loanTermYears', 30)),
            'propertyTaxRate': float(data.get('propertyTaxRate', 1.25)),
            'insuranceMonthly': float(data.get('insuranceMonthly', 200)),
            'utilitiesMonthly': float(data.get('utilitiesMonthly', 150)),
            'maintenancePercent': float(data.get('maintenancePercent', 1)),
            'propertyManagementPercent': float(data.get('propertyManagementPercent', 8)),
            'vacancyRate': float(data.get('vacancyRate', 5))
        }
        
        # Debug logging for investment parameters
        print("📊 DEBUG: Received investment parameters:")
        print(f"   - Purchase Price: {purchase_price}")
        for key, value in investment_params.items():
            print(f"   - {key}: {value}")
        
        # Validate ranges
        if not (0 <= beds <= 10):
            return jsonify({"error": "Beds must be between 0 and 10"}), 400
        if not (0.5 <= baths <= 10):
            return jsonify({"error": "Baths must be between 0.5 and 10"}), 400
        if not (250 <= footage <= 10000):
            return jsonify({"error": "Footage must be between 250 and 10000"}), 400
        if not (37.6 <= latitude <= 37.9):
            return jsonify({"error": "Latitude must be between 37.6 and 37.9"}), 400
        if not (-122.6 <= longitude <= -122.3):
            return jsonify({"error": "Longitude must be between -122.6 and -122.3"}), 400
        
        # Check if model is loaded
        if not model_loaded:
            return jsonify({
                "error": "Model not loaded. Please check server logs."
            }), 503
        
        # Prepare features for YOUR model (order: Beds, Baths, Footage, Latitude, Longitude)
        feature_array = np.array([[beds, baths, footage, latitude, longitude]])
        
        # Make prediction using YOUR ACTUAL TRAINED MODEL
        predicted_rent = model.predict(feature_array)[0]
        
        # Build input features dictionary
        input_features = {
            "beds": beds,
            "baths": baths,
            "footage": footage,
            "latitude": latitude,
            "longitude": longitude,
            "purchasePrice": purchase_price
        }
        
        # Add investment parameters if provided
        if purchase_price:
            input_features.update(investment_params)
        
        # Return response
        return jsonify({
            "estimated_rent": round(predicted_rent, 2),
            "input_features": input_features,
            "model_info": {
                "type": "Gradient Boosting Regressor",
                "accuracy": "81.2%",
                "trained_on": "SF Rental Data",
                "features": ["Beds", "Baths", "Footage", "Latitude", "Longitude"]
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Prediction error: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🏠 SF RENT PREDICTION API - REAL MODEL VERSION")
    print("=" * 60)
    if model_loaded:
        print("✅ Using your ACTUAL trained Gradient Boosting model!")
        print("🎯 81.2% accuracy on test data")
        print("📊 Trained on San Francisco rental listings")
        print("🚀 Ready for real predictions!")
    else:
        print("❌ Model not loaded - check the models/ directory")
    print("🌐 API available at: http://localhost:8000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8000, debug=True)