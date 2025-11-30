"""
Simplified model training script that creates a mock model for demonstration.
For production, use Python 3.11 or 3.12 with the full requirements.
"""

import joblib
from pathlib import Path
import json

class MockGradientBoostingModel:
    """Mock model that simulates the gradient boosting predictions."""
    
    def predict(self, X):
        """
        Predict rent based on features.
        X should be array with: [beds, baths, footage, latitude, longitude]
        """
        # Simple prediction logic based on the feature analysis from notebook
        beds, baths, footage, lat, lng = X[0]
        
        # Base rent calculation
        base_rent = 1500
        
        # Add rent based on features (approximating the real model)
        rent = base_rent
        rent += beds * 800  # Each bedroom adds ~$800
        rent += baths * 400  # Each bathroom adds ~$400
        rent += footage * 1.5  # $1.5 per sq ft
        
        # Location adjustment (simplified)
        # Central SF (around 37.78, -122.42) is more expensive
        lat_factor = 1.0 + (37.78 - lat) * 2
        lng_factor = 1.0 + (-122.42 - lng) * 2
        location_multiplier = 1.0 + (lat_factor + lng_factor) * 0.05
        
        rent *= location_multiplier
        
        # Add some variance to make it more realistic
        import random
        rent *= random.uniform(0.95, 1.05)
        
        return [rent]

def main():
    print("Creating Mock Gradient Boosting Model")
    print("=" * 50)
    print("\nNOTE: This is a simplified model for demonstration.")
    print("For production use, please use Python 3.11 or 3.12 with full dependencies.\n")
    
    # Create mock model
    model = MockGradientBoostingModel()
    
    # Test the model
    test_features = [[2, 1.5, 1200, 37.7749, -122.4194]]
    prediction = model.predict(test_features)
    print(f"Test prediction for 2BR/1.5BA, 1200sqft in downtown SF: ${prediction[0]:,.2f}")
    
    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "gradient_boosting_model.pkl"
    joblib.dump(model, model_path)
    
    print(f"\nMock model saved to: {model_path}")
    print("\nYou can now run the FastAPI server!")
    
    # Also save model info
    model_info = {
        "type": "mock_model",
        "features": ["beds", "baths", "footage", "latitude", "longitude"],
        "note": "This is a simplified model. Use Python 3.11/3.12 for the real model."
    }
    
    with open(model_dir / "model_info.json", "w") as f:
        json.dump(model_info, f, indent=2)

if __name__ == "__main__":
    main()