from flask.testing import FlaskClient
from pytest import mark

STRICT_CSP = "default-src 'none'; frame-ancestors 'none'"


def test_api_responses_carry_strict_headers(client: FlaskClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.headers["Content-Security-Policy"] == STRICT_CSP
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert "Strict-Transport-Security" not in resp.headers


def test_doc_page_allows_scalar_assets(client: FlaskClient) -> None:
    resp = client.get("/apidoc", follow_redirects=True)
    assert resp.status_code == 200
    assert "https://cdn.jsdelivr.net" in resp.headers["Content-Security-Policy"]


def test_doc_spec_keeps_strict_csp(client: FlaskClient) -> None:
    resp = client.get("/apidoc/openapi.json")
    assert resp.headers["Content-Security-Policy"] == STRICT_CSP


@mark.parametrize("env", ["prod"])
def test_prod_redirects_http_to_https(client: FlaskClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 302
    assert resp.headers["Location"].startswith("https://")


@mark.parametrize("env", ["prod"])
def test_prod_sends_hsts_over_https(client: FlaskClient) -> None:
    resp = client.get("/api/v1/health", base_url="https://localhost")
    assert resp.status_code == 200
    assert "max-age=" in resp.headers["Strict-Transport-Security"]
