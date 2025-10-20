# LiteLLM Prometheus Exporter

This exporter provides comprehensive Prometheus metrics for LiteLLM, exposing usage, spend, performance, and operational data from the LiteLLM database.

## Metrics Exposed

### Spend Metrics

- `litellm_total_spend`: Total spend across all users by model
- `litellm_user_spend`: Spend by user and model (labels: user_id, user_alias, model)
- `litellm_team_spend`: Spend by team and model (labels: team_id, team_alias, model)
- `litellm_org_spend`: Spend by organization and model (labels: organization_id, organization_alias, model)
- `litellm_tag_spend`: Spend by request tag
- `litellm_key_spend`: Spend by API key and model (labels: key_name, key_alias, model)

### Token Metrics

- `litellm_total_tokens`: Total tokens used by model
- `litellm_prompt_tokens`: Prompt tokens used by model
- `litellm_completion_tokens`: Completion tokens used by model

### Request Metrics

- `litellm_request_duration_seconds`: Request duration histogram
- `litellm_requests_total`: Total number of requests by model and status
- `litellm_parallel_requests`: Current parallel requests by entity (labels: entity_type, entity_id, entity_alias)

### Rate Limit Metrics

- `litellm_tpm_limit`: Tokens per minute limit by entity (labels: entity_type, entity_id, entity_alias)
- `litellm_rpm_limit`: Requests per minute limit by entity (labels: entity_type, entity_id, entity_alias)
- `litellm_current_tpm`: Current tokens per minute usage (labels: entity_type, entity_id, entity_alias)
- `litellm_current_rpm`: Current requests per minute usage (labels: entity_type, entity_id, entity_alias)

### Cache Metrics

- `litellm_cache_hits_total`: Total number of cache hits by model
- `litellm_cache_misses_total`: Total number of cache misses by model

### Budget Metrics

- `litellm_budget_utilization`: Budget utilization percentage (labels: entity_type, entity_id, entity_alias)
- `litellm_max_budget`: Maximum budget (labels: entity_type, entity_id, entity_alias)
- `litellm_soft_budget`: Soft budget limit (labels: entity_type, entity_id, entity_alias)
- `litellm_budget_reset_time`: Time until budget reset in seconds (labels: entity_type, entity_id, entity_alias)

### Error Metrics

- `litellm_errors_total`: Total number of errors by model and error type
- `litellm_error_rate`: Rate of errors per minute by model

### Entity Metrics

- `litellm_blocked_status`: Entity blocked status (labels: entity_type, entity_id, entity_alias)
- `litellm_member_count`: Number of members in a team (labels: team_id, team_alias)
- `litellm_admin_count`: Number of admins in a team (labels: team_id, team_alias)

### API Key Metrics

- `litellm_active_keys`: Number of active API keys (labels: entity_type, entity_id, entity_alias)
- `litellm_expired_keys`: Number of expired API keys (labels: entity_type, entity_id, entity_alias)
- `litellm_key_expiry`: Time until key expiry in seconds (labels: key_name, key_alias)

### Model Metrics

- `litellm_available_models`: Number of available models (labels: entity_type, entity_id, entity_alias)
- `litellm_model_info`: Model information (name, configuration, etc.)

## Configuration

For a comprehensive guide to all environment variables, their impacts, and best practices, see [ENV_VARS.md](ENV_VARS.md).

### Database Connection

- `LITELLM_DB_HOST`: PostgreSQL host (default: localhost)
- `LITELLM_DB_PORT`: PostgreSQL port (default: 5432)
- `LITELLM_DB_NAME`: Database name (default: litellm)
- `LITELLM_DB_USER`: Database user (default: postgres)
- `LITELLM_DB_PASSWORD`: Database password (default: empty)
- `DB_MIN_CONNECTIONS`: Minimum number of database connections in the pool (default: 1)
- `DB_MAX_CONNECTIONS`: Maximum number of database connections in the pool (default: 10)

For security best practices, it's recommended to create a dedicated read-only PostgreSQL user for the exporter. See [POSTGRES_SETUP.md](POSTGRES_SETUP.md) for detailed instructions on setting up a read-only database user.

### Metric Collection Configuration

