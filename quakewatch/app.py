import os

from flask import Flask, render_template, request
from sqlalchemy import Engine, text

from quakewatch.db import build_engine, migrate


def search_earthquakes(engine: Engine, query: str, limit: int = 50) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT id, magnitude, place, occurred_at, url FROM earthquakes "
            "WHERE LOWER(place) LIKE :q ORDER BY occurred_at DESC LIMIT :limit"
        ), {"q": f"%{query.lower()}%", "limit": limit})
        return [dict(row._mapping) for row in rows]


def create_app(engine: Engine | None = None) -> Flask:
    app = Flask(__name__)
    engine = engine or build_engine()
    migrate(engine)

    @app.get("/")
    def index():
        query = request.args.get("q", "").strip()
        results = search_earthquakes(engine, query) if query else []
        return render_template("index.html", query=query, results=results)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=int(os.environ.get("PORT", 5000)))
