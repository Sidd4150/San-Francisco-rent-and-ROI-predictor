import hashlib
import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from prepare_data import closed_band, prepare
from rental_features import feature_frame
from train_model import conformal_radius

ROOT = Path(__file__).resolve().parent


class ModelQualityTests(unittest.TestCase):
    def test_band_parser_never_invents_midpoints_for_open_ended_rents(self):
        self.assertEqual(closed_band('$2751-$3000'), (2751, 3000))
        self.assertEqual(closed_band('501-750 Sq.Ft'), (501, 750))
        for value in ('$7000+', '4000+ Sq.Ft', 'Unknown', '$0 (no rent paid by the occupant)'):
            self.assertIsNone(closed_band(value))

    def test_features_use_same_area_bins_and_never_use_target(self):
        rows = [dict(beds=2, baths=1, footage=1000, latitude=37.77, longitude=-122.42, rent=5000)]
        features = feature_frame(rows)
        self.assertEqual(features.iloc[0].footage, 875.5)
        self.assertNotIn('rent', features.columns)
        self.assertTrue(np.isnan(features.iloc[0].waterIncluded))

    def test_snapshot_matches_documented_checksum_and_disjoint_blocks(self):
        metadata = json.loads((ROOT / 'data/provenance.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT / 'data/recent_tenancies.csv.gz').read_bytes()).hexdigest(), metadata['sha256'])
        splits = pd.read_csv(ROOT / 'data/evaluation_splits.csv.gz', dtype={'block': str})
        self.assertEqual(splits.groupby('block').partition.nunique().max(), 1)
        self.assertTrue((splits[splits.partition == 'test_2026'].tenancyYear == 2026).all())
        self.assertTrue((splits[splits.partition != 'test_2026'].tenancyYear == 2025).all())

    def test_conformal_rank_uses_finite_sample_correction(self):
        self.assertEqual(conformal_radius([1, 2, 3, 4, 5], .8), 5)


if __name__ == '__main__':
    unittest.main()
