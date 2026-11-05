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
      const response = await api.post('/predict', formData);
      if (!isValidPrediction(response.data)) {
        throw new Error('The prediction service returned an unexpected response. Please try again shortly.');
      }
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
        <div className="header-inner">
          <div className="top-bar">
            <div className="wordmark"><span className="wordmark-symbol">SF</span> RENT ANALYSIS</div>
            <a href="https://data.sf.gov/Housing-and-Buildings/Rent-Board-Housing-Inventory/gdc7-dmcn" target="_blank" rel="noreferrer">View source data ↗</a>
          </div>
          <div className="header-copy">
            <p className="eyebrow">2026 housing inventory</p>
            <h1>San Francisco rent analysis.</h1>
            <p className="header-description">Estimate rent, review the range, and work through the numbers.</p>
          </div>
        </div>
      </header>

      <main className="App-main">
        <div className="container">
          <aside className="data-banner">
            <strong>Built on 2026 San Francisco Rent Board reports</strong>
            <p>Estimates reflect occupied rents for tenancies begun in 2025–2026, including possible subsidized units.
              They are a benchmark, not an advertised market-rent quote. Rent and floor area are reported in bands.</p>
          </aside>
          <div className="content-grid">
            <div className="form-section">
              <div className="section-label"><span>01</span><h2>Property details</h2></div>
              <PropertyForm
                onSubmit={handleSubmit}
                loading={loading}
                initialData={propertyData}
                onLocationChange={handleLocationSelect}
              />

              {error && (
                <div className="error-message">
                  <p>{error}</p>
                </div>
              )}
            </div>

            <div className="map-section">
              <div className="section-label"><span>02</span><h2>Location</h2></div>
              <p className="section-caption">Select the property on the map, or enter its address in the form.</p>
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
              <p className="map-source">Neighborhood is inferred from the nearest published block. Exact addresses are not part of the training data.</p>
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
        <div className="footer-inner">
          <p>San Francisco · Rent &amp; cash flow</p>
          <p>Based on reported rents. Model performance accompanies each estimate.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
