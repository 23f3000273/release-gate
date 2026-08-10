import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def safe_payload():
    return {
        "target": "preview",
        "event": "pull_request",
        "ref": "refs/heads/feature",
        "workflow": {
            "trigger": "pull_request",
            "permissions": {
                "contents": "read",
                "packages": "write",
                "id-token": "none"
            },
            "testsPassed": True,
            "matrixComplete": True,
            "failFast": False,
            "actions": [
                {
                    "owner": "actions",
                    "name": "checkout",
                    "ref": "v4"
                },
                {
                    "owner": "docker",
                    "name": "setup-buildx-action",
                    "ref": "0123456789abcdef0123456789abcdef01234567"
                }
            ]
        },
        "image": {
            "multiStage": True,
            "runsAsRoot": False,
            "secretMode": "none",
            "criticalVulnerabilities": 0,
            "digestPinned": True
        }
    }


def test_safe_request(client):
    response = client.post("/release-gate", json=safe_payload())

    assert response.status_code == 200
    assert response.get_json() == {
        "decision": "promote",
        "violations": []
    }


def test_excess_permission(client):
    payload = safe_payload()
    payload["workflow"]["permissions"]["issues"] = "write"

    body = client.post(
        "/release-gate",
        json=payload
    ).get_json()

    assert body["decision"] == "block"
    assert "EXCESS_PERMISSION" in body["violations"]


def test_unsafe_pr_trigger(client):
    payload = safe_payload()
    payload["workflow"]["trigger"] = "pull_request_target"

    body = client.post(
        "/release-gate",
        json=payload
    ).get_json()

    assert body["decision"] == "block"
    assert "UNSAFE_PR_TRIGGER" in body["violations"]


def test_incomplete_tests(client):
    payload = safe_payload()
    payload["workflow"]["testsPassed"] = False

    body = client.post(
        "/release-gate",
        json=payload
    ).get_json()

    assert body["decision"] == "block"
    assert "TESTS_INCOMPLETE" in body["violations"]


def test_root_runtime(client):
    payload = safe_payload()
    payload["image"]["runsAsRoot"] = True

    body = client.post(
        "/release-gate",
        json=payload
    ).get_json()

    assert body["decision"] == "block"
    assert "ROOT_RUNTIME" in body["violations"]


def test_production_approval(client):
    payload = safe_payload()

    payload["target"] = "production"
    payload["event"] = "push"
    payload["ref"] = "refs/heads/main"

    body = client.post(
        "/release-gate",
        json=payload
    ).get_json()

    assert body["decision"] == "block"
    assert "APPROVAL_REQUIRED" in body["violations"]
