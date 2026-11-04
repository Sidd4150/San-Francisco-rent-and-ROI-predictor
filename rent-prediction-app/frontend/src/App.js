import React, { useState } from 'react';
import api from './api';
import { isValidPrediction } from './prediction';
import PropertyForm from './components/PropertyForm';
import PredictionResult from './components/PredictionResult';
import MapView from './components/MapView';
import './App.css';



function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [propertyData, setPropertyData] = useState({
    beds: 2,
    baths: 1,
    footage: 1000,
    latitude: 37.7749,
    longitude: -122.4194,
    purchasePrice: ''
  });

  const handleLocationSelect = (lat, lng) => {
    setPropertyData(prev => ({
      ...prev,
      latitude: Math.round(lat * 10000) / 10000,
      longitude: Math.round(lng * 10000) / 10000
    }));
  };

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      console.log('Sending data:', formData); // Debug log
      const response = await api.post('/predict', formData);
      if (!isValidPrediction(response.data)) {
        throw new Error('The prediction service returned an unexpected response. Please try again shortly.');
      }
      console.log('Received response:', response.data); // Debug log
      setPrediction(response.data);
      setPropertyData(formData);
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.detail || err.message || 'An error occurred while predicting rent');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>San Francisco Rent Predictor</h1>
        <p>Estimate monthly rent based on property features using machine learning</p>
      </header>

      <main className="App-main">
        <div className="container">
          <div className="content-grid">
            <div className="form-section">
              <h2>Property Details</h2>
              <PropertyForm
                onSubmit={handleSubmit}
                loading={loading}
                initialData={propertyData}
              />

              {error && (
                <div className="error-message">
                  <p>{error}</p>
                </div>
              )}
            </div>

            <div className="map-section">
              <h2>Select Location</h2>
              <MapView
                onLocationSelect={handleLocationSelect}
                currentLocation={{
                  lat: propertyData.latitude,
                  lng: propertyData.longitude
                }}
              />
              <div className="coordinates">
                <span>Lat: {propertyData.latitude.toFixed(4)}</span>
                <span>Lng: {propertyData.longitude.toFixed(4)}</span>
              </div>
            </div>
          </div>

          {prediction && (
            <div className="result-section">
              <PredictionResult prediction={prediction} />
            </div>
          )}
        </div>
      </main>

      <footer className="App-footer">
        <p>Built with React & Flask | ML Model: Gradient Boosting (81.2% accuracy)</p>
      </footer>
    </div>
  );
}

export default App;
