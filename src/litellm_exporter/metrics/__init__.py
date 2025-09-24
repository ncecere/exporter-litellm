import logging
from datetime import datetime

from prometheus_client import Gauge

from ..config import MetricsConfig
from ..database import DatabaseConnection
from ..queries import MetricQueries

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiteLLMMetrics:
    def __init__(self):
        # Spend metrics
        self.total_spend = Gauge(
            "litellm_total_spend", "Total spend across all users", ["model"]
        )
        self.user_spend = Gauge(
            "litellm_user_spend", "Spend by user", ["user_id", "user_alias", "model"]
        )
        self.team_spend = Gauge(
            "litellm_team_spend", "Spend by team", ["team_id", "team_alias", "model"]
        )
        self.org_spend = Gauge(
            "litellm_org_spend",
            "Spend by organization",
            ["organization_id", "organization_alias", "model"],
        )

        # Token metrics
        self.total_tokens = Gauge(
            "litellm_total_tokens", "Total tokens used", ["model"]
        )
        self.prompt_tokens = Gauge(
            "litellm_prompt_tokens", "Prompt tokens used", ["model"]
        )
        self.completion_tokens = Gauge(
            "litellm_completion_tokens", "Completion tokens used", ["model"]
        )

        # Request metrics
        self.requests_total = Gauge(
            "litellm_requests_total", "Total number of requests", ["model"]
        )
        self.cache_hits = Gauge(
            "litellm_cache_hits_total", "Total number of cache hits", ["model"]
        )
        self.cache_misses = Gauge(
            "litellm_cache_misses_total", "Total number of cache misses", ["model"]
        )

        # Rate limit metrics
        self.tpm_limit = Gauge(
            "litellm_tpm_limit",
            "Tokens per minute limit",
            ["entity_type", "entity_id", "entity_alias"],
        )
        self.rpm_limit = Gauge(
            "litellm_rpm_limit",
            "Requests per minute limit",
            ["entity_type", "entity_id", "entity_alias"],
        )
        self.parallel_requests = Gauge(
            "litellm_parallel_requests",
            "Maximum parallel requests",
            ["entity_type", "entity_id", "entity_alias"],
        )

        # Budget metrics
        self.budget_utilization = Gauge(
            "litellm_budget_utilization",
            "Budget utilization percentage",
            ["entity_type", "entity_id", "entity_alias"],
        )
        self.max_budget = Gauge(
            "litellm_max_budget",
            "Maximum budget",
            ["entity_type", "entity_id", "entity_alias"],
        )
        self.soft_budget = Gauge(
            "litellm_soft_budget",
            "Soft budget limit",
            ["entity_type", "entity_id", "entity_alias"],
        )
        self.budget_reset = Gauge(
            "litellm_budget_reset_time",
            "Time until budget reset in seconds",
            ["entity_type", "entity_id", "entity_alias"],
        )

        # Status metrics
        self.blocked_status = Gauge(
            "litellm_blocked_status",
            "Entity blocked status",
            ["entity_type", "entity_id", "entity_alias"],
        )

        # Key metrics
        self.key_expiry = Gauge(
            "litellm_key_expiry",
            "Time until key expiry in seconds",
            ["key_name", "key_alias"],
        )
        self.key_spend = Gauge(
            "litellm_key_spend", "Current spend for key", ["key_name", "key_alias"]
        )


