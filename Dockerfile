FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PORT=8000
CMD python -m quakewatch.db && (python -m quakewatch.collector || true) && gunicorn --bind 0.0.0.0:$PORT "quakewatch.app:create_app()"
