import os
import subprocess
import time
from typing import Generator

import pytest
import requests


def wait_for_http_ok(url: str, timeout_seconds: int = 60, sleep_seconds: float = 1.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error: str = ""
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=5)
            if 200 <= response.status_code < 300:
                return
            last_error = f"status={response.status_code}"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        time.sleep(sleep_seconds)
    raise TimeoutError(f"Timeout waiting for {url} to be ready; last_error={last_error}")


@pytest.fixture(scope="session")
def compose_up() -> Generator[None, None, None]:
    workdir = os.path.abspath(os.path.dirname(__file__))
    compose_file = os.getenv("COMPOSE_FILE", "docker-compose-e2e.yml")
    up_cmd = ["docker", "compose", "-f", compose_file, "up", "-d"]
    subprocess.run(up_cmd, cwd=workdir, check=True)
    try:
        yield
    finally:
        down_cmd = ["docker", "compose", "-f", compose_file, "down", "-v"]
        subprocess.run(down_cmd, cwd=workdir, check=False)


@pytest.fixture(scope="session")
def endpoints_ready(compose_up: None) -> None:
    litellm_base = os.getenv("LITELLM_BASE_URL", "http://0.0.0.0:4000")
    exporter_base = os.getenv("EXPORTER_URL", "http://0.0.0.0:9090")
    for path in ("/health/liveliness", "/health", "/", ""):
        try:
            wait_for_http_ok(f"{litellm_base}{path}", timeout_seconds=30)
            break
        except TimeoutError:
            continue

    # Wait for exporter metrics endpoint
    wait_for_http_ok(f"{exporter_base}/metrics", timeout_seconds=90)

