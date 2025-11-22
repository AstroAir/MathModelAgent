import pytest


@pytest.fixture(autouse=True)
def _temp_settings_file(tmp_path, monkeypatch):
    """Redirect settings file to a temporary path for tests."""
    from app.routers import settings_router

    temp_file = tmp_path / "user_settings.json"
    monkeypatch.setattr(settings_router, "SETTINGS_FILE", str(temp_file))


@pytest.mark.asyncio
async def test_profile_crud(async_client):
    # get default profile
    resp = await async_client.get("/api/settings/profile")
    assert resp.status_code == 200
    profile = resp.json()
    assert "email" in profile

    # update profile
    profile["name"] = "Test User"
    resp = await async_client.put("/api/settings/profile", json=profile)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_notifications_privacy_and_reset(async_client):
    # get notifications
    resp = await async_client.get("/api/settings/notifications")
    assert resp.status_code == 200

    # update notifications
    body = resp.json()
    body["email_enabled"] = False
    resp = await async_client.put("/api/settings/notifications", json=body)
    assert resp.status_code == 200

    # privacy
    resp = await async_client.get("/api/settings/privacy")
    assert resp.status_code == 200
    privacy = resp.json()
    privacy["data_collection"] = False
    resp = await async_client.put("/api/settings/privacy", json=privacy)
    assert resp.status_code == 200

    # reset
    resp = await async_client.post("/api/settings/reset")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_password_and_account_deletion(async_client):
    # change password
    resp = await async_client.post(
        "/api/settings/password/change",
        json={
            "current_password": "oldpassword",
            "new_password": "newpassword",
            "confirm_password": "newpassword",
        },
    )
    assert resp.status_code == 200

    # invalid confirmation text
    resp = await async_client.post(
        "/api/settings/account/delete",
        json={"password": "x", "confirmation_text": "WRONG"},
    )
    assert resp.status_code == 400

    # valid deletion request
    resp = await async_client.post(
        "/api/settings/account/delete",
        json={"password": "x", "confirmation_text": "DELETE"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sessions_and_2fa(async_client):
    # get 2fa status
    resp = await async_client.get("/api/settings/security/2fa")
    assert resp.status_code == 200

    # update 2fa
    resp = await async_client.put(
        "/api/settings/security/2fa",
        json={"enabled": True, "method": "sms"},
    )
    assert resp.status_code == 200

    # get sessions
    resp = await async_client.get("/api/settings/security/sessions")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)

    # revoke one session (mocked list ensures id exists)
    session_id = data[0]["session_id"]
    resp = await async_client.delete(f"/api/settings/security/sessions/{session_id}")
    assert resp.status_code == 200
