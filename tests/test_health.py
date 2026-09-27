def test_not_get_error(client):
    resp = client.put("/api/v1/health")
    assert resp.status_code == 404
    resp = client.post("/api/v1/health")
    assert resp.status_code == 404


def test_get_return_valid_json(client):
    resp = client.get("/api/v1/health/")
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json()["message"] == "healthy service"
