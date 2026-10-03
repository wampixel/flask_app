from pytest import mark


@mark.parametrize("automatic_options", [True, False], ids=["on", "off"])
def test_not_get_error(client):
    resp = client.put("/api/v1/health")
    assert resp.status_code in (401, 405)
    resp = client.post("/api/v1/health")
    assert resp.status_code in (401, 405)


def test_get_return_valid_json(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json()["message"] == "healthy service"
