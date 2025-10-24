from urllib.parse import parse_qsl, urlparse

from backend.src.core.config import settings
from backend.src.modules.auth.router import (
    _GOOGLE_AUTH_ENDPOINT,
    _LINKEDIN_AUTH_ENDPOINT,
    _OAUTH_STATE_MAX_AGE,
)


def test_google_oauth_start_and_callback_flow(client):
    previous_client_id = settings.google_client_id
    previous_callback = settings.google_callback_url
    try:
        settings.google_client_id = "test-google-client"
        settings.google_callback_url = None

        start_response = client.get(
            "/api/auth/oauth/google/start",
            params={"next": "/dashboard"},
            allow_redirects=False,
        )
        assert start_response.status_code == 307
        location = start_response.headers["location"]
        assert "https://accounts.google.com" in location

        query = dict(parse_qsl(urlparse(location).query))
        assert query["client_id"] == "test-google-client"
        state_value = query["state"]
        assert state_value.startswith("google:")

        # TestClient should retain the issued state cookie
        assert client.cookies.get("oauth_state_google")

        callback_response = client.get(
            "/api/auth/oauth/google/callback",
            params={"code": "sample-code", "state": state_value},
            allow_redirects=False,
        )
        assert callback_response.status_code == 302
        final_location = callback_response.headers["location"]
        assert final_location.startswith(
            settings.frontend_origin.rstrip("/") + "/auth/callback"
        )

        final_query = dict(parse_qsl(urlparse(final_location).query))
        assert final_query["code"] == "sample-code"
        assert final_query["state"] == state_value
        assert final_query["next"] == "/dashboard"

        # Cookie should be cleared after callback
        set_cookie_header = callback_response.headers.get("set-cookie", "")
        assert "oauth_state_google=" in set_cookie_header
        assert "Max-Age=0" in set_cookie_header
    finally:
        settings.google_client_id = previous_client_id
        settings.google_callback_url = previous_callback
        client.cookies.clear()


def test_linkedin_oauth_start_and_callback_flow(client):
    previous_client_id = settings.linkedin_client_id
    previous_callback = settings.linkedin_callback_url
    try:
        settings.linkedin_client_id = "test-linkedin-client"
        settings.linkedin_callback_url = None

        start_response = client.get(
            "/api/auth/oauth/linkedin/start",
            params={"next": "/dashboard"},
            allow_redirects=False,
        )
        assert start_response.status_code == 307
        location = start_response.headers["location"]
        assert "https://www.linkedin.com/oauth" in location

        query = dict(parse_qsl(urlparse(location).query))
        assert query["client_id"] == "test-linkedin-client"
        state_value = query["state"]
        assert state_value.startswith("linkedin:")

        assert client.cookies.get("oauth_state_linkedin")

        callback_response = client.get(
            "/api/auth/oauth/linkedin/callback",
            params={"code": "linkedin-code", "state": state_value},
            allow_redirects=False,
        )
        assert callback_response.status_code == 302
        final_location = callback_response.headers["location"]
        assert final_location.startswith(
            settings.frontend_origin.rstrip("/") + "/auth/callback"
        )
        final_query = dict(parse_qsl(urlparse(final_location).query))
        assert final_query["code"] == "linkedin-code"
        assert final_query["state"] == state_value
        assert final_query["next"] == "/dashboard"

        set_cookie_header = callback_response.headers.get("set-cookie", "")
        assert "oauth_state_linkedin=" in set_cookie_header
        assert "Max-Age=0" in set_cookie_header
    finally:
        settings.linkedin_client_id = previous_client_id
        settings.linkedin_callback_url = previous_callback
        client.cookies.clear()


def test_google_oauth_start_json_mode(client):
    previous_client_id = settings.google_client_id
    previous_callback = settings.google_callback_url
    try:
        settings.google_client_id = "json-google-client"
        settings.google_callback_url = None

        response = client.get(
            "/api/auth/oauth/google/start",
            params={"next": "/dashboard", "format": "json"},
            headers={"accept": "application/json"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["provider"] == "google"
        assert payload["state"].startswith("google:")
        assert payload["authorization_url"].startswith(_GOOGLE_AUTH_ENDPOINT)
        assert payload["expires_in"] == _OAUTH_STATE_MAX_AGE

        assert client.cookies.get("oauth_state_google")
    finally:
        settings.google_client_id = previous_client_id
        settings.google_callback_url = previous_callback
        client.cookies.clear()


def test_linkedin_oauth_start_json_mode(client):
    previous_client_id = settings.linkedin_client_id
    previous_callback = settings.linkedin_callback_url
    try:
        settings.linkedin_client_id = "json-linkedin-client"
        settings.linkedin_callback_url = None

        response = client.get(
            "/api/auth/oauth/linkedin/start",
            params={"next": "/dashboard", "format": "json"},
            headers={"accept": "application/json"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["provider"] == "linkedin"
        assert payload["state"].startswith("linkedin:")
        assert payload["authorization_url"].startswith(_LINKEDIN_AUTH_ENDPOINT)
        assert payload["expires_in"] == _OAUTH_STATE_MAX_AGE

        assert client.cookies.get("oauth_state_linkedin")
    finally:
        settings.linkedin_client_id = previous_client_id
        settings.linkedin_callback_url = previous_callback
        client.cookies.clear()
