def test_api_version_returns_json(client):
    response = client.get("/api/version")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("application/json")
    payload = response.json()
    assert "version" in payload
    assert "buildVersion" in payload
