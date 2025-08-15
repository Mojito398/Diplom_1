import json
import os
from typing import Any, Dict, Iterable, Optional, Tuple

import pytest
import requests
from deepdiff import DeepDiff
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


_test_results: list[Dict[str, Any]] = []


def build_requests_session() -> Session:
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


_session = build_requests_session()


def _normalize_bearer(token: str) -> str:
    token_stripped = token.strip()
    if token_stripped.lower().startswith("bearer "):
        return token_stripped
    return f"Bearer {token_stripped}"


def _iter_collection_items(items: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    for item in items:
        if "request" in item:
            yield item
        if "item" in item and isinstance(item["item"], list):
            yield from _iter_collection_items(item["item"])  # type: ignore[arg-type]


def _extract_request_url(raw_url: Any) -> Optional[str]:
    if isinstance(raw_url, str):
        return raw_url
    if isinstance(raw_url, dict):
        if raw_url.get("raw"):
            return str(raw_url["raw"])
        protocol = raw_url.get("protocol")
        host = raw_url.get("host")
        path = raw_url.get("path")
        if isinstance(host, list):
            host = ".".join(host)
        if isinstance(path, list):
            path = "/".join(path)
        if host and path:
            prefix = f"{protocol}://" if protocol else "https://"
            return f"{prefix}{host}/{path}"
    return None


def get_expected_response_and_url_from_postman(collection_uid: str, request_name: str) -> Tuple[str, Dict[str, Any]]:
    api_key = os.getenv("POSTMAN_API_KEY")
    if not api_key:
        pytest.skip("POSTMAN_API_KEY is not set in environment; skipping API tests.")

    url = f"https://api.getpostman.com/collections/{collection_uid}"
    headers = {"X-Api-Key": api_key}

    resp = _session.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    collection = resp.json()

    items = collection.get("collection", {}).get("item", [])

    for item in _iter_collection_items(items):
        if item.get("name") == request_name and "request" in item:
            request_url = _extract_request_url(item["request"].get("url"))
            if not request_url:
                raise ValueError(f"Request URL is missing or invalid for '{request_name}' in Postman collection")

            responses = item.get("response") or []
            example_body_text: Optional[str] = None
            if responses and isinstance(responses, list):
                first = responses[0]
                example_body_text = first.get("body") if isinstance(first, dict) else None

            if example_body_text is None:
                raise ValueError(f"No example response body found in Postman item '{request_name}'")

            try:
                expected_response = json.loads(example_body_text)
            except Exception as exc:
                raise ValueError(
                    f"Example response for '{request_name}' is not valid JSON: {exc}"
                ) from exc

            return request_url, expected_response

    raise ValueError(f"Request '{request_name}' not found in Postman collection {collection_uid}")


def perform_request_and_validate(collection_uid: str, request_name: str) -> None:
    auth_token_env = os.getenv("AUTH_TOKEN") or os.getenv("API_AUTH_TOKEN")
    if not auth_token_env:
        pytest.skip("AUTH_TOKEN is not set in environment; skipping API tests.")

    request_url, expected_response = get_expected_response_and_url_from_postman(collection_uid, request_name)

    headers = {"Authorization": _normalize_bearer(auth_token_env)}

    response = _session.get(request_url, headers=headers, timeout=30)
    response.raise_for_status()

    try:
        response_json = response.json()
    except Exception as exc:
        raise AssertionError(
            f"Response for '{request_name}' is not valid JSON: {exc}\nRaw: {response.text[:1000]}"
        ) from exc

    diff = DeepDiff(response_json, expected_response, ignore_order=True)

    result = {
        "test_name": request_name,
        "status": "PASSED" if not diff else "FAILED",
        "expected_response": expected_response,
        "actual_response": response_json,
        "differences": diff if diff else None,
    }
    _test_results.append(result)

    if diff:
        raise AssertionError(
            "\n".join(
                [
                    f"Фактический и ожидаемый JSON не совпадают для запроса '{request_name}'!",
                    f"Ожидаемый результат (ОР): {json.dumps(expected_response, ensure_ascii=False, indent=2)}",
                    f"Фактический результат (ФР): {json.dumps(response_json, ensure_ascii=False, indent=2)}",
                    f"Различия: {diff}",
                ]
            )
        )