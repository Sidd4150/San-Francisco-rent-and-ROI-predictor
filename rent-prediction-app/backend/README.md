# Rent prediction backend

This service runs Flask, not the legacy FastAPI entry point.

```sh
pip install -r requirements.txt
python real_model_api.py
```

Production entry point: `gunicorn real_model_api:app`, bound to Railway's `PORT`.
The evaluated artifact is `models/rental_model.joblib`. Keep `rental_features.py`
and `data/market_context.json` alongside the service. `/model-info` publishes the
model's measured performance and source limitations.

Run `python train_model.py` to reproduce training on the included data snapshot.
Run `python prepare_data.py` to refresh the documented official data cohort first.
Neither command uses synthetic training data. `train_model_simple.py`, `main.py`
and `simple_api.py` are legacy demonstration code and are not production entry
points. See the [root README](../../README.md) for evaluation design and setup.
