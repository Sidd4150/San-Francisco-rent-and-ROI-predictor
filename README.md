# San Francisco rent benchmark & cash-flow explorer

A deployed React + Flask application that estimates recent-tenancy rents using
San Francisco's official 2026 rental inventory. It combines property and building
features with measured model error, a calibration range, and cash-flow scenarios.

**Website:** https://sf-rent-and-roi-predictor.up.railway.app/

## What the estimate means

The target is **owner-reported occupied monthly rent for tenancies begun in
2025–2026**, recorded in the 2026 inventory. It is not a quote for a new market
listing. The data can include subsidized tenancies and rent-regulated units;
subsidy status is unavailable. Rents are reported in $250 bands, floor area in
250-square-foot bands, and locations are anonymized to city blocks.

The application shows Zillow's citywide asking-rent index separately as context.
It does not multiply individual predictions by that index or claim validation on
advertised asking rents.

## Measured performance

The shipped model is a histogram gradient boosting regressor, selected using
validation data from three model families. Test records were not used for model
selection, fitting, or interval calibration.

| Evaluation on 433 tenancies begun in 2026, in 180 unseen blocks | MAE / month | RMSE / month | R² |
| --- | ---: | ---: | ---: |
| Richer model, available source features | $572.32 | $838.99 | 0.5522 |
| Independently selected five-feature baseline | $624.93 | $878.36 | 0.5092 |
| Richer model, optional building/utility details all unknown | $585.68 | $848.75 | 0.5417 |
| Training-set median baseline | $993.07 | $1,288.38 | -0.0560 |

The richer model reduces MAE by **8.42%** against the five-feature baseline on
this test set. Errors are against reported band midpoints, not exact lease rents.
These results replace the former unsupported “81.2% accuracy” claim. They are
not directly comparable to the legacy model's undocumented evaluation.

The standard range is calibrated for nominal 80% coverage using 3,208 reserved
2025 observations. It covered **72.06%** of the 2026 test midpoints: temporal drift
and dataset bias mean it must not be presented as a guaranteed 80% range. The API
also measures a separate range when all optional details are unknown. Partial
missingness may behave differently. Both ranges and their limitations are visible.

Full results, candidate scores, subgroup errors and exclusions:
[`evaluation.json`](rent-prediction-app/backend/models/evaluation.json).

## Data and features

Source: [San Francisco Rent Board Housing Inventory, DataSF](https://data.sf.gov/Housing-and-Buildings/Rent-Board-Housing-Inventory/gdc7-dmcn).
License: Open Data Commons Public Domain Dedication and License.
Snapshot: November 4, 2026; 23,141 recent-tenancy source records, **20,271 usable
records across 2,159 blocks**. The exact query, exclusions and SHA-256 checksum
are saved in [`provenance.json`](rent-prediction-app/backend/data/provenance.json).
The normalized compressed snapshot is included so training does not require a
live API or silently switch to synthetic data.

Inputs include bedrooms, bathrooms, floor area and location, plus:

- Building year and number of units.
- Inclusion of water/sewer, gas, electricity and garbage/recycling in rent.
- Neighborhood inferred from the nearest published block location.
- Derived building age, area per bedroom, and distances to downtown and Golden Gate Park.

Unknown utilities remain unknown, rather than being interpreted as “no.” Training
includes optional-feature masking to support incomplete user inputs. The model
does not invent parking, laundry or condition effects absent from this source.

Excluded: no-rent and unbounded $7,000+ rent records, unknown or unsupported floor
areas, shared bathrooms, missing geography and future/missing tenancy dates.
The model therefore underrepresents luxury homes. Bedrooms 5+ and bathrooms 3+
are grouped by the source. Supported floor area is 251–4,000 sq ft; larger
properties generate a data-support warning.

Market context: [Zillow Research, ZORI](https://www.zillow.com/research/data/).
Data provided by Zillow Group. The stored citywide series currently ends in
September 2026. Zillow terms apply; this is an aggregate rent index, not an
individual property valuation.

## Reproduce the model

Use Python 3.11. From the repository root:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r rent-prediction-app/backend/requirements.txt
# Refit and evaluate the included, checksum-verified snapshot:
python rent-prediction-app/backend/train_model.py
# Optional: refresh official data and market context before retraining:
python rent-prediction-app/backend/prepare_data.py
```

Refresh queries currently target the documented 2026 inventory and tenancies begun
in 2025–2026. Moving to a new reporting year requires deliberately updating the
cohort, feature-year reference and evaluation strategy, not just rerunning the
script indefinitely.

A fixed-seed group split keeps every city block in a single partition. Model
selection uses 8,682 training observations and 2,439 validation observations from
2025. The selected model is refit on those 11,121 observations. Calibration uses
3,208 other 2025 observations. The primary final test uses only 2026 tenancies
from the held-out blocks. Remaining 2026 development-block records are unused.
Split membership is included for audit. Public source record IDs are never sent
in prediction responses. The original model is retained only as a legacy artifact.

## Run locally

```sh
python rent-prediction-app/backend/real_model_api.py
```

In another terminal:

```sh
cd rent-prediction-app/frontend
npm ci
npm start
```

React development requests proxy to port 8000. Production defaults to the existing
Railway backend. `REACT_APP_API_URL` overrides it at build time; bare hostnames are
normalized to HTTPS. The root Docker build uses same-origin API requests.

## Tests

```sh
python -m unittest discover -s rent-prediction-app/backend -p 'test_deployment.py'
python -m unittest discover -s rent-prediction-app/backend -p 'test_model_quality.py'
cd rent-prediction-app/frontend
npm test -- --watchAll=false --runInBand
npm run build
```

Tests cover real model loading and predictions, input validation, optional-feature
handling, interval responses, data integrity, block separation, HTML-response
protection, form persistence, and API URL normalization.

## API

- `GET /health`: model readiness; 503 if the model fails to load.
- `GET /model-info`: evaluation report, provenance and market context.
- `POST /predict`: rent benchmark, calibration range, warnings and echoed inputs.
- `POST /geocode`: San Francisco street-address lookup.

Required prediction fields: `beds`, `baths`, `footage`, `latitude`, `longitude`.
Optional model fields: `yearBuilt`, `buildingUnits`, `waterIncluded`, `gasIncluded`,
`electricityIncluded`, `refuseIncluded`. Utility values are 1, 0, or unknown/null.

The investment explorer includes mortgage principal/interest, property tax,
insurance, owner-paid utilities, HOA dues, maintenance, management and vacancy.
It shows break-even rent and cash flow at the lower/upper rent estimates rather
than making a definitive good/bad investment recommendation. Closing costs,
major repairs, income taxes and appreciation are outside the calculation.

## Railway deployment

The existing GitHub-connected frontend and backend services deploy from `main`.
The backend runs `real_model_api:app`; install `requirements.txt` (the alternative
`requirements_flask.txt` delegates to it). Keep the evaluated model and feature
module together. No training or live-data downloads occur at application startup.

For a combined service, set Root Directory to `/`. Railway detects the root
Dockerfile, which builds React and starts Gunicorn on Railway's `PORT`. Remove old
build/start overrides for that combined deployment. `/health` is the readiness
check. The committed macOS virtual environment is not used by Docker.
