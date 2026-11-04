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


if __name__ == '__main__':
    unittest.main()
