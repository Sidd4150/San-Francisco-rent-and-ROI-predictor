"""
Flask API using your ACTUAL trained Gradient Boosting model
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load your REAL trained model
MODEL_PATH = Path("models/gradient_boosting_model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print("🎯 SUCCESS: Your ACTUAL trained Gradient Boosting model loaded!")
    print(f"Model type: {type(model)}")
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

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": model_loaded,
        "model_type": "REAL Gradient Boosting Model (81.2% accuracy)" if model_loaded else "No model loaded"
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from request
        data = request.get_json()
        
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
        
        # Optional purchase price for ROI calculation
        purchase_price = data.get('purchasePrice', None)
        if purchase_price and purchase_price != '':
            purchase_price = float(purchase_price)
        else:
            purchase_price = None
        
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
        
        # Calculate confidence range (±10%)
        lower_bound = predicted_rent * 0.9
        upper_bound = predicted_rent * 1.1
        
        # Return response
        return jsonify({
            "estimated_rent": round(predicted_rent, 2),
            "confidence_range": {
                "lower": round(lower_bound, 2),
                "upper": round(upper_bound, 2)
            },
            "input_features": {
                "beds": beds,
                "baths": baths,
                "footage": footage,
                "latitude": latitude,
                "longitude": longitude,
                "purchasePrice": purchase_price
            },
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