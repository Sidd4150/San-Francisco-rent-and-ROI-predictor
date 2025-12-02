import React from 'react';

const PredictionResult = ({ prediction }) => {
  if (!prediction) return null;

  const { estimated_rent, input_features } = prediction;
  
  // Calculate ROI metrics if purchase price is provided
  const purchasePrice = input_features.purchasePrice ? parseFloat(input_features.purchasePrice) : null;
  const monthlyRent = estimated_rent;
  const annualRent = monthlyRent * 12;
  const grossRentalYield = purchasePrice ? ((annualRent / purchasePrice) * 100) : null;

  // Advanced cash flow calculations
  let cashFlowAnalysis = null;

  if (purchasePrice && input_features.downPaymentPercent !== undefined) {
    // Get values - use nullish coalescing (??) to allow 0 as a valid value
    const downPaymentPercent = input_features.downPaymentPercent ?? 20;
    const interestRate = input_features.interestRate ?? 7.0;
    const loanTermYears = input_features.loanTermYears ?? 30;
    const propertyTaxRate = input_features.propertyTaxRate ?? 1.25;
    const insuranceMonthly = input_features.insuranceMonthly ?? 0;
    const utilitiesMonthly = input_features.utilitiesMonthly ?? 0;
    const maintenancePercent = input_features.maintenancePercent ?? 0;
    const propertyManagementPercent = input_features.propertyManagementPercent ?? 0;
    const vacancyRate = input_features.vacancyRate ?? 0;

    // Calculate down payment and loan
    const downPayment = purchasePrice * (downPaymentPercent / 100);
    const loanAmount = purchasePrice - downPayment;

    // Monthly mortgage payment calculation (P&I) - standard amortization formula
    const monthlyRate = interestRate / 100 / 12;
    const numPayments = loanTermYears * 12;

    let monthlyMortgage = 0;
    if (loanAmount > 0 && monthlyRate > 0) {
      monthlyMortgage = (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
        (Math.pow(1 + monthlyRate, numPayments) - 1);
    } else if (loanAmount > 0) {
      monthlyMortgage = loanAmount / numPayments;
    }

    // Monthly expenses
    const propertyTax = (purchasePrice * (propertyTaxRate / 100)) / 12;
    const insurance = insuranceMonthly;
    const utilities = utilitiesMonthly;
    const maintenance = monthlyRent * (maintenancePercent / 100);
    const propertyManagement = monthlyRent * (propertyManagementPercent / 100);
    const vacancyLoss = monthlyRent * (vacancyRate / 100);
    
    // Total monthly expenses
    const totalMonthlyExpenses = monthlyMortgage + propertyTax + insurance + 
                                 utilities + maintenance + propertyManagement + vacancyLoss;
    
    // Net monthly cash flow
    const netMonthlyCashFlow = monthlyRent - totalMonthlyExpenses;
    
    // Cash-on-cash return - handle division by zero
    const annualCashFlow = netMonthlyCashFlow * 12;
    const cashOnCashReturn = downPayment > 0 ? (annualCashFlow / downPayment) * 100 : 0;
    
    cashFlowAnalysis = {
      downPayment,
      downPaymentPercent,
      loanAmount,
      interestRate,
      loanTermYears,
      monthlyMortgage,
      propertyTax,
      propertyTaxRate,
      insurance,
      utilities,
      maintenance,
      maintenancePercent,
      propertyManagement,
      propertyManagementPercent,
      vacancyLoss,
      vacancyRate,
      totalMonthlyExpenses,
      netMonthlyCashFlow,
      annualCashFlow,
      cashOnCashReturn,
      isGoodInvestment: netMonthlyCashFlow > 0
    };
  }

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
        </div>
      )}

      {/* Detailed Cash Flow Analysis */}
      {cashFlowAnalysis && (
        <div className="cash-flow-analysis">
          <h3>💸 Cash Flow Analysis</h3>
          
          <div className="cash-flow-summary">
            <div className={`investment-decision ${cashFlowAnalysis.isGoodInvestment ? 'positive' : 'negative'}`}>
              <h2>{cashFlowAnalysis.isGoodInvestment ? '✅ GOOD INVESTMENT' : '❌ POOR INVESTMENT'}</h2>
              
              <div className="monthly-comparison">
                <div className="comparison-item">
                  <span>Monthly Rental Income:</span>
                  <span className="positive">{formatCurrency(monthlyRent)}</span>
                </div>
                <div className="comparison-item">
                  <span>Monthly Total Cost:</span>
                  <span className="negative">-{formatCurrency(cashFlowAnalysis.totalMonthlyExpenses)}</span>
                </div>
                <div className="comparison-item net-result">
                  <span>Net Monthly Cash Flow:</span>
                  <span className={cashFlowAnalysis.netMonthlyCashFlow >= 0 ? 'positive' : 'negative'}>
                    {cashFlowAnalysis.netMonthlyCashFlow >= 0 ? '+' : '-'}{formatCurrency(Math.abs(cashFlowAnalysis.netMonthlyCashFlow))}
                  </span>
                </div>
              </div>
              
              <p className="recommendation">
                {cashFlowAnalysis.isGoodInvestment 
                  ? `You'll make ${formatCurrency(cashFlowAnalysis.netMonthlyCashFlow)} profit per month. This property is worth renting out!`
                  : `You'll lose ${formatCurrency(Math.abs(cashFlowAnalysis.netMonthlyCashFlow))} per month. Not recommended as a rental investment.`}
              </p>
            </div>
          </div>

          <div className="cash-flow-breakdown">
            <div className="income-section">
              <h4>💰 Monthly Income</h4>
              <ul>
                <li>
                  <span>Rental Income</span>
                  <span className="positive">{formatCurrency(monthlyRent)}</span>
                </li>
              </ul>
              <div className="total">
                <span>Total Income</span>
                <span className="positive">{formatCurrency(monthlyRent)}</span>
              </div>
            </div>

            <div className="expense-section">
              <h4>💸 Monthly Expenses</h4>
              <ul>
                <li>
                  <span>Mortgage (P&I)</span>
                  <span className="negative">{formatCurrency(cashFlowAnalysis.monthlyMortgage)}</span>
                </li>
                <li>
                  <span>Property Tax</span>
                  <span className="negative">{formatCurrency(cashFlowAnalysis.propertyTax)}</span>
                </li>
                <li>
                  <span>Insurance</span>
                  <span className="negative">{formatCurrency(cashFlowAnalysis.insurance)}</span>
                </li>
                <li>
                  <span>Utilities</span>
                  <span className="negative">{formatCurrency(cashFlowAnalysis.utilities)}</span>
                </li>
                <li>
                  <span>Maintenance ({cashFlowAnalysis.maintenancePercent}%)</span>
                  <span className="negative">{formatCurrency(cashFlowAnalysis.maintenance)}</span>
                </li>
                <li>
                  <span>Property Management ({cashFlowAnalysis.propertyManagementPercent}%)</span>
                  <span className="negative">{formatCurrency(cashFlowAnalysis.propertyManagement)}</span>
                </li>
                <li>
                  <span>Vacancy Loss ({cashFlowAnalysis.vacancyRate}%)</span>
                  <span className="negative">{formatCurrency(cashFlowAnalysis.vacancyLoss)}</span>
                </li>
              </ul>
              <div className="total">
                <span>Total Expenses</span>
                <span className="negative">{formatCurrency(cashFlowAnalysis.totalMonthlyExpenses)}</span>
              </div>
            </div>
          </div>

          <div className="roi-metrics advanced">
            <div className="roi-card">
              <h4>Cash-on-Cash Return</h4>
              <div className={`roi-percentage ${cashFlowAnalysis.cashOnCashReturn >= 0 ? 'positive' : 'negative'}`}>
                {cashFlowAnalysis.downPayment > 0
                  ? `${cashFlowAnalysis.cashOnCashReturn.toFixed(2)}%`
                  : 'N/A'}
              </div>
              <p>{cashFlowAnalysis.downPayment > 0
                ? `Return on ${formatCurrency(cashFlowAnalysis.downPayment)} down`
                : 'No down payment'}</p>
            </div>
            <div className="roi-card">
              <h4>Annual Cash Flow</h4>
              <div className={`roi-amount ${cashFlowAnalysis.annualCashFlow >= 0 ? 'positive' : 'negative'}`}>
                {cashFlowAnalysis.annualCashFlow >= 0 ? '+' : '-'}{formatCurrency(Math.abs(cashFlowAnalysis.annualCashFlow))}
              </div>
              <p>{cashFlowAnalysis.annualCashFlow >= 0 ? 'Annual profit' : 'Annual loss'}</p>
            </div>
          </div>

          <div className="investment-details">
            <h4>Investment Details</h4>
            <ul>
              <li><strong>Purchase Price:</strong> {formatCurrency(purchasePrice)}</li>
              <li><strong>Down Payment ({cashFlowAnalysis.downPaymentPercent}%):</strong> {formatCurrency(cashFlowAnalysis.downPayment)}</li>
              <li><strong>Loan Amount:</strong> {formatCurrency(cashFlowAnalysis.loanAmount)}</li>
              <li><strong>Interest Rate:</strong> {cashFlowAnalysis.interestRate}%</li>
              <li><strong>Loan Term:</strong> {cashFlowAnalysis.loanTermYears} years</li>
            </ul>
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