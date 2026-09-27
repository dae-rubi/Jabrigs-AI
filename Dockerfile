FROM python:3.11-slim

WORKDIR /app

# System deps yang mungkin dibutuhkan script pengendali (opsional)
RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
    curl git && \
    rm -rf /var/lib/apt/lists/*

# Environment non-interaktif supaya pip/tidak prompt
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Buat script start
RUN echo '#!/bin/sh\nexec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh && \
    chmod +x /app/start.sh

# Default non-root user (opsional, lebih aman)
RUN addgroup --system --gid 1001 jabrig && \
    adduser --system --uid 1001 --ingroup jabrig --shell /sbin/nologin --disabled-password jabrig && \
    chown -R jabrig:jabrig /app

USER jabrig

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

ENTRYPOINT ["/app/start.sh"]
