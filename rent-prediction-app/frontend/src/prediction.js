export function isValidPrediction(value) {
  return Boolean(value && Number.isFinite(value.estimated_rent) &&
    value.input_features &&
    ['beds', 'baths', 'footage', 'latitude', 'longitude'].every(
      field => Number.isFinite(value.input_features[field])
    ));
}
