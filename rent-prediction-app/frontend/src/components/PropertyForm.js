import React, { useState, useEffect } from 'react';
import api from '../api';

const PropertyForm = ({ onSubmit, loading, initialData, onLocationChange }) => {
  const [formData, setFormData] = useState({
    beds: 2,
    baths: 1,
    footage: 1000,
    latitude: 37.7749,
    longitude: -122.4194,
    purchasePrice: '',
    address: '',
    yearBuilt: '',
    buildingUnits: '',
    waterIncluded: '',
    gasIncluded: '',
    electricityIncluded: '',
    refuseIncluded: '',
    // Investment analysis fields
    downPaymentPercent: 20,
    interestRate: 7.0,
    loanTermYears: 30,
    propertyTaxRate: 1.25,
    insuranceMonthly: 200,
    utilitiesMonthly: 150,
    maintenancePercent: 1,
    propertyManagementPercent: 8,
    vacancyRate: 5,
    hoaMonthly: 0,
    ...initialData
  });

  const [geocoding, setGeocoding] = useState(false);
  const [geocodeError, setGeocodeError] = useState(null);

  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({ ...prev, latitude: initialData.latitude, longitude: initialData.longitude }));
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const textFields = ['address']; // Remove 'purchasePrice' from text fields
    
    // Parse numeric values, but handle purchasePrice specially since it can be empty
    let parsedValue;
    if (textFields.includes(name)) {
      parsedValue = value;
    } else if (value === '' || name === 'purchasePrice') {
      parsedValue = value === '' ? '' : parseFloat(value);
    } else {
      parsedValue = parseFloat(value);
    }
    
    
    setFormData(prev => ({
      ...prev,
      [name]: parsedValue
    }));
    
    // Clear geocode error when typing in address field
    if (name === 'address' && geocodeError) {
      setGeocodeError(null);
    }
  };

  const handleGeocodeAddress = async () => {
    setGeocoding(true);
    setGeocodeError(null);

    try {
      const response = await api.post('/geocode', {
        address: formData.address
      });

      if (response.data.success) {
        onLocationChange?.(response.data.latitude, response.data.longitude);
        setFormData(prev => ({
          ...prev,
          latitude: Math.round(response.data.latitude * 10000) / 10000,
          longitude: Math.round(response.data.longitude * 10000) / 10000
        }));
      }
    } catch (error) {
      setGeocodeError(error.response?.data?.error || 'Failed to convert address');
    } finally {
      setGeocoding(false);
    }
  };


  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="property-form">
      <div className="property-basics">
      <div className="form-group">
        <label htmlFor="beds">Bedrooms</label>
        <input
          type="number"
          id="beds"
          name="beds"
          value={formData.beds}
          onChange={handleChange}
          min="0"
          max="5"
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
          min="1"
          max="3"
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
          min="251"
          max="4000"
          step="1"
          required
        />
      </div>

      </div>
      <div className="location-section">
        <h3>Address &amp; coordinates</h3>
        
        <div className="form-group">
          <label htmlFor="address">Street Address (San Francisco)</label>
          <input
            type="text"
            id="address"
            name="address"
            value={formData.address || ''}
            onChange={handleChange}
            placeholder="e.g., 1 Market Street"
          />
          <button 
            type="button" 
            onClick={handleGeocodeAddress}
            disabled={!formData.address || geocoding}
            className="geocode-btn"
          >
            {geocoding ? 'Converting...' : 'Get Coordinates'}
          </button>
          <small>Enter SF address and click "Get Coordinates" to auto-fill lat/lng</small>
          {geocodeError && (
            <div className="error-message">
              <p>{geocodeError}</p>
            </div>
          )}
        </div>

        <div className="coordinates-section">
          <div className="form-group">
            <label htmlFor="latitude">Latitude</label>
            <input
              type="number"
              id="latitude"
              name="latitude"
              value={formData.latitude}
              onChange={handleChange}
              min="37.70"
              max="37.84"
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
              min="-122.52"
              max="-122.35"
              step="0.0001"
              required
            />
          </div>
        </div>
      </div>

      <fieldset className="building-section">
        <legend>Building &amp; included utilities</legend>
        <p>These details improve the estimate. Leave anything you do not know blank.</p>
        <div className="investment-grid">
          <div className="form-group">
            <label htmlFor="yearBuilt">Year built</label>
            <input id="yearBuilt" name="yearBuilt" type="number" min="1800" max="2026" step="1"
              placeholder="Unknown" value={formData.yearBuilt} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label htmlFor="buildingUnits">Units in building</label>
            <input id="buildingUnits" name="buildingUnits" type="number" min="1" max="10000" step="1"
              placeholder="Unknown" value={formData.buildingUnits} onChange={handleChange} />
          </div>
          {[
            ['waterIncluded', 'Water / sewer included'], ['gasIncluded', 'Natural gas included'],
            ['electricityIncluded', 'Electricity included'], ['refuseIncluded', 'Garbage / recycling included'],
          ].map(([name, label]) => (
            <div className="form-group" key={name}>
              <label htmlFor={name}>{label}</label>
              <select id={name} name={name} value={formData[name]} onChange={handleChange}>
                <option value="">Unknown</option><option value="1">Yes</option><option value="0">No</option>
              </select>
            </div>
          ))}
        </div>
        <small>Neighborhood and distance features are inferred from location. Bedrooms 5+ and bathrooms 3+ are grouped in the source data.</small>
      </fieldset>

      <div className="investment-section">
        <h3>Investment assumptions</h3>
        
        <div className="investment-grid">
          <div className="form-group">
            <label htmlFor="purchasePrice">Purchase Price</label>
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
          </div>

          <div className="form-group">
            <label htmlFor="downPaymentPercent">Down Payment (%)</label>
            <input
              type="number"
              id="downPaymentPercent"
              name="downPaymentPercent"
              value={formData.downPaymentPercent}
              onChange={handleChange}
              min="0"
              max="100"
              step="5"
            />
          </div>

          <div className="form-group">
            <label htmlFor="interestRate">Interest Rate (%)</label>
            <input
              type="number"
              id="interestRate"
              name="interestRate"
              value={formData.interestRate}
              onChange={handleChange}
              min="0"
              max="20"
              step="0.1"
            />
          </div>

          <div className="form-group">
            <label htmlFor="loanTermYears">Loan Term (years)</label>
            <input
              type="number"
              id="loanTermYears"
              name="loanTermYears"
              value={formData.loanTermYears}
              onChange={handleChange}
              min="5"
              max="30"
              step="5"
            />
          </div>

          <div className="form-group">
            <label htmlFor="propertyTaxRate">Property Tax Rate (%)</label>
            <input
              type="number"
              id="propertyTaxRate"
              name="propertyTaxRate"
              value={formData.propertyTaxRate}
              onChange={handleChange}
              min="0"
              max="5"
              step="0.05"
            />
            <small>Default: 1.25% for SF</small>
          </div>

          <div className="form-group">
            <label htmlFor="insuranceMonthly">Insurance ($/month)</label>
            <input
              type="number"
              id="insuranceMonthly"
              name="insuranceMonthly"
              value={formData.insuranceMonthly}
              onChange={handleChange}
              min="0"
              max="1000"
              step="10"
            />
          </div>

          <div className="form-group">
            <label htmlFor="utilitiesMonthly">Utilities ($/month)</label>
            <input
              type="number"
              id="utilitiesMonthly"
              name="utilitiesMonthly"
              value={formData.utilitiesMonthly}
              onChange={handleChange}
              min="0"
              max="1000"
              step="10"
            />
          </div>

          <div className="form-group">
            <label htmlFor="hoaMonthly">HOA dues ($/month)</label>
            <input id="hoaMonthly" name="hoaMonthly" type="number" min="0" max="100000" step="1"
              value={formData.hoaMonthly} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="maintenancePercent">Maintenance (% of rent)</label>
            <input
              type="number"
              id="maintenancePercent"
              name="maintenancePercent"
              value={formData.maintenancePercent}
              onChange={handleChange}
              min="0"
              max="10"
              step="0.5"
            />
          </div>

          <div className="form-group">
            <label htmlFor="propertyManagementPercent">Property Mgmt (%)</label>
            <input
              type="number"
              id="propertyManagementPercent"
              name="propertyManagementPercent"
              value={formData.propertyManagementPercent}
              onChange={handleChange}
              min="0"
              max="20"
              step="1"
            />
          </div>

          <div className="form-group">
            <label htmlFor="vacancyRate">Vacancy Rate (%)</label>
            <input
              type="number"
              id="vacancyRate"
              name="vacancyRate"
              value={formData.vacancyRate}
              onChange={handleChange}
              min="0"
              max="20"
              step="1"
            />
          </div>
        </div>
        
        <small>Fill in purchase details to see cash flow analysis and investment recommendation</small>
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
