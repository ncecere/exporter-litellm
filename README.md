# LiteLLM Prometheus Exporter

This exporter provides comprehensive Prometheus metrics for LiteLLM, exposing usage, spend, performance, and operational data from the LiteLLM database.

## Metrics Exposed

### Spend Metrics
- `litellm_total_spend`: Total spend across all users by model
- `litellm_user_spend`: Spend by user and model (labels: user_id, user_alias, model)
- `litellm_team_spend`: Spend by team and model (labels: team_id, team_alias, model)
- `litellm_org_spend`: Spend by organization and model (labels: organization_id, organization_alias, model)
- `litellm_tag_spend`: Spend by request tag

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

### Database Connection
- `LITELLM_DB_HOST`: PostgreSQL host (default: localhost)
- `LITELLM_DB_PORT`: PostgreSQL port (default: 5432)
- `LITELLM_DB_NAME`: Database name (default: litellm)
- `LITELLM_DB_USER`: Database user (default: postgres)
- `LITELLM_DB_PASSWORD`: Database password (default: empty)
- `DB_MIN_CONNECTIONS`: Minimum number of database connections in the pool (default: 1)
- `DB_MAX_CONNECTIONS`: Maximum number of database connections in the pool (default: 10)

### Metric Collection Configuration
- `METRICS_PORT`: Port to expose metrics on (default: 9090)
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

## Running with Docker

1. Build the Docker image:
```bash
docker build -t litellm-exporter .
```

2. Run the container:
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
  -e METRICS_SPEND_WINDOW=30d \
  -e METRICS_REQUEST_WINDOW=24h \
  -e METRICS_ERROR_WINDOW=1h \
  litellm-exporter
```

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export LITELLM_DB_HOST=your-db-host
export LITELLM_DB_PORT=5432
export LITELLM_DB_NAME=your-db-name
export LITELLM_DB_USER=your-db-user
export LITELLM_DB_PASSWORD=your-db-password
export DB_MIN_CONNECTIONS=1
export DB_MAX_CONNECTIONS=10
export METRICS_SPEND_WINDOW=30d
export METRICS_REQUEST_WINDOW=24h
export METRICS_ERROR_WINDOW=1h
```

3. Run the exporter:
```bash
python litellm_exporter.py
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