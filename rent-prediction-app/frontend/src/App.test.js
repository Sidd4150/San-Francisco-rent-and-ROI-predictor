import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import App from './App';
import api from './api';

jest.mock('./api', () => ({ post: jest.fn() }));
jest.mock('./components/MapView', () => () => <div>Map</div>);

test('HTML API responses show an error without crashing the app', async () => {
  api.post.mockResolvedValueOnce({ data: '<!doctype html><div id="root"></div>' });
  render(<App />);
  fireEvent.submit(screen.getByText('Predict Rent & ROI').closest('form'));
  expect(await screen.findByText(/prediction service returned an unexpected response/)).toBeTruthy();
  expect(screen.getByText('Predict Rent & ROI')).toBeTruthy();
});

test('valid API responses display rent and investment results', async () => {
  api.post.mockResolvedValueOnce({ data: {
    estimated_rent: 3385.19,
    input_features: { beds: 2, baths: 1.5, footage: 1200, latitude: 37.7749,
      longitude: -122.4194, purchasePrice: 795000, downPaymentPercent: 20 },
  } });
  render(<App />);
  fireEvent.submit(screen.getByText('Predict Rent & ROI').closest('form'));
  expect(await screen.findByText('Rent Prediction Results')).toBeTruthy();
  expect(screen.getByText('Gross Rental Yield')).toBeTruthy();
  expect(screen.getByText('Cash-on-Cash Return')).toBeTruthy();
});
