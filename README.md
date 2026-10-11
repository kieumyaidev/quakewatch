# QuakeWatch

Collects recent earthquakes from the USGS public API, stores them in a database, and lets users search them by place on a small web page.

## Data source

USGS GeoJSON feed (no API key needed): https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson

## Database

- `DATABASE_URL` selects the database. Default is SQLite (`sqlite:///quakewatch.db`). Postgres also works, e.g. `postgresql://user:pass@localhost:5432/quakewatch`.
- Schema migrations are plain SQL files in `migrations/`. `quakewatch/db.py` runs the ones not yet applied and records them in the `schema_migrations` table.

## Run locally

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python -m quakewatch.db          # run migrations
python -m quakewatch.collector   # fetch data from USGS and save it
python -m quakewatch.app         # web app on http://localhost:5000
```

Run tests:

```shell
python -m pytest
```

## Deploy

`render.yaml` deploys the app to Render (free tier) from the `Dockerfile`, with a free Render PostgreSQL database. Each time the container starts it runs the migrations, collects the feed once, then starts gunicorn. There is no schedule in this version; run `python -m quakewatch.collector` to collect again.
