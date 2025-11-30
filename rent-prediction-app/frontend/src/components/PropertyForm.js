import React, { useState, useEffect } from 'react';

const PropertyForm = ({ onSubmit, loading, initialData }) => {
  const [formData, setFormData] = useState({
    beds: 2,
    baths: 1,
    footage: 1000,
    latitude: 37.7749,
    longitude: -122.4194,
    purchasePrice: ''
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'purchasePrice' ? value : parseFloat(value)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="property-form">
      <div className="form-group">
        <label htmlFor="beds">Bedrooms</label>
        <input
          type="number"
          id="beds"
          name="beds"
          value={formData.beds}
          onChange={handleChange}
          min="0"
          max="10"
          step="1"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="baths">Bathrooms</label>
        <input
          type="number"
          id="baths"
          name="baths"
          value={formData.baths}
          onChange={handleChange}
          min="0.5"
          max="10"
          step="0.5"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="footage">Square Footage</label>
        <input
          type="number"
          id="footage"
          name="footage"
          value={formData.footage}
          onChange={handleChange}
          min="250"
          max="10000"
          step="10"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="latitude">Latitude</label>
        <input
          type="number"
          id="latitude"
          name="latitude"
          value={formData.latitude}
          onChange={handleChange}
          min="37.6"
          max="37.9"
          step="0.0001"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="longitude">Longitude</label>
        <input
          type="number"
          id="longitude"
          name="longitude"
          value={formData.longitude}
          onChange={handleChange}
          min="-122.6"
          max="-122.3"
          step="0.0001"
          required
        />
      </div>

      <div className="form-group investment-section">
        <label htmlFor="purchasePrice">Purchase Price (for ROI calculation)</label>
        <input
          type="number"
          id="purchasePrice"
          name="purchasePrice"
          value={formData.purchasePrice || ''}
          onChange={handleChange}
          min="100000"
          max="10000000"
          step="1000"
          placeholder="e.g., 1200000"
        />
        <small>Optional - Leave blank if only predicting rent</small>
      </div>

      <button 
        type="submit" 
        className={`submit-btn ${loading ? 'loading' : ''}`}
        disabled={loading}
      >
        {loading ? 'Analyzing...' : 'Predict Rent & ROI'}
      </button>
    </form>
  );
};

export default PropertyForm;