import responses
from sqlalchemy import text

from quakewatch.collector import FEED_URL, collect
from quakewatch.db import migrate

FEED = {
    "features": [
        {
            "id": "ak001",
            "properties": {"mag": 2.4, "place": "24 km ENE of Beluga, Alaska", "time": 1790789106395,
                           "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ak001"},
            "geometry": {"coordinates": [-150.6, 61.2, 49.3]},
        },
        {
            "id": "jp001",
            "properties": {"mag": 4.8, "place": "Off the coast of Japan", "time": 1790780000000, "url": None},
            "geometry": {"coordinates": [142.1, 38.3, 10.0]},
        },
    ]
}


@responses.activate
def test_collect_saves_earthquakes(engine):
    responses.get(FEED_URL, json=FEED)

    assert collect(engine) == 2

    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, magnitude, place FROM earthquakes ORDER BY id")).all()
    assert [tuple(r) for r in rows] == [
        ("ak001", 2.4, "24 km ENE of Beluga, Alaska"),
        ("jp001", 4.8, "Off the coast of Japan"),
    ]


@responses.activate
def test_collect_twice_does_not_duplicate(engine):
    responses.get(FEED_URL, json=FEED)

    collect(engine)
    assert collect(engine) == 0

    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM earthquakes")).scalar() == 2


def test_migrations_run_once(engine):
    assert migrate(engine) == []
