from datetime import datetime

from quakewatch.app import create_app
from quakewatch.collector import Earthquake, save_earthquakes


def test_echoes_user_input(engine):
    client = create_app(engine).test_client()

    response = client.get("/?q=Hanoi")

    assert response.status_code == 200
    assert "You searched for: <strong>Hanoi</strong>" in response.text


def test_escapes_user_input(engine):
    client = create_app(engine).test_client()

    response = client.get("/?q=<script>alert(1)</script>")

    assert "<script>alert(1)</script>" not in response.text
    assert "&lt;script&gt;" in response.text


def test_shows_matching_earthquakes(engine):
    save_earthquakes(engine, [
        Earthquake("ak001", 2.4, "Beluga, Alaska", datetime(2026, 10, 1), -150.6, 61.2, 49.3, None),
        Earthquake("jp001", 4.8, "Off the coast of Japan", datetime(2026, 10, 1), 142.1, 38.3, 10.0, None),
    ])
    client = create_app(engine).test_client()

    response = client.get("/?q=alaska")

    assert "Beluga, Alaska" in response.text
    assert "Off the coast of Japan" not in response.text
