"""Reproducible, block-separated evaluation on real recent-tenancy records."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from threadpoolctl import threadpool_limits

from rental_features import BASE_FEATURES, CATEGORICAL_FEATURES, NUMERIC_FEATURES, OPTIONAL_FEATURES, feature_frame

ROOT = Path(__file__).resolve().parent
DATA, MODELS = ROOT / 'data', ROOT / 'models'


def split_groups(frame, fraction, seed):
    first, second = next(GroupShuffleSplit(n_splits=1, test_size=fraction, random_state=seed).split(frame, groups=frame.block))
    return frame.iloc[first].copy(), frame.iloc[second].copy()


def pipeline(estimator, basic=False):
    numeric = BASE_FEATURES if basic else NUMERIC_FEATURES
    columns = [('numbers', SimpleImputer(strategy='median', add_indicator=True), numeric)]
    if not basic:
        columns.append(('neighborhood', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES))
    return Pipeline([('features', ColumnTransformer(columns)), ('regressor', estimator)])


def hidden_optional(frame):
    result = frame.copy()
    result[OPTIONAL_FEATURES] = np.nan
    return feature_frame(result)


def augment(frame):
    # Teach the model how to handle unknown optional inputs without treating them
    # as 'no'. This uses only the fit partition, never validation/calibration/test.
    missing = frame.copy()
    missing[OPTIONAL_FEATURES] = np.nan
    return pd.concat([feature_frame(frame), feature_frame(missing)], ignore_index=True), np.tile(frame.rent.to_numpy(), 2)


def metrics(y, predicted):
    y, predicted = np.asarray(y), np.asarray(predicted)
    return dict(mae=round(float(mean_absolute_error(y, predicted)), 2),
                rmse=round(float(np.sqrt(mean_squared_error(y, predicted))), 2),
                r2=round(float(r2_score(y, predicted)), 4),
                median_absolute_error=round(float(np.median(np.abs(y - predicted))), 2),
                within_500_pct=round(float(np.mean(np.abs(y - predicted) <= 500) * 100), 2),
                n=len(y))


def conformal_radius(residuals, coverage=0.8):
    rank = min(len(residuals), int(np.ceil((len(residuals) + 1) * coverage)))
    return float(np.sort(np.asarray(residuals))[rank - 1])


def main():
    provenance = json.loads((DATA / 'provenance.json').read_text())
    path = DATA / 'recent_tenancies.csv.gz'
    if hashlib.sha256(path.read_bytes()).hexdigest() != provenance['sha256']:
        raise RuntimeError('Data checksum differs from the documented snapshot')
    frame = pd.read_csv(path, dtype={'block': str, 'recordId': str})
    # No blocks, and therefore no buildings or repeated units, cross partitions.
    development, heldout = split_groups(frame, .2, 42)
    development = development[development.tenancyYear == 2025]
    test = heldout[heldout.tenancyYear == 2026]
    historical_test = heldout[heldout.tenancyYear == 2025]
    fit_val, calibration = split_groups(development, .2, 43)
    fit, validation = split_groups(fit_val, .2, 44)
    partitions = {'fit': fit, 'validation': validation, 'calibration': calibration, 'test_2026': test}
    for name, part in partitions.items():
        if len(part) < 100:
            raise RuntimeError(f'Insufficient observations in {name}')
    names = list(partitions)
    for index, name in enumerate(names):
        for other in names[index + 1:]:
            assert set(partitions[name].block).isdisjoint(partitions[other].block)
    candidates = {
        'hist_gradient_boosting': HistGradientBoostingRegressor(loss='absolute_error', max_iter=250, max_leaf_nodes=15, min_samples_leaf=30, l2_regularization=10, learning_rate=.06, random_state=42),
        'gradient_boosting': GradientBoostingRegressor(loss='absolute_error', n_estimators=220, max_depth=3, min_samples_leaf=25, learning_rate=.05, random_state=42),
        'extra_trees': ExtraTreesRegressor(n_estimators=250, min_samples_leaf=5, max_features=.85, random_state=42, n_jobs=1),
    }
    validation_scores = {}
    fit_x, fit_y = augment(fit)
    for name, estimator in candidates.items():
        model = pipeline(clone(estimator))
        model.fit(fit_x, fit_y)
        full = mean_absolute_error(validation.rent, model.predict(feature_frame(validation)))
        unknown = mean_absolute_error(validation.rent, model.predict(hidden_optional(validation)))
        validation_scores[name] = {'mae': round(float(full), 2), 'unknown_optional_mae': round(float(unknown), 2), 'selection_score': float((full + unknown) / 2)}
        print(name, validation_scores[name], flush=True)
    winner = min(validation_scores, key=lambda name: validation_scores[name]['selection_score'])
    final = pipeline(clone(candidates[winner]))
    final_x, final_y = augment(fit_val)
    final.fit(final_x, final_y)
    # Select the strongest five-feature baseline on validation, independently of
    # the test set, using the same candidate families and final fit rows.
    basic_scores = {}
    for name, estimator in candidates.items():
        basic = pipeline(clone(estimator), basic=True)
        basic.fit(feature_frame(fit), fit.rent)
        basic_scores[name] = float(mean_absolute_error(validation.rent, basic.predict(feature_frame(validation))))
    baseline_name = min(basic_scores, key=basic_scores.get)
    baseline = pipeline(clone(candidates[baseline_name]), basic=True)
    baseline.fit(feature_frame(fit_val), fit_val.rent)
    dummy = DummyRegressor(strategy='median').fit(feature_frame(fit_val), fit_val.rent)
    predicted = final.predict(feature_frame(test))
    unknown_predicted = final.predict(hidden_optional(test))
    residuals = np.abs(calibration.rent.to_numpy() - final.predict(feature_frame(calibration)))
    unknown_residuals = np.abs(calibration.rent.to_numpy() - final.predict(hidden_optional(calibration)))
    radius = conformal_radius(residuals)
    unknown_radius = conformal_radius(unknown_residuals)
    # Unknown-optional requests get the more conservative independently measured radius.
    unknown_radius = max(radius, unknown_radius)
    test_metrics = metrics(test.rent, predicted)
    baseline_metrics = metrics(test.rent, baseline.predict(feature_frame(test)))
    test_metrics['interval_coverage_pct'] = round(float(np.mean(np.abs(test.rent - predicted) <= radius) * 100), 2)
    unknown_metrics = metrics(test.rent, unknown_predicted)
    unknown_metrics['interval_coverage_pct'] = round(float(np.mean(np.abs(test.rent - unknown_predicted) <= unknown_radius) * 100), 2)
    by_bedroom = {str(int(beds)): metrics(part.rent, final.predict(feature_frame(part))) for beds, part in test.groupby('beds') if len(part) >= 20}
    locations = frame[['latitude', 'longitude', 'neighborhood']].drop_duplicates().sort_values(['latitude', 'longitude', 'neighborhood']).to_dict('records')
    report = dict(version='recent-tenancies-v1', trained_at=datetime.now(timezone.utc).isoformat(),
                  model=winner, target='Reported monthly rent band midpoint for recent tenancies',
                  data=provenance, features=list(final_x.columns),
                  validation_candidates=validation_scores, baseline_validation_mae=basic_scores,
                  split=dict(method='Disjoint city blocks; train/validation/calibration use 2025 tenancies; final test uses 2026 tenancies in unseen blocks.', seed=42,
                             counts={name: {'rows': len(part), 'blocks': int(part.block.nunique())} for name, part in partitions.items()},
                             final_fit_rows=len(fit_val), final_fit_blocks=int(fit_val.block.nunique()),
                             unused_2026_development_rows=int(((frame.tenancyYear == 2026) & ~frame.block.isin(heldout.block)).sum()),
                             block_overlap=0),
                  test=test_metrics, five_feature_baseline=dict(model=baseline_name, **baseline_metrics),
                  median_baseline=metrics(test.rent, dummy.predict(feature_frame(test))),
                  unknown_optional_test=unknown_metrics,
                  historical_unseen_block_test=metrics(historical_test.rent, final.predict(feature_frame(historical_test))),
                  improvement_over_five_features_pct=round((baseline_metrics['mae'] - test_metrics['mae']) / baseline_metrics['mae'] * 100, 2),
                  by_bedroom=by_bedroom,
                  interval=dict(nominal_coverage=.8, radius=round(radius, 2), unknown_optional_radius=round(unknown_radius, 2),
                                method='Split-conformal absolute residual quantile, using the reserved 2025 calibration blocks.',
                                limitation='Nominal coverage assumes exchangeability; temporal drift and source bias can reduce coverage.'),
                  feature_support={field: {'min': float(frame[field].min()), 'max': float(frame[field].max())} for field in BASE_FEATURES},
                  limitations=provenance['limitations'] + ['Unverified owner reports can contain errors. Subsidy status is unavailable.',
                      '2026 test errors are measured against band midpoints, not exact lease rents.',
                      'The legacy model has unknown training provenance, so it is not treated as a clean held-out baseline.',
                      'Neighborhood is inferred from the nearest published block location, not an exact parcel lookup.'])
    # Save only after evaluation succeeds; no test rows are used in fitting.
    MODELS.mkdir(exist_ok=True)
    bundle = dict(pipeline=final, report=report, locations=locations, calibration_radius=radius,
                  unknown_optional_radius=unknown_radius, bedroom_counts={str(int(k)): int(v) for k, v in fit_val.beds.value_counts().items()})
    joblib.dump(bundle, MODELS / 'rental_model.joblib', compress=3)
    (MODELS / 'evaluation.json').write_text(json.dumps(report, indent=2) + '\n')
    # Store split membership for audits, never distribute original tenant identifiers in API responses.
    audit = pd.concat([part.assign(partition=name)[['recordId', 'block', 'tenancyYear', 'partition']] for name, part in partitions.items()])
    audit.to_csv(DATA / 'evaluation_splits.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})
    print(json.dumps({key: report[key] for key in ['model', 'split', 'test', 'five_feature_baseline', 'improvement_over_five_features_pct', 'interval']}, indent=2), flush=True)


if __name__ == '__main__':
    with threadpool_limits(limits=1):
        main()
