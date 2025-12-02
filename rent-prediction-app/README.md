# San Francisco Rent Prediction & Investment Analysis App

A full-stack machine learning application that predicts rental prices and provides comprehensive investment cash flow analysis for San Francisco properties.

## Features

- **Machine Learning Model**: Gradient Boosting Regressor with 81.2% accuracy trained on SF rental data
- **Flask API Backend**: Serves your actual trained model for real-time predictions
- **React Frontend**: Interactive UI with map-based location selection
- **Address Geocoding**: Convert street addresses to coordinates automatically
- **Investment Analysis**: Complete cash flow analysis including:
  - Mortgage payment calculations (P&I)
  - Property taxes (using SF rate of 1.25%)
  - Insurance, utilities, maintenance costs
  - Property management fees
  - Vacancy loss estimates
  - Net monthly cash flow
  - Cash-on-Cash return
  - Investment recommendation (Good/Poor)

## Project Structure

```
rent-prediction-app/
├── backend/
│   ├── real_model_api.py          # Flask API using your trained model
│   ├── requirements_flask.txt     # Python dependencies
│   └── models/
│       └── gradient_boosting_model.pkl  # Your trained ML model
├── frontend/
│   ├── src/
│   │   ├── App.js                 # Main React component
│   │   ├── App.css                # Styling
│   │   └── components/
│   │       ├── PropertyForm.js    # Property & investment input form
│   │       ├── PredictionResult.js # Results with cash flow analysis
│   │       └── MapView.js         # Interactive map for location
│   └── package.json               # Node dependencies
└── README.md
```

## Prerequisites

- **Python 3.11** (required for scikit-learn compatibility)
- **Node.js 16+** and npm
- **Git** (optional, for cloning)

## Quick Start

### 1. Clone or Download the Project

```bash
cd /path/to/Machine-Learning-Fall-2025
```

### 2. Backend Setup

```bash
# Navigate to backend
cd rent-prediction-app/backend

# Create Python 3.11 virtual environment
python3.11 -m venv venv_real

# Activate virtual environment
source venv_real/bin/activate  # Mac/Linux
# OR
venv_real\Scripts\activate     # Windows

# Install dependencies
pip install flask flask-cors scikit-learn numpy pandas joblib requests

# Start the API server
python real_model_api.py
```

You should see:
```
🎯 SUCCESS: Your ACTUAL trained Gradient Boosting model loaded!
✅ Model parameters:
   - n_estimators: 200
   - learning_rate: 0.05
   - max_depth: 3
🌐 API available at: http://localhost:8000
```

### 3. Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd rent-prediction-app/frontend

# Install dependencies
npm install

# Start React development server
npm start
```

The app will open at **http://localhost:3000**

## How to Use

### Basic Rent Prediction

1. Enter property details:
   - Bedrooms (0-10)
   - Bathrooms (0.5-10)
   - Square footage (250-10,000)

2. Set location using one of three methods:
   - **Address**: Type an address and click "Convert to Coordinates"
   - **Map**: Click on the interactive map
   - **Manual**: Enter latitude/longitude directly

3. Click **"Predict Rent & ROI"** to get your estimated monthly rent

### Investment Analysis

To see full cash flow analysis, also enter:

| Field | Description | Default |
|-------|-------------|---------|
| Purchase Price | Property purchase price | Required |
| Down Payment % | Percentage of purchase price | 20% |
| Interest Rate % | Annual mortgage interest rate | 7% |
| Loan Term | Mortgage length in years | 30 |
| Property Tax Rate % | Annual property tax rate | 1.25% (SF) |
| Insurance | Monthly insurance cost | $0 |
| Utilities | Monthly utilities cost | $0 |
| Maintenance % | % of rent for maintenance | 0% |
| Property Mgmt % | % of rent for management | 0% |
| Vacancy Rate % | Expected vacancy percentage | 0% |

### Understanding Results

The app calculates:

- **Gross Rental Yield**: `(Annual Rent / Purchase Price) × 100`
- **Monthly Mortgage (P&I)**: Standard amortization formula
- **Property Tax**: `(Purchase Price × Tax Rate) / 12`
- **Net Cash Flow**: `Rental Income - All Monthly Expenses`
- **Cash-on-Cash Return**: `(Annual Cash Flow / Down Payment) × 100`

**Investment Decision**:
- ✅ **GOOD INVESTMENT**: Positive monthly cash flow
- ❌ **POOR INVESTMENT**: Negative monthly cash flow

## How It Works

### System Architecture

```
┌─────────────────┐    HTTP POST     ┌─────────────────┐    predict()   ┌─────────────────┐
│  React Frontend │ ───────────────► │   Flask API     │ ─────────────► │  ML Model       │
│  localhost:3000 │                  │  localhost:8000 │                │  (.pkl file)    │
│                 │ ◄─────────────── │                 │ ◄───────────── │  81.2% accuracy │
│  Investment     │    JSON Response │  /predict       │   $4,251/mo    │                 │
│  Calculations   │                  │  /geocode       │                │                 │
└─────────────────┘                  └─────────────────┘                └─────────────────┘
```

### Data Flow

1. **User Input** → PropertyForm.js collects property & investment details
2. **API Request** → App.js sends POST to Flask backend
3. **ML Prediction** → real_model_api.py runs your trained model
4. **Response** → Backend returns predicted rent + input features
5. **Calculations** → PredictionResult.js computes all investment metrics
6. **Display** → Results shown with visual indicators

### Key Formulas

**Monthly Mortgage Payment (P&I)**:
```
M = P × [r(1+r)^n] / [(1+r)^n - 1]

