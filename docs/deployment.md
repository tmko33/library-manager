# Deployment

The API is stateless; all state lives in PostgreSQL. Any container platform that
can run the Docker image and provide a database URL works.

## Required environment variables

| Variable | Notes |
|---|---|
| `DATABASE_URL` | `postgresql://` and `postgres://` are normalised to `postgresql+asyncpg://` automatically. |
| `SECRET_KEY` | At least 32 characters. Startup fails in production if it still contains a development marker. |
| `ENVIRONMENT` | Set to `production` to enable the secret check. |
| `CORS_ORIGINS` | JSON list, e.g. `["https://app.example.com"]`. |

Optional: `LOAN_PERIOD_DAYS`, `MAX_ACTIVE_LOANS`, `FINE_PER_DAY`,
`RESERVATION_HOLD_DAYS`, `ACCESS_TOKEN_EXPIRE_MINUTES`.

## Render

1. Push the repository to GitHub.
2. In Render, choose **New → Blueprint** and select this repository. Render reads
   `render.yaml`, creates the web service and the PostgreSQL instance, and wires
   `DATABASE_URL`.
3. The image runs `docker/start.sh`, which applies `alembic upgrade head` and then
   starts Uvicorn on the port Render injects (`$PORT`). No custom start command is
   needed in `render.yaml`.
4. Seed demo data once from the Render shell:

   ```bash
   python -m scripts.seed
   ```

The health check points at `/health/ready`, which returns 503 when the database
is unreachable, so failed deployments roll back automatically.

## Docker

```bash
docker build -t library-manager .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/library \
  -e SECRET_KEY=replace-with-a-long-random-value \
  library-manager
```

Run migrations as a separate step (the image's entrypoint already does this when
started normally):

```bash
docker run --rm -e DATABASE_URL=... library-manager alembic upgrade head
```

The container respects `PORT`; locally it defaults to `8000`.

## Scheduled maintenance

Overdue detection and hold expiration run in `scripts/maintenance.py`:

```bash
python -m scripts.maintenance
```

Schedule it every few minutes with cron, a Render Cron Job, or a Kubernetes
CronJob:

```cron
*/15 * * * * cd /app && python -m scripts.maintenance
```

## Observability

- `GET /health` — process is alive.
- `GET /health/ready` — database is reachable.
- `GET /metrics` — Prometheus counters and latency histograms.
- Every response includes `X-Request-ID`; logs use the same id.
