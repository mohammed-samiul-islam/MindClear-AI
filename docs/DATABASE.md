# Database notes

The backend reads a single `DATABASE_URL` (SQLAlchemy URL).

| Environment | Value |
|---|---|
| Local (default) | unset → `sqlite:///./dev.db` (file created in the working directory) |
| Tests | a temporary SQLite file (see `backend/tests/conftest.py`) |
| Production | Neon Postgres, e.g. `postgresql://USER:PASSWORD@ep-xxx-pooler.REGION.aws.neon.tech/neondb?sslmode=require` |

* `postgres://` URLs are normalized to `postgresql://` automatically.
* UUID columns use SQLAlchemy's generic `Uuid` type, so the same models work on SQLite and Postgres.
* Tables are created at startup with `Base.metadata.create_all`. There are no migrations yet; this
  branch adds `session_id` and `source` columns, so an **existing** `dev.db` or database created by the
  old version must be dropped/recreated (delete `dev.db` locally; on Neon, use a fresh database or
  `DROP TABLE tasks, conversions;`). Adding Alembic is a sensible next step.
* Neon's free tier suspends idle compute; the first request after idle may take a few seconds.
  `pool_pre_ping=True` is enabled so stale pooled connections are recycled.