- `METRICS_PORT`: Port to expose metrics on (default: 9090)
- `METRICS_UPDATE_INTERVAL`: How frequently metrics are updated in seconds (default: 15)
- `METRICS_SPEND_WINDOW`: Time window for spend metrics (default: 30d)
- `METRICS_REQUEST_WINDOW`: Time window for request metrics (default: 24h)
- `METRICS_ERROR_WINDOW`: Time window for error metrics (default: 1h)

Time windows can be specified using:

- 'd' for days (e.g., '30d')
- 'h' for hours (e.g., '24h')
- 'm' for minutes (e.g., '30m')

### Time Window Impact

Different time windows affect both metric accuracy and database performance:

- **Spend Window** (default: 30d)
  - Longer windows provide better historical spend analysis
  - Affects memory usage and query performance
  - Consider your retention needs when adjusting

- **Request Window** (default: 24h)
  - Shorter windows provide more accurate recent usage patterns
  - Useful for monitoring current system load
  - Affects request rate and throughput calculations

- **Error Window** (default: 1h)
  - Short window for immediate error detection
  - Helps identify current system issues
  - Minimal impact on database performance

- **Update Interval** (default: 15s)
  - Controls how frequently metrics are refreshed
  - Lower values provide more real-time data but increase database load
  - Higher values reduce database load but decrease metric freshness
  - Adjust based on your monitoring needs and database capacity

## Running with Docker Compose

The easiest way to get started is using Docker Compose:

1. Create a docker-compose.yml file:

```yaml
services:
  litellm-exporter:
    image: nicholascecere/exporter-litellm:latest
    platform: linux/amd64
    ports:
      - "9090:9090"
    environment:
      - LITELLM_DB_HOST=your-db-host
      - LITELLM_DB_PORT=5432
      - LITELLM_DB_NAME=your-db-name
      - LITELLM_DB_USER=your-db-user
      - LITELLM_DB_PASSWORD=your-db-password
      - DB_MIN_CONNECTIONS=1
      - DB_MAX_CONNECTIONS=10
      - METRICS_UPDATE_INTERVAL=15
      - METRICS_SPEND_WINDOW=30d
      - METRICS_REQUEST_WINDOW=24h
      - METRICS_ERROR_WINDOW=1h
```

1. Start the exporter:

```bash
docker-compose up -d
```

The exporter will start on port 9090 and connect to your existing LiteLLM database.

## Running with Kubernetes

The exporter can be deployed to Kubernetes using the provided manifests in the `k8s` directory:

1. First, encode your database credentials:

```bash
echo -n "your-db-host" | base64
echo -n "5432" | base64
echo -n "your-db-name" | base64
echo -n "your-db-user" | base64
echo -n "your-db-password" | base64
```

1. Update the Secret in `k8s/exporter-litellm.yaml` with your base64-encoded values:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: litellm-exporter-secrets
type: Opaque
data:
  LITELLM_DB_HOST: "base64-encoded-host"
  LITELLM_DB_PORT: "base64-encoded-port"
  LITELLM_DB_NAME: "base64-encoded-name"
  LITELLM_DB_USER: "base64-encoded-user"
  LITELLM_DB_PASSWORD: "base64-encoded-password"
```

1. Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/exporter-litellm.yaml
```

This will create:

- A ConfigMap with exporter configuration
- A Secret containing database credentials
- A Deployment running the exporter
- A Service exposing the metrics endpoint

The exporter will be available at `http://litellm-exporter:9090` within your cluster. The deployment includes:

- Resource limits and requests
- Liveness and readiness probes
- Prometheus scrape annotations
- Configurable replicas (default: 1)

## Running with Docker

You can run the exporter directly with Docker:

```bash
docker run -d \
  -p 9090:9090 \
  -e LITELLM_DB_HOST=your-db-host \
  -e LITELLM_DB_PORT=5432 \
  -e LITELLM_DB_NAME=your-db-name \
  -e LITELLM_DB_USER=your-db-user \
  -e LITELLM_DB_PASSWORD=your-db-password \
  -e DB_MIN_CONNECTIONS=1 \
  -e DB_MAX_CONNECTIONS=10 \
  -e METRICS_UPDATE_INTERVAL=15 \
  -e METRICS_SPEND_WINDOW=30d \
  -e METRICS_REQUEST_WINDOW=24h \
  -e METRICS_ERROR_WINDOW=1h \
  nicholascecere/exporter-litellm:latest
```

