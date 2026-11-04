import React from 'react';
import { render, screen } from '@testing-library/react';
import PredictionResult from './PredictionResult';

test('cash flow includes HOA and responds to the rent range', () => {
  render(<PredictionResult prediction={{ estimated_rent: 3000,
    input_features: { beds: 2, baths: 1, footage: 1000, latitude: 37.77, longitude: -122.42,
      purchasePrice: 100000, downPaymentPercent: 100, interestRate: 0, propertyTaxRate: 0,
      insuranceMonthly: 0, utilitiesMonthly: 0, hoaMonthly: 500, maintenancePercent: 0,
      propertyManagementPercent: 0, vacancyRate: 0 },
    prediction_interval: { lower: 2000, upper: 4000, observed_test_coverage_pct: 72.06 },
  }} />);
  expect(screen.getByText('Positive estimated cash flow')).toBeTruthy();
  expect(screen.getByText('Break-even monthly rent:').textContent).toContain('$500');
  expect(screen.getByText('At the lower rent estimate:').textContent).toContain('$1,500/month');
  expect(screen.getByText('At the upper rent estimate:').textContent).toContain('$3,500/month');
  expect(screen.getByText('HOA dues')).toBeTruthy();
});

test('an unexpected prediction cannot crash the results component', () => {
  render(<PredictionResult prediction={'<!doctype html>'} />);
  expect(screen.getByRole('alert').textContent).toMatch(/Unable to display/);
});