class MetricsCollector:
    def __init__(
        self,
        db_connection: DatabaseConnection,
        metrics: LiteLLMMetrics,
        config: MetricsConfig,
    ):
        self.db = db_connection
        self.metrics = metrics
        self.config = config

    def update_spend_metrics(self):
        query = MetricQueries.get_spend_metrics(self.config.time_windows["spend"])
        results = self.db.execute_query(
            query, {"time_window": self.config.time_windows["spend"]}
        )

        for row in results:
            model = row["model"] or "unknown"

            # Update model-level metrics
            self.metrics.total_spend.labels(model=model).set(row["total_spend"] or 0)
            self.metrics.total_tokens.labels(model=model).set(row["total_tokens"] or 0)
            self.metrics.prompt_tokens.labels(model=model).set(
                row["prompt_tokens"] or 0
            )
            self.metrics.completion_tokens.labels(model=model).set(
                row["completion_tokens"] or 0
            )
            self.metrics.requests_total.labels(model=model).set(row["request_count"])
            self.metrics.cache_hits.labels(model=model).set(row["cache_hits"] or 0)
            self.metrics.cache_misses.labels(model=model).set(row["cache_misses"] or 0)

            # Update user/team/org specific metrics
            if row["user_id"]:
                self.metrics.user_spend.labels(
                    user_id=row["user_id"],
                    user_alias=row["user_alias"] or "none",
                    model=model,
                ).set(row["total_spend"] or 0)

            if row["team_id"]:
                self.metrics.team_spend.labels(
                    team_id=row["team_id"],
                    team_alias=row["team_alias"] or "none",
                    model=model,
                ).set(row["total_spend"] or 0)

            if row["organization_id"]:
                self.metrics.org_spend.labels(
                    organization_id=row["organization_id"],
                    organization_alias=row["organization_alias"] or "none",
                    model=model,
                ).set(row["total_spend"] or 0)

    def update_rate_limits(self):
        results = self.db.execute_query(MetricQueries.get_rate_limits())

        for row in results:
            entity_type = row["entity_type"]
            entity_id = row["entity_id"]
            entity_alias = row["entity_alias"] or "none"

            if row["tpm_limit"]:
                self.metrics.tpm_limit.labels(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_alias=entity_alias,
                ).set(row["tpm_limit"])

            if row["rpm_limit"]:
                self.metrics.rpm_limit.labels(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_alias=entity_alias,
                ).set(row["rpm_limit"])

            if row["max_parallel_requests"]:
                self.metrics.parallel_requests.labels(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_alias=entity_alias,
                ).set(row["max_parallel_requests"])

            if row["is_blocked"]:
                self.metrics.blocked_status.labels(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_alias=entity_alias,
                ).set(1)

    def update_budget_metrics(self):
        results = self.db.execute_query(MetricQueries.get_budget_metrics())

        for row in results:
            entity_type = row["entity_type"]
            entity_id = row["entity_id"]
            entity_alias = row["entity_alias"] or "none"

            if row["max_budget"]:
                self.metrics.max_budget.labels(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_alias=entity_alias,
                ).set(row["max_budget"])

                if row["current_spend"]:
                    utilization = (row["current_spend"] / row["max_budget"]) * 100
                    self.metrics.budget_utilization.labels(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        entity_alias=entity_alias,
                    ).set(utilization)

            if row["soft_budget"]:
                self.metrics.soft_budget.labels(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_alias=entity_alias,
                ).set(row["soft_budget"])

            if row["budget_reset_at"]:
                reset_seconds = (
                    row["budget_reset_at"] - datetime.now()
                ).total_seconds()
                if reset_seconds > 0:
                    self.metrics.budget_reset.labels(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        entity_alias=entity_alias,
                    ).set(reset_seconds)

    def update_key_metrics(self):
        results = self.db.execute_query(MetricQueries.get_key_metrics())

        for row in results:
            key_name = row["key_name"] or "none"
            key_alias = row["key_alias"] or "none"

            if row["expires"]:
                expiry_seconds = (row["expires"] - datetime.now()).total_seconds()
                if expiry_seconds > 0:
                    self.metrics.key_expiry.labels(
                        key_name=key_name, key_alias=key_alias
                    ).set(expiry_seconds)

            if row["spend"]:
                self.metrics.key_spend.labels(
                    key_name=key_name, key_alias=key_alias
                ).set(row["spend"])

    def update_key_spend(self):
        results = self.db.execute_query(MetricQueries.get_key_spend())
        for row in results:
            key_name = row["key_name"] or "none"
            key_alias = row["key_alias"] or "none"
            spend = row["total_spend"] or 0
            self.metrics.key_spend.labels(key_name=key_name, key_alias=key_alias).set(
                spend
            )

    def update_all_metrics(self):
        try:
            self.update_spend_metrics()
            self.update_rate_limits()
            self.update_budget_metrics()
            self.update_key_metrics()
            self.update_key_spend()
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
