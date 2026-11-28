FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    MPLBACKEND=Agg \
    PIP_DISABLE_PIP_VERSION_CHECK=1

FROM base AS dependencies
RUN python -m pip install --no-cache-dir --only-binary=:all: \
        "mlflow==2.22.5" "SQLAlchemy==2.0.58" \
    && mkdir -p /var/lib/lifeguard \
    && chown 10001:10001 /var/lib/lifeguard
RUN find /usr/local/lib/python3.12/site-packages -type d -name __pycache__ -prune -exec rm -rf '{}' + \
    && find /usr/local/lib/python3.12/site-packages/mlflow/server/js/build -name '*.map' -delete

FROM base
WORKDIR /app
COPY --from=dependencies /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=dependencies /usr/local/bin/mlflow /usr/local/bin/gunicorn /usr/local/bin/
COPY --from=dependencies --chown=10001:10001 /var/lib/lifeguard/ /var/lib/lifeguard/
COPY tracking/*.py ./tracking/
COPY simulation/index.html simulation/charging-controller.html simulation/discharge-controller.html simulation/switch-replay.html simulation/*.css simulation/*.js ./simulation/

ENV PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1
WORKDIR /var/lib/lifeguard
USER 10001:10001
EXPOSE 5500
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:5500/health', timeout=2).close()"]

CMD ["python", "-m", "gunicorn", "--workers", "1", "--bind", "0.0.0.0:5500", "tracking.container:create_app()"]
