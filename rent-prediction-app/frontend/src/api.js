import axios from 'axios';

const defaultApiUrl = process.env.NODE_ENV === 'production'
  ? 'https://san-francisco-rent-and-roi-predictor-production.up.railway.app'
  : '';

const api = axios.create({
  baseURL: (process.env.REACT_APP_API_URL ?? defaultApiUrl).replace(/\/$/, ''),
  timeout: 20000,
});

export default api;
