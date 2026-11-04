import { normalizeApiUrl } from './apiConfig';

test.each([
  ['san-francisco-rent-and-roi-predictor-production.up.railway.app', 'https://san-francisco-rent-and-roi-predictor-production.up.railway.app'],
  [' https://backend.example/ ', 'https://backend.example'],
  ['http://localhost:8000/', 'http://localhost:8000'],
  ['/', ''],
  ['', ''],
  ['/api/', '/api'],
])('normalizes API setting %s', (setting, expected) => {
  expect(normalizeApiUrl(setting)).toBe(expected);
});
