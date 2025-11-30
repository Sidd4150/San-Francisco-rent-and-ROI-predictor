# SF Rent Prediction Backend

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Train the model (or use existing model):
```bash
python train_model.py
```

4. Run the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

## API Endpoints

- `POST /predict` - Predict rent for a property
- `GET /health` - Check API health
- `GET /docs` - Interactive API documentation