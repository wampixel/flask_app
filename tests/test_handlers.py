def test_error_response(client):
    resp = client.get("/invalid")
    assert resp.status_code == 404
    assert resp.is_json
    assert resp.get_json()["type"] == "not_found"
