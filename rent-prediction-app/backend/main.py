from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import uvicorn
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(title="SF Rent Prediction API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model for property features
class PropertyFeatures(BaseModel):
    beds: int = Field(ge=0, le=10, description="Number of bedrooms")
    baths: float = Field(ge=0.5, le=10, description="Number of bathrooms")
    footage: float = Field(ge=250, le=10000, description="Square footage")
    latitude: float = Field(ge=37.6, le=37.9, description="Latitude (San Francisco area)")
    longitude: float = Field(ge=-122.6, le=-122.3, description="Longitude (San Francisco area)")

    class Config:
        json_schema_extra = {
            "example": {
                "beds": 2,
                "baths": 1.5,
                "footage": 1200,
                "latitude": 37.7749,
                "longitude": -122.4194
            }
        }

# Response model
class RentPrediction(BaseModel):
    estimated_rent: float
    confidence_range: dict
    input_features: dict

# Load the trained model
MODEL_PATH = Path("models/gradient_boosting_model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully!")
except FileNotFoundError:
    print(f"Model file not found at {MODEL_PATH}")
    print("Please run train_model_simple.py first to generate the model file.")
    model = None

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SF Rent Prediction API",
        "endpoints": {
            "/predict": "POST - Predict rent for a property",
            "/docs": "GET - API documentation",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.post("/predict", response_model=RentPrediction)
async def predict_rent(features: PropertyFeatures):
    """
    Predict monthly rent for a property based on its features.
    """
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model not loaded. Please ensure the model file exists."
        )
    
    try:
        # Prepare features for model (order matters!)
        # Model expects: ['Beds', 'Baths', 'Footage', 'Latitude', 'Longitude']
        feature_array = np.array([[
            features.beds,
            features.baths,
            features.footage,
            features.latitude,
            features.longitude
        ]])
        
        # Make prediction
        predicted_rent = model.predict(feature_array)[0]
        
        # Calculate confidence range (±10% for simplicity)
        lower_bound = predicted_rent * 0.9
        upper_bound = predicted_rent * 1.1
        
        return RentPrediction(
            estimated_rent=round(predicted_rent, 2),
            confidence_range={
                "lower": round(lower_bound, 2),
                "upper": round(upper_bound, 2)
            },
            input_features=features.dict()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)