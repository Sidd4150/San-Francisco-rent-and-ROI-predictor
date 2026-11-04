"""Run with python -m unittest discover -s rent-prediction-app/backend -p test_deployment.py."""
import unittest
from unittest.mock import patch

import real_model_api as api


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.client = api.app.test_client()
        self.property = dict(beds=2, baths=1.5, footage=1200,
                             latitude=37.7749, longitude=-122.4194)

    def test_bundled_model_loads_and_predicts_from_repository_root(self):
        self.assertTrue(api.model_loaded)
        self.assertEqual(self.client.get('/health').status_code, 200)
        response = self.client.post('/predict', json=self.property)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json['estimated_rent'], 0)

    def test_missing_model_is_not_healthy(self):
        with patch.object(api, 'model_loaded', False):
            self.assertEqual(self.client.get('/health').status_code, 503)
            self.assertEqual(self.client.post('/predict', json=self.property).status_code, 503)

    def test_invalid_json_and_numbers_are_client_errors(self):
        for body in (None, [], {'beds': 'invalid'}, dict(self.property, footage=None)):
            self.assertEqual(self.client.post('/predict', json=body).status_code, 400)

    def test_investment_zero_values_are_preserved(self):
        response = self.client.post('/predict', json=dict(
            self.property, purchasePrice=795000, interestRate=0, insuranceMonthly=0))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['input_features']['interestRate'], 0)
        self.assertEqual(response.json['input_features']['insuranceMonthly'], 0)

    def test_geocoding_uses_timeout(self):
        with patch.object(api.requests, 'get') as get:
            get.return_value.status_code = 200
            get.return_value.json.return_value = [dict(lat='37.7749', lon='-122.4194')]
            response = self.client.post('/geocode', json={'address': '1 Market Street'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(get.call_args.kwargs['timeout'], 10)

    def test_optional_features_and_uncertainty_contract(self):
        complete = dict(self.property, yearBuilt=1963, buildingUnits=12,
                        waterIncluded=1, gasIncluded=0, electricityIncluded=0, refuseIncluded=1)
        response = self.client.post('/predict', json=complete)
        self.assertEqual(response.status_code, 200)
        result = response.json
        self.assertEqual(result['input_features']['waterIncluded'], 1)
        self.assertEqual(result['input_features']['gasIncluded'], 0)
        self.assertTrue(result['input_features']['neighborhood'])
        interval = result['prediction_interval']
        self.assertLess(interval['lower'], result['estimated_rent'])
        self.assertGreater(interval['upper'], result['estimated_rent'])
        self.assertFalse(interval['unknown_details'])
        unknown = self.client.post('/predict', json=self.property).json
        self.assertTrue(unknown['prediction_interval']['unknown_details'])
        self.assertGreaterEqual(unknown['prediction_interval']['upper'] - unknown['prediction_interval']['lower'],
                                interval['upper'] - interval['lower'] - .02)

    def test_nonfinite_and_unsupported_inputs_rejected(self):
        for field, value in [('footage', 10000), ('beds', float('nan')), ('baths', float('inf')),
                             ('yearBuilt', 2050), ('waterIncluded', 2), ('purchasePrice', -10),
                             ('loanTermYears', 0), ('hoaMonthly', -1)]:
            with self.subTest(field=field, value=value):
                self.assertEqual(self.client.post('/predict', json=dict(self.property, **{field: value})).status_code, 400)

    def test_model_info_exposes_measured_performance_and_provenance(self):
        response = self.client.get('/model-info')
        self.assertEqual(response.status_code, 200)
        report = response.json
        self.assertGreater(report['test']['n'], 100)
        self.assertGreater(report['test']['mae'], 0)
        self.assertEqual(report['split']['block_overlap'], 0)
        self.assertIn('Occupied', report['data']['query'])
        self.assertNotIn('accuracy', report)


if __name__ == '__main__':
    unittest.main()
