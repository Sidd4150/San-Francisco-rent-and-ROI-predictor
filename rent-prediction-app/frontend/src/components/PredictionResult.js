import React from 'react';

const PredictionResult = ({ prediction }) => {
  if (!prediction) return null;

  const { estimated_rent, confidence_range, input_features } = prediction;
  
  // Calculate ROI metrics if purchase price is provided
  const purchasePrice = input_features.purchasePrice ? parseFloat(input_features.purchasePrice) : null;
  const monthlyRent = estimated_rent;
  const annualRent = monthlyRent * 12;
  const grossRentalYield = purchasePrice ? ((annualRent / purchasePrice) * 100) : null;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="prediction-result">
      <h2>Rent Prediction Results</h2>
      
      <div className="result-main">
        <div className="estimated-rent">
          <h3>Estimated Monthly Rent</h3>
          <div className="rent-amount">{formatCurrency(estimated_rent)}</div>
        </div>
        
        <div className="confidence-range">
          <h4>Confidence Range</h4>
          <div className="range">
            <span className="lower">{formatCurrency(confidence_range.lower)}</span>
            <span className="separator">-</span>
            <span className="upper">{formatCurrency(confidence_range.upper)}</span>
          </div>
        </div>
      </div>

      {/* ROI Analysis Section */}
      {grossRentalYield && (
        <div className="roi-analysis">
          <h3>Investment Analysis</h3>
          <div className="roi-metrics">
            <div className="roi-card">
              <h4>Gross Rental Yield</h4>
              <div className="roi-percentage">{grossRentalYield.toFixed(2)}%</div>
              <p>Annual return on investment</p>
            </div>
            <div className="roi-card">
              <h4>Annual Rental Income</h4>
              <div className="roi-amount">{formatCurrency(annualRent)}</div>
              <p>Monthly rent × 12 months</p>
            </div>
          </div>
          
          <div className="investment-summary">
            <h4>Investment Summary</h4>
            <ul>
              <li><strong>Purchase Price:</strong> {formatCurrency(purchasePrice)}</li>
              <li><strong>Monthly Rental Income:</strong> {formatCurrency(monthlyRent)}</li>
              <li><strong>Annual Rental Income:</strong> {formatCurrency(annualRent)}</li>
              <li><strong>Gross Rental Yield:</strong> {grossRentalYield.toFixed(2)}%</li>
              <li><strong>Payback Period:</strong> {(purchasePrice / annualRent).toFixed(1)} years</li>
            </ul>
            
            <div className="roi-interpretation">
              {grossRentalYield >= 8 && (
                <p className="roi-excellent">🟢 <strong>Excellent ROI:</strong> This property shows strong rental yield potential!</p>
              )}
              {grossRentalYield >= 5 && grossRentalYield < 8 && (
                <p className="roi-good">🟡 <strong>Good ROI:</strong> Decent rental yield for San Francisco market.</p>
              )}
              {grossRentalYield < 5 && (
                <p className="roi-poor">🔴 <strong>Low ROI:</strong> Consider negotiating price or looking at other properties.</p>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="property-summary">
        <h4>Property Details</h4>
        <ul>
          <li><strong>Bedrooms:</strong> {input_features.beds}</li>
          <li><strong>Bathrooms:</strong> {input_features.baths}</li>
          <li><strong>Square Footage:</strong> {input_features.footage.toLocaleString()} sq ft</li>
          <li><strong>Location:</strong> ({input_features.latitude.toFixed(4)}, {input_features.longitude.toFixed(4)})</li>
          {purchasePrice && <li><strong>Purchase Price:</strong> {formatCurrency(purchasePrice)}</li>}
        </ul>
      </div>

      <div className="additional-info">
        <p className="note">
          * This prediction is based on machine learning analysis of San Francisco rental data.
          Actual rents may vary based on additional factors like amenities, condition, and market timing.
        </p>
      </div>
    </div>
  );
};

export default PredictionResult;