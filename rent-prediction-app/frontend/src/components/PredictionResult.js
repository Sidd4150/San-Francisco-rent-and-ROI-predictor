import React from 'react';
import { isValidPrediction } from '../prediction';

const PredictionResult = ({ prediction }) => {
  if (!prediction) return null;
  if (!isValidPrediction(prediction)) {
    return <p role="alert">Unable to display this prediction. Please try again.</p>;
  }

  const { estimated_rent, input_features, prediction_interval, model_info, market_context, warnings = [] } = prediction;
  
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
    const hoaMonthly = input_features.hoaMonthly ?? 0;
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
                                 utilities + hoaMonthly + maintenance + propertyManagement + vacancyLoss;
    
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
      hoaMonthly,
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
      isGoodInvestment: netMonthlyCashFlow > 0,
      cashFlowAtRent: rent => rent * (1 - (maintenancePercent + propertyManagementPercent + vacancyRate) / 100) -
        (monthlyMortgage + propertyTax + insurance + utilities + hoaMonthly),
      breakEvenRent: (maintenancePercent + propertyManagementPercent + vacancyRate) < 100
        ? (monthlyMortgage + propertyTax + insurance + utilities + hoaMonthly) /
          (1 - (maintenancePercent + propertyManagementPercent + vacancyRate) / 100)
        : null
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
          <p>Recent-tenancy benchmark · reported rent bands</p>
        </div>
        {prediction_interval && (
          <div className="confidence-range">
            <h4>Calibration range</h4>
            <div className="range">{formatCurrency(prediction_interval.lower)}–{formatCurrency(prediction_interval.upper)}</div>
            <p>The {prediction_interval.unknown_details ? 'unknown-details' : 'standard'} range contained {prediction_interval.observed_test_coverage_pct}% of
              reported rent midpoints in the 2026 test set. Partially missing inputs may behave differently.</p>
            <small>{prediction_interval.note}</small>
          </div>
        )}
      </div>

      {warnings.length > 0 && <aside className="prediction-warnings"><ul>{warnings.map(warning => <li key={warning}>{warning}</li>)}</ul></aside>}

      {model_info?.validation && (
        <details className="model-evidence">
          <summary>Data quality &amp; measured model performance</summary>
          <p>Mean absolute error: <strong>{formatCurrency(model_info.validation.mae)}/month</strong> on {model_info.validation.n} tenancies
            begun in 2026, on city blocks excluded from training. Errors are measured against reported $250 rent-band midpoints.</p>
          <p>The richer model reduced test error by {model_info.improvement_over_five_features_pct}% compared with a newly trained
            five-feature baseline ({formatCurrency(model_info.five_feature_baseline.mae)}/month).</p>
          <p>{model_info.usable_records.toLocaleString()} usable reports · data as of {model_info.data_as_of.slice(0, 10)}.</p>
          <ul>{model_info.limitations.map(note => <li key={note}>{note}</li>)}</ul>
          <a href={model_info.source_url} target="_blank" rel="noreferrer">Original San Francisco Rent Board data</a>
        </details>
      )}

      {market_context && (
        <aside className="market-context">
          <h3>Citywide asking-rent context</h3>
          <p>Zillow’s San Francisco rent index: <strong>{formatCurrency(market_context.latest.rent)}/month</strong> ({market_context.latest.date.slice(0, 7)}).</p>
          <p>{market_context.note} Its all-home mix differs from this property and from occupied-rent reports.</p>
          <a href={market_context.source_url} target="_blank" rel="noreferrer">{market_context.attribution}</a>
        </aside>
      )}

      {/* ROI Analysis Section */}
      {grossRentalYield && (
        <div className="roi-analysis">
          <h3>Investment Analysis</h3>
          <div className="roi-metrics">
            <div className="roi-card">
              <h4>Gross Rental Yield</h4>
              <div className="roi-percentage">{grossRentalYield.toFixed(2)}%</div>
              <p>Annual gross rent / purchase price</p>
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
              <h2>{cashFlowAnalysis.isGoodInvestment ? 'Positive estimated cash flow' : 'Negative estimated cash flow'}</h2>
              
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
                  ? `Estimated surplus of ${formatCurrency(cashFlowAnalysis.netMonthlyCashFlow)} per month under these assumptions.`
                  : `Estimated shortfall of ${formatCurrency(Math.abs(cashFlowAnalysis.netMonthlyCashFlow))} per month under these assumptions.`}
              </p>
              <p>Excludes closing costs, major repairs, income taxes and appreciation.</p>
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
                <li><span>HOA dues</span><span className="negative">{formatCurrency(cashFlowAnalysis.hoaMonthly)}</span></li>
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

          <div className="rent-sensitivity">
            <h4>How much does rent uncertainty affect cash flow?</h4>
            {cashFlowAnalysis.breakEvenRent !== null && <p>Break-even monthly rent: <strong>{formatCurrency(cashFlowAnalysis.breakEvenRent)}</strong></p>}
            {prediction_interval && <>
              <p>At the lower rent estimate: <strong>{formatCurrency(cashFlowAnalysis.cashFlowAtRent(prediction_interval.lower))}/month</strong></p>
              <p>At the upper rent estimate: <strong>{formatCurrency(cashFlowAnalysis.cashFlowAtRent(prediction_interval.upper))}/month</strong></p>
            </>}
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
          {input_features.neighborhood && <li><strong>Inferred neighborhood:</strong> {input_features.neighborhood}</li>}
          {purchasePrice && <li><strong>Purchase Price:</strong> {formatCurrency(purchasePrice)}</li>}
        </ul>
      </div>

      <div className="additional-info">
        <p className="note">
          This estimate reflects owner-reported occupied rents for recent tenancies. It is not a quote for a new listing.
          Advertised rents, unit condition, parking, laundry, concessions and subsidy status can differ substantially.
        </p>
      </div>
    </div>
  );
};

export default PredictionResult;
