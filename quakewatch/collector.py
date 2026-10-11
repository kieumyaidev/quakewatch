from dataclasses import dataclass
from datetime import datetime, timezone

import requests
from sqlalchemy import Engine, text

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"


@dataclass
class Earthquake:
    id: str
    magnitude: float | None
    place: str | None
    occurred_at: datetime
    longitude: float
    latitude: float
    depth_km: float | None
    url: str | None


def fetch_earthquakes(url: str = FEED_URL) -> list[Earthquake]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return [parse_feature(f) for f in response.json()["features"]]


def parse_feature(feature: dict) -> Earthquake:
    props = feature["properties"]
    longitude, latitude, depth = feature["geometry"]["coordinates"]
    return Earthquake(
        id=feature["id"],
        magnitude=props.get("mag"),
        place=props.get("place"),
        occurred_at=datetime.fromtimestamp(props["time"] / 1000, tz=timezone.utc).replace(tzinfo=None),
        longitude=longitude,
        latitude=latitude,
        depth_km=depth,
        url=props.get("url"),
    )


def save_earthquakes(engine: Engine, earthquakes: list[Earthquake]) -> int:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    new_rows = 0
    with engine.begin() as conn:
        for quake in earthquakes:
            values = {**quake.__dict__, "collected_at": now}
            exists = conn.execute(text("SELECT 1 FROM earthquakes WHERE id = :id"), {"id": quake.id}).first()
            if exists:
                conn.execute(text(
                    "UPDATE earthquakes SET magnitude = :magnitude, place = :place, occurred_at = :occurred_at, "
                    "longitude = :longitude, latitude = :latitude, depth_km = :depth_km, url = :url, "
                    "collected_at = :collected_at WHERE id = :id"
                ), values)
            else:
                conn.execute(text(
                    "INSERT INTO earthquakes (id, magnitude, place, occurred_at, longitude, latitude, depth_km, url, collected_at) "
                    "VALUES (:id, :magnitude, :place, :occurred_at, :longitude, :latitude, :depth_km, :url, :collected_at)"
                ), values)
                new_rows += 1
    return new_rows


def collect(engine: Engine, url: str = FEED_URL) -> int:
    earthquakes = fetch_earthquakes(url)
    new_rows = save_earthquakes(engine, earthquakes)
    print(f"fetched {len(earthquakes)} earthquakes, {new_rows} new")
    return new_rows


if __name__ == "__main__":
    from quakewatch.db import build_engine, migrate

    engine = build_engine()
    migrate(engine)
    collect(engine)
