import os


class MetricsConfig:
    def __init__(self):
        # Time windows for different types of metrics
        self.spend_window = os.getenv(
            "METRICS_SPEND_WINDOW", "30d"
        )  # Default 30 days for spend metrics
        self.request_window = os.getenv(
            "METRICS_REQUEST_WINDOW", "24h"
        )  # Default 24 hours for request metrics
        self.error_window = os.getenv(
            "METRICS_ERROR_WINDOW", "1h"
        )  # Default 1 hour for error metrics
        self.update_interval = int(
            os.getenv("METRICS_UPDATE_INTERVAL", "15")
        )  # Default 15 seconds for metrics update

        # Convert time window strings to PostgreSQL intervals
        self.time_windows = {
            "spend": self._parse_time_window(self.spend_window),
            "request": self._parse_time_window(self.request_window),
            "error": self._parse_time_window(self.error_window),
        }

    def _parse_time_window(self, window: str) -> str:
        """Convert time window string (e.g., '30d', '24h') to PostgreSQL interval."""
        unit = window[-1].lower()
        value = int(window[:-1])

        units = {"d": "days", "h": "hours", "m": "minutes"}

        if unit not in units:
            raise ValueError(
                f"Invalid time window unit: {unit}. Use 'd' for days, 'h' for hours, or 'm' for minutes."
            )

        return f"{value} {units[unit]}"


class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv("LITELLM_DB_HOST", "localhost")
        self.port = os.getenv("LITELLM_DB_PORT", "5432")
        self.name = os.getenv("LITELLM_DB_NAME", "litellm")
        self.user = os.getenv("LITELLM_DB_USER", "postgres")
        self.password = os.getenv("LITELLM_DB_PASSWORD", "")
        self.min_connections = int(os.getenv("DB_MIN_CONNECTIONS", "1"))
        self.max_connections = int(os.getenv("DB_MAX_CONNECTIONS", "10"))
