import logging
import os
import time

from prometheus_client import start_http_server

from .config import DatabaseConfig, MetricsConfig
from .database import DatabaseConnection
from .metrics import LiteLLMMetrics, MetricsCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Initialize configurations
    metrics_config = MetricsConfig()
    db_config = DatabaseConfig()

    # Initialize connections and collectors
    db_connection = DatabaseConnection(db_config)
    metrics = LiteLLMMetrics()
    collector = MetricsCollector(db_connection, metrics, metrics_config)

    # Start the metrics server
    metrics_port = int(os.getenv("METRICS_PORT", "9090"))
    start_http_server(metrics_port)
    logger.info(f"Metrics server started on port {metrics_port}")
    logger.info(
        f"Using time windows: spend={metrics_config.spend_window}, "
        f"request={metrics_config.request_window}, error={metrics_config.error_window}"
    )
    logger.info(f"Metrics update interval: {metrics_config.update_interval} seconds")

    # Update metrics based on configured interval
    while True:
        collector.update_all_metrics()
        time.sleep(metrics_config.update_interval)


if __name__ == "__main__":
    main()
