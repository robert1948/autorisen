def test_api_version_returns_json(client):
    response = client.get("/api/version")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("application/json")
    payload = response.json()
    assert "version" in payload
    assert "buildVersion" in payload


def test_auth_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("application/json")


def test_sw_js_not_html(client):
    response = client.get("/sw.js")
    body = response.text.lstrip().lower()
    assert not body.startswith("<!doctype html")
    if response.status_code == 200:
        content_type = response.headers.get("content-type", "")
        assert "javascript" in content_type
    else:
        assert response.status_code == 404
