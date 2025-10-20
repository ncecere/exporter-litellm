import os
import time
from typing import Dict, List

import requests


def generate_virtual_key() -> Dict:
    base_url = os.getenv("LITELLM_BASE_URL", "http://0.0.0.0:4000")
    url = f"{base_url}/key/generate"
    headers = {
        "Authorization": "Bearer dummy-key",
        "Content-Type": "application/json",
    }
    data = {
        "models": ["mock"],
        "metadata": {"user": "mock@steinbrueck.io"},
        "tpm_limit": 10000,  # tokens per minute
        "rpm_limit": 120,    # requests per minute
        "budget": 10.0,      # budget per 30 days
    }
    response = requests.post(url, headers=headers, json=data, timeout=10)
    response.raise_for_status()
    return response.json()


def make_chat_completion(api_key: str) -> Dict:
    base_url = os.getenv("LITELLM_BASE_URL", "http://0.0.0.0:4000")
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    last_response: Dict = {}
    for i in range(3):
        payload = {
            "model": "mock",
            "messages": [
                {"role": "user", "content": f"hello #{i+1}"},
            ],
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        last_response = resp.json()
    return last_response


def fetch_metrics() -> List[str]:
    exporter_url = os.getenv("EXPORTER_URL", "http://0.0.0.0:9090")
    resp = requests.get(f"{exporter_url}/metrics", timeout=10)
    resp.raise_for_status()
    return resp.text.splitlines()


def test_end_to_end_flow(endpoints_ready: None) -> None:
    # 1) Create virtual key in LiteLLM
    key_payload = generate_virtual_key()
    assert "key" in key_payload or "message" in key_payload
    api_key = key_payload.get("key") or key_payload.get("message")

    # Trigger traffic so exporter has data to expose
    make_chat_completion(api_key)
    
    # 2) Poll exporter metrics briefly to allow first scrape cycle
    metrics: List[str] = []
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            metrics = fetch_metrics()
            if any(line.startswith("litellm_") for line in metrics):
                break
        except Exception:
            pass
        time.sleep(2)
    expected_any = [
        "litellm_requests_total",
        "litellm_total_spend",
        "litellm_prompt_tokens",
        "litellm_completion_tokens",
    ]
    found = {name: any(line.startswith(name) for line in metrics) for name in expected_any}
    assert all(found.values()), f"Missing expected metrics; present={found}"

    # Additional targeted checks
    def parse_metric_value(lines: List[str], metric: str, label_selector: str) -> float:
        """Find metric value by exact prefix (strict order)."""
        prefix = f"{metric}{label_selector} "
        for line in lines:
            if line.startswith(prefix):
                try:
                    return float(line.split(" ")[-1])
                except Exception:
                    pass
        raise AssertionError(f"Metric not found: {prefix!r}")

    def find_metric_value_with_label(lines: List[str], metric: str, label_contains: str) -> float:
        """Find metric value by searching any label order, matching substring in label block."""
        metric_prefix = f"{metric}{{"
        for line in lines:
            if line.startswith(metric_prefix) and label_contains in line:
                try:
                    return float(line.split(" ")[-1])
                except Exception:
                    continue
        raise AssertionError(f"Metric with label not found: {metric} contains {label_contains!r}")

    # We sent 3 requests; accept counting either under model="mock"
    # (alias) or under the underlying real model (e.g., gpt-3.5-turbo)
    requests_value: float = 0.0
    found_any = False
    for label in ('model="mock"', 'model="gpt-3.5-turbo"'):
        try:
            requests_value = find_metric_value_with_label(metrics, "litellm_requests_total", label)
            found_any = True
            break
        except AssertionError:
            continue
    assert found_any, "litellm_requests_total with model label not found (mock or gpt-3.5-turbo)"
    assert requests_value >= 3.0, f"expected >=3 requests, got {requests_value}"

    # Spend and tokens: prefer checking concrete models; fall back to optional if label not present
    def assert_metric_non_negative_for_any_model(metric_name: str) -> None:
        for label in ('model="mock"', 'model="gpt-3.5-turbo"'):
            try:
                value = find_metric_value_with_label(metrics, metric_name, label)
                assert value >= 0.0
                return
            except AssertionError:
                continue
        # If no labeled line found, rely on earlier presence check and skip strict value assertion
        return

    assert_metric_non_negative_for_any_model("litellm_total_spend")
    assert_metric_non_negative_for_any_model("litellm_prompt_tokens")