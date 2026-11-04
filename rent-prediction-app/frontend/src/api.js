import axios from 'axios';
import { normalizeApiUrl } from './apiConfig';

const defaultApiUrl = process.env.NODE_ENV === 'production'
  ? 'https://san-francisco-rent-and-roi-predictor-production.up.railway.app'
  : '';

const api = axios.create({
  baseURL: normalizeApiUrl(process.env.REACT_APP_API_URL || defaultApiUrl),
  timeout: 20000,
});

export default api;
