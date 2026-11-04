FROM node:22-bookworm-slim AS frontend
WORKDIR /frontend
COPY rent-prediction-app/frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY rent-prediction-app/frontend/ ./
RUN REACT_APP_API_URL=/ npm run build

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY rent-prediction-app/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY rent-prediction-app/backend/real_model_api.py ./backend/real_model_api.py
COPY rent-prediction-app/backend/models/ ./backend/models/
COPY --from=frontend /frontend/build ./frontend/build
CMD ["sh", "-c", "exec gunicorn --chdir /app/backend --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4 --timeout 60 --access-logfile - --error-logfile - real_model_api:app"]
