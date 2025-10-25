import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import agents_tooling as tooling  # noqa: E402


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("HEROKU_API_KEY", raising=False)
    monkeypatch.delenv("HEROKU_APP_NAME", raising=False)


def test_find_agent_returns_expected_agent():
    path, agent = tooling.find_agent("deployer-stg")
    assert path.name == "agent.yaml"
    assert agent["name"] == "deployer-stg"
    assert agent["role"].startswith("Deploy AutoLocal")


def test_prepare_adapters_flags_missing_env():
    _, agent = tooling.find_agent("deployer-stg")
    adapters = tooling.prepare_adapters(agent, "dev")
    assert [entry[0] for entry in adapters] == ["github", "heroku"]

    github_adapter = adapters[0][3]
    heroku_adapter = adapters[1][3]

    assert "GH_TOKEN" in github_adapter.verify_env()
    assert set(["HEROKU_API_KEY", "HEROKU_APP_NAME"]).issubset(
        heroku_adapter.verify_env()
    )


@pytest.mark.parametrize("status_code", [200, 503, -1])
def test_http_adapter_handles_probe(monkeypatch, status_code):
    _, agent = tooling.find_agent("health-checker")
    adapters = tooling.prepare_adapters(agent, "dev")
    http_adapter = adapters[0][3]

    class FakeResponse:
        def __init__(self, code: int):
            self.status = code

        def read(self):
            if self.status == 200:
                return b'{"status": "ok"}'
            return b"service unavailable"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(url, timeout):
        assert url.endswith("/api/health")
        if status_code == -1:
            raise urllib.error.URLError("blocked")
        return FakeResponse(status_code)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = http_adapter.run("Check health")
    assert result["status"] == "checked"

    for probe in result["probes"]:
        if "*" in probe["host"]:
            assert probe["status"] == "skipped"
        else:
            if status_code == 200:
                assert probe["status"] in {"ok", "error"}
            elif status_code == 503:
                assert probe["status"] in {"warn", "error"}
            else:
                assert probe["status"] == "error"


def test_prepare_adapters_raises_for_missing_config():
    agent = {
        "name": "custom",
        "tools": [
            {"id": "github", "config_ref": "does-not-exist"},
        ],
    }
    with pytest.raises(SystemExit) as exc:
        tooling.prepare_adapters(agent, "dev")
    assert "does-not-exist" in str(exc.value)
