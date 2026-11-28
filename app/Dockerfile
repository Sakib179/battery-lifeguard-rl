FROM python:3.12-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1
WORKDIR /app

FROM base AS data
COPY simulation/ ./simulation/
COPY app/data.py ./app/
COPY reports/ ./reports/
RUN python -m app.data /app/app/data.json

FROM base
COPY app/requirements.txt ./app/
RUN python -m pip install --no-cache-dir --only-binary=:all: -r app/requirements.txt \
    && find /usr/local/lib/python3.12/site-packages -type d -name __pycache__ -prune -exec rm -rf '{}' +
COPY app/app.py ./app/
COPY --from=data /app/app/data.json ./app/

ENV HOME=/tmp
USER 10001:10001
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:8501/_stcore/health', timeout=2).close()"]
CMD ["python", "-m", "streamlit", "run", "app/app.py", "--server.address=0.0.0.0", "--server.headless=true", "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"]
