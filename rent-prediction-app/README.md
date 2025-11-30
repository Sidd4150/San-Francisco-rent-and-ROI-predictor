# San Francisco Rent Prediction App

A full-stack application that predicts rental prices for properties in San Francisco using machine learning.

## Features

- **Machine Learning Model**: Gradient Boosting model with 81.2% accuracy
- **FastAPI Backend**: Modern, fast API with automatic documentation
- **React Frontend**: Interactive UI with map-based location selection
- **Real-time Predictions**: Get instant rent estimates based on property features

## Project Structure

```
rent-prediction-app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── train_model.py       # Model training script
│   ├── requirements.txt     # Python dependencies
│   └── models/             # Saved ML models
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── components/     # React components
│   │   └── App.css         # Styling
│   └── package.json        # Node dependencies
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd rent-prediction-app/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create the models directory:
```bash
mkdir models
```

5. Train the model:
```bash
python train_model.py
```
When prompted, either:
- Press Enter to use synthetic training data (for testing)
- Provide the path to your CSV file: `/Users/raunaqmokha/Downloads/Z-Real-Estate-Scraper-Data-Rental Listings in San Francisco CA-20251111.csv`

6. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### Frontend Setup

1. In a new terminal, navigate to the frontend directory:
```bash
cd rent-prediction-app/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The app will open at http://localhost:3000

## Using the Application

1. **Enter Property Details**:
   - Number of bedrooms (0-10)
   - Number of bathrooms (0.5-10)
   - Square footage (250-10,000)
   - Location coordinates (or use the map)

2. **Select Location**:
   - Click on the map to set location
   - Or drag the marker to desired position
   - Coordinates update automatically

3. **Get Prediction**:
   - Click "Predict Rent" button
   - View estimated monthly rent
   - See confidence range (±10%)

## Model Details

The Gradient Boosting model was trained on San Francisco rental data with these features:
- Beds
- Baths
- Square Footage
- Latitude
- Longitude

Performance metrics:
- R²: 0.7875
- RMSE: $1,093.80
- Accuracy: 81.2%

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /predict` - Predict rent (requires JSON body with property features)
- `GET /docs` - Interactive API documentation

## Example API Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "beds": 2,
    "baths": 1.5,
    "footage": 1200,
    "latitude": 37.7749,
    "longitude": -122.4194
  }'
```

## Troubleshooting

- **Model not found error**: Make sure you run `train_model.py` before starting the server
- **CORS errors**: Ensure both backend and frontend are running on the correct ports
- **Map not loading**: Check that you have an internet connection for map tiles

## Future Enhancements

- Add more property features (amenities, property age, etc.)
- Implement user authentication
- Add historical rent trends
- Support for other cities
- Deploy to cloud platforms