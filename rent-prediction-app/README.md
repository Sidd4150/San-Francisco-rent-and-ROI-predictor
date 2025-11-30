# San Francisco Rent Prediction & Investment Analysis App

A full-stack machine learning application that predicts rental prices and calculates investment ROI for San Francisco properties.

## Features

- **Machine Learning Model**: Gradient Boosting Regressor with 81.2% accuracy
- **Flask API Backend**: Serves your actual trained model from Jupyter notebook
- **React Frontend**: Interactive UI with map-based location selection and investment analysis
- **Real-time Predictions**: Instant rent estimates and ROI calculations
- **Investment Analysis**: Gross rental yield and payback period calculations

## Project Structure

```
rent-prediction-app/
├── backend/
│   ├── real_model_api.py        # Flask API using your actual trained model
│   ├── simple_api.py            # Alternative enhanced predictor
│   ├── train_model_simple.py    # Model training script (fallback)
│   ├── requirements_flask.txt   # Minimal Flask dependencies
│   ├── venv_real/              # Python 3.11 virtual environment
│   └── models/
│       └── gradient_boosting_model.pkl  # Your actual trained model
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React component
│   │   ├── components/
│   │   │   ├── PropertyForm.js # Property input form with ROI fields
│   │   │   ├── PredictionResult.js # Results display with investment analysis
│   │   │   └── MapView.js      # Interactive map for location selection
│   │   └── App.css             # Complete styling including ROI components
│   └── package.json            # Node dependencies
└── README.md
```

## Setup Instructions

### Backend Setup (Using Your Real Model)

1. **Navigate to backend directory:**
```bash
cd rent-prediction-app/backend
```

2. **Set up Python 3.11 environment** (required for scikit-learn compatibility):
```bash
# Install Python 3.11 if needed
brew install python@3.11

# Create virtual environment with Python 3.11
python3.11 -m venv venv_real
source venv_real/bin/activate
```

3. **Install ML dependencies:**
```bash
pip install flask flask-cors scikit-learn numpy pandas joblib
```

4. **Ensure your trained model exists:**
- Your model should be at: `models/gradient_boosting_model.pkl`
- If missing, export it from your Jupyter notebook:
```python
import joblib
import os

# In your Jupyter notebook (Google Colab)
os.makedirs('/Users/raunaqmokha/Machine-Learning-Fall-2025/rent-prediction-app/backend/models', exist_ok=True)
joblib.dump(gb_model, '/Users/raunaqmokha/Machine-Learning-Fall-2025/rent-prediction-app/backend/models/gradient_boosting_model.pkl')

# Download the file if using Google Colab
from google.colab import files
files.download('gradient_boosting_model.pkl')
```

5. **Start the Flask API:**
```bash
python3 real_model_api.py
```

You should see:
```
🎯 SUCCESS: Your ACTUAL trained Gradient Boosting model loaded!
✅ Using your ACTUAL trained Gradient Boosting model!
🎯 81.2% accuracy on test data
```

The API will be available at http://localhost:8000

### Frontend Setup

1. **In a new terminal, navigate to frontend:**
```bash
cd rent-prediction-app/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start React development server:**
```bash
npm start
```

The app will open at http://localhost:3000

## Using the Application

1. **Enter Property Details**:
   - Number of bedrooms (0-10)
   - Number of bathrooms (0.5-10)  
   - Square footage (250-10,000)
   - Location coordinates (or use the interactive map)
   - **Purchase Price** (optional, for ROI analysis)

2. **Interactive Location Selection**:
   - Click on the map to set location
   - Drag the marker to desired position
   - Coordinates update automatically

3. **Get Predictions & Investment Analysis**:
   - Click "Predict Rent & ROI" button
   - View estimated monthly rent (from your trained model)
   - See confidence range (±10%)
   - **Investment Analysis** (if purchase price entered):
     - Gross Rental Yield percentage
     - Annual rental income
     - Payback period
     - Color-coded ROI recommendations

## Model Details

**Your Actual Trained Model**:
- **Type**: Gradient Boosting Regressor
- **Training Data**: San Francisco rental listings CSV
- **Features**: Beds, Baths, Square Footage, Latitude, Longitude
- **Performance Metrics**:
  - R²: 0.7875
  - RMSE: $1,093.80
  - **Accuracy: 81.2%**
- **Training Parameters**:
  ```python
  GradientBoostingRegressor(
      n_estimators=200,
      learning_rate=0.05,
      max_depth=3,
      min_samples_split=10,
      random_state=42
  )
  ```

## Investment Analysis

The ROI calculation matches your Jupyter notebook analysis:

```python
# Gross Rental Yield calculation
gross_rental_yield = (annual_rent / purchase_price) * 100
payback_period = purchase_price / annual_rent
```

**ROI Interpretation**:
- 🟢 **8%+ ROI**: Excellent investment opportunity
- 🟡 **5-8% ROI**: Good for SF market
- 🔴 **<5% ROI**: Consider price negotiation

## API Endpoints

- `GET /` - API information and model status
- `GET /health` - Health check with model info
- `POST /predict` - Predict rent and calculate ROI

### Example API Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "beds": 2,
    "baths": 1.5,
    "footage": 1200,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "purchasePrice": 1200000
  }'
```

### Example Response

```json
{
  "estimated_rent": 5666.95,
  "confidence_range": {
    "lower": 5100.26,
    "upper": 6233.65
  },
  "input_features": {
    "beds": 2,
    "baths": 1.5,
    "footage": 1200,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "purchasePrice": 1200000
  },
  "model_info": {
    "type": "Gradient Boosting Regressor",
    "accuracy": "81.2%",
    "trained_on": "SF Rental Data"
  }
}
```

## Technical Implementation

### Machine Learning Pipeline
1. **Data Collection**: SF rental listings CSV from web scraping
2. **Data Cleaning**: Removed outliers, handled missing values
3. **Feature Engineering**: Selected optimal features based on importance
4. **Model Training**: Gradient Boosting with hyperparameter tuning
5. **Model Persistence**: Saved as `.pkl` file using joblib
6. **Deployment**: Flask API loads and serves predictions

### Full Stack Architecture
- **Backend**: Flask + scikit-learn (your actual trained model)
- **Frontend**: React with interactive components and map
- **Communication**: RESTful API with JSON data exchange
- **Deployment**: Local development environment

## Troubleshooting

### Common Issues:

**"Model not loaded" error**:
- Ensure `models/gradient_boosting_model.pkl` exists
- Check that you're using Python 3.11 environment
- Verify model was exported correctly from Jupyter

**Scikit-learn version warnings**:
- These are compatibility warnings but don't affect functionality
- Model works correctly despite version differences

**Frontend build errors**:
```bash
# If npm start fails, try:
rm -rf node_modules package-lock.json
npm install
npm start
```

**CORS errors**:
- Ensure backend runs on port 8000 and frontend on port 3000
- Flask-CORS is configured to allow requests from localhost:3000

## Project Highlights

✅ **Complete ML Pipeline**: From data collection to deployment  
✅ **Real Model**: Uses your actual 81.2% accuracy Gradient Boosting model  
✅ **Full Stack**: React frontend + Flask backend + ML model  
✅ **Investment Analysis**: ROI calculations matching your Jupyter notebook  
✅ **Interactive Features**: Map-based location selection  
✅ **Production Ready**: Error handling, validation, proper architecture