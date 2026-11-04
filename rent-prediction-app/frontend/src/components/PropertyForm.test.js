import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import PropertyForm from './PropertyForm';

jest.mock('../api', () => ({ post: jest.fn() }));

test('retains investment defaults and edits when map coordinates change', () => {
  const initialData = { beds: 2, baths: 1, footage: 1000, latitude: 37.7749, longitude: -122.4194 };
  const onSubmit = jest.fn();
  const { rerender } = render(<PropertyForm initialData={initialData} onSubmit={onSubmit} />);
  expect(screen.getByLabelText('Down Payment (%)').value).toBe('20');
  fireEvent.change(screen.getByLabelText('Insurance ($/month)'), { target: { value: '350' } });
  rerender(<PropertyForm initialData={{ ...initialData, latitude: 37.78 }} onSubmit={onSubmit} />);
  expect(screen.getByLabelText('Insurance ($/month)').value).toBe('350');
  fireEvent.submit(screen.getByText('Predict Rent & ROI').closest('form'));
  expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ latitude: 37.78, insuranceMonthly: 350, downPaymentPercent: 20 }));
});
