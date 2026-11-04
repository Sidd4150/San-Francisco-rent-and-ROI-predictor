export function normalizeApiUrl(value) {
  const url = value.trim().replace(/\/+$/, '');
  if (!url || url.startsWith('/')) return url;
  return /^https?:\/\//i.test(url) ? url : `https://${url}`;
}