## Running Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Set environment variables:

```bash
export LITELLM_DB_HOST=your-db-host
export LITELLM_DB_PORT=5432
export LITELLM_DB_NAME=your-db-name
export LITELLM_DB_USER=your-db-user
export LITELLM_DB_PASSWORD=your-db-password
export DB_MIN_CONNECTIONS=1
export DB_MAX_CONNECTIONS=10
export METRICS_UPDATE_INTERVAL=15
export METRICS_SPEND_WINDOW=30d
export METRICS_REQUEST_WINDOW=24h
export METRICS_ERROR_WINDOW=1h
```

1. Run the exporter:

```bash
python litellm_exporter.py
```

## Local Docker Build & Test (for Development)

To build and test the Docker container locally, use the provided Makefile for a streamlined workflow. This approach allows you to quickly build and test the Docker image in your local environment, streamlining development and troubleshooting.

### Prerequisites

- Docker installed and running
- A valid `.env` file in the project root (see [Configuration](#configuration) for required variables)

### Build the Docker Image

```bash
make build
```

This will build the image as `litellm-exporter:local` by default. You can override the image name if needed:

```bash
make build IMAGE_NAME=my-custom-image:dev
```

### Run the Container (Interactive)

```bash
make run
```

This will start the container interactively, mapping port 9090 and loading environment variables from `.env`.

### Run the Container (Detached)

```bash
make run-detached
```

This will start the container in the background. To view logs:

```bash
make logs
```

### Stop and Clean Up

```bash
make stop
```

This stops and removes the running container. To remove the local image as well:

```bash
make clean
```

### Customization

You can override the following variables at runtime:

- `IMAGE_NAME` (default: `litellm-exporter:local`)
- `CONTAINER_NAME` (default: `litellm-exporter`)
- `PORT` (default: `9090`)

Example:

```bash
make run-detached IMAGE_NAME=my-image:dev CONTAINER_NAME=litellm-dev PORT=8080
```

## Prometheus Configuration

Add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'litellm'
    static_configs:
      - targets: ['localhost:9090']
```

## Grafana Dashboard Examples

Here are some example Prometheus queries for creating Grafana dashboards:

### Spend Monitoring

- Total spend rate: `rate(litellm_total_spend[1h])`
- Spend by model: `sum by (model) (litellm_total_spend)`
- Team spend by alias: `sum by (team_alias) (litellm_team_spend)`
- Organization spend by alias: `sum by (organization_alias) (litellm_org_spend)`
- API key spend by alias: `sum by (key_alias) (litellm_key_spend)`
- API key spend by key name: `sum by (key_name) (litellm_key_spend)`

### Performance Monitoring

- Request latency: `rate(litellm_request_duration_seconds_sum[5m]) / rate(litellm_request_duration_seconds_count[5m])`
- Error rate: `rate(litellm_errors_total[5m])`
- Cache hit ratio: `rate(litellm_cache_hits_total[5m]) / (rate(litellm_cache_hits_total[5m]) + rate(litellm_cache_misses_total[5m]))`

### Rate Limit Monitoring

- TPM utilization by alias: `sum by (entity_alias) (litellm_current_tpm / litellm_tpm_limit * 100)`
- RPM utilization by alias: `sum by (entity_alias) (litellm_current_rpm / litellm_rpm_limit * 100)`

### User/Team Activity

- Active teams by alias: `count by (team_alias) (litellm_member_count)`
- Blocked users by alias: `sum by (entity_alias) (litellm_blocked_status{entity_type="user"})`

### API Key Management

- Expiring keys alert: `litellm_key_expiry{key_alias="important-service"} < 86400` (keys expiring within 24h)
- Active keys by entity: `sum by (entity_alias) (litellm_active_keys)`

### Budget Monitoring

- High budget utilization alert: `litellm_budget_utilization > 80`
- Budget utilization by alias: `sum by (entity_alias) (litellm_budget_utilization)`

These metrics provide comprehensive monitoring of your LiteLLM deployment, enabling you to track usage, performance, costs, and potential issues. The addition of alias labels and configurable time windows makes it easier to create meaningful dashboards and manage database performance.

## License

This project is licensed under the GLWT (Good Luck With That) Public License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