Where:
P = Loan Amount (Purchase Price - Down Payment)
r = Monthly Interest Rate (Annual Rate / 12 / 100)
n = Total Payments (Years × 12)
```

**Example**: $636,000 loan @ 7% for 30 years = $4,231/month

**Cash Flow**:
```
Net Monthly Cash Flow = Rental Income - (Mortgage + Taxes + Insurance + Utilities + Maintenance + Management + Vacancy)
```

## Model Details

| Metric | Value |
|--------|-------|
| Model Type | Gradient Boosting Regressor |
| Accuracy | 81.2% |
| R² Score | 0.7875 |
| RMSE | $1,093.80 |
| Training Data | San Francisco rental listings |
| Features | Beds, Baths, Sqft, Latitude, Longitude |

**Model Parameters**:
```python
GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    min_samples_split=10,
    random_state=42
)
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and status |
| GET | `/health` | Health check with model details |
| POST | `/predict` | Predict rent for a property |
| POST | `/geocode` | Convert address to coordinates |

### Example: Predict Rent

**Request**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "beds": 2,
    "baths": 1.5,
    "footage": 1200,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "purchasePrice": 795000,
    "downPaymentPercent": 20,
    "interestRate": 7,
    "loanTermYears": 30,
    "propertyTaxRate": 1.25,
    "insuranceMonthly": 200,
    "utilitiesMonthly": 150,
    "maintenancePercent": 1,
    "propertyManagementPercent": 8,
    "vacancyRate": 5
  }'
```

**Response**:
```json
{
  "estimated_rent": 4251.32,
  "input_features": {
    "beds": 2,
    "baths": 1.5,
    "footage": 1200,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "purchasePrice": 795000,
    "downPaymentPercent": 20,
    "interestRate": 7,
    "loanTermYears": 30,
    "propertyTaxRate": 1.25,
    "insuranceMonthly": 200,
    "utilitiesMonthly": 150,
    "maintenancePercent": 1,
    "propertyManagementPercent": 8,
    "vacancyRate": 5
  },
  "model_info": {
    "type": "Gradient Boosting Regressor",
    "accuracy": "81.2%",
    "trained_on": "SF Rental Data",
    "features": ["Beds", "Baths", "Footage", "Latitude", "Longitude"]
  }
}
```

### Example: Geocode Address

**Request**:
```bash
curl -X POST "http://localhost:8000/geocode" \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Market Street"}'
```

**Response**:
```json
{
  "latitude": 37.7937,
  "longitude": -122.3965,
  "display_name": "123 Market Street, San Francisco, CA",
  "success": true
}
```

## Troubleshooting

### Backend Issues

**"Model not loaded" error**:
```bash
# Ensure model file exists
ls backend/models/gradient_boosting_model.pkl

# Check Python version (must be 3.11)
python --version
```

**Port already in use**:
```bash
# Kill existing process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**npm install fails**:
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**CORS errors**:
- Ensure backend is running on port 8000
- Ensure frontend is running on port 3000

### Model Issues

**Scikit-learn version warning**:
- This is a compatibility warning but doesn't affect predictions
- Model will work correctly

**Recreating the model** (if .pkl file is missing):
```python
# In your Jupyter notebook / Google Colab
import joblib
joblib.dump(gb_model, 'gradient_boosting_model.pkl')

# Download and place in backend/models/
```

## Technologies Used

- **Backend**: Python 3.11, Flask, scikit-learn, NumPy, Pandas
- **Frontend**: React 18, Axios, Leaflet (maps)
- **ML Model**: Gradient Boosting Regressor
- **APIs**: OpenStreetMap Nominatim (geocoding)

## Project Highlights

✅ Real ML model trained on SF rental data (81.2% accuracy)
✅ Complete cash flow analysis for investment decisions
✅ Interactive map-based location selection
✅ Address-to-coordinates geocoding
✅ Responsive UI with clear investment recommendations
✅ Full-stack architecture (React + Flask + scikit-learn)

## License

This project was created for educational purposes as part of a Machine Learning course.
