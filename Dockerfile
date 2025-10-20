FROM python:3.12.8

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Add Tini (multi-arch)
ARG TARGETARCH
ENV TINI_VERSION=v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${TARGETARCH} /tini
RUN chmod +x /tini

# Install uv and dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"
COPY pyproject.toml ./
RUN uv sync --no-dev
ENV PATH="/app/.venv/bin:${PATH}"

# Copy application code
COPY src/litellm_exporter/ /app/litellm_exporter/

# Default environment variables
ENV METRICS_PORT=9090
ENV LITELLM_DB_HOST=localhost
ENV LITELLM_DB_PORT=5432
ENV LITELLM_DB_NAME=litellm
ENV LITELLM_DB_USER=postgres
ENV DB_MIN_CONNECTIONS=1
ENV DB_MAX_CONNECTIONS=10

# Metric collection configuration
ENV METRICS_UPDATE_INTERVAL=15
ENV METRICS_SPEND_WINDOW=30d
ENV METRICS_REQUEST_WINDOW=24h
ENV METRICS_ERROR_WINDOW=1h

# Sensitive environment variable not included here
# ENV LITELLM_DB_PASSWORD=

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${METRICS_PORT} || exit 1

# Create non-root user
RUN useradd -m -u 1000 exporter
USER exporter

EXPOSE ${METRICS_PORT}

# Use tini as init system to handle signals properly
ENTRYPOINT ["/tini", "--"]

# Run the exporter module directly
CMD ["python", "-m", "litellm_exporter"]
