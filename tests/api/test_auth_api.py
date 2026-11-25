"""Token-authenticated Toolshop API checks using an account created for this run."""

import pytest
from playwright.sync_api import APIRequestContext

from tests.conftest import RegisteredUser


@pytest.mark.api
def test_current_user_endpoint_rejects_missing_bearer_token(
    api_context: APIRequestContext,
) -> None:
    """TC_API_05a: GET /users/me follows the documented 401 unauthenticated contract."""

    response = api_context.get("/users/me")

    assert response.status == 401, response.text()


@pytest.mark.api
def test_registered_user_token_authenticates_current_user_endpoint(
    api_context: APIRequestContext, registered_user: RegisteredUser
) -> None:
    """TC_API_05b: a private API-created user can log in and call GET /users/me."""

    login_response = api_context.post(
        "/users/login",
        data={"email": registered_user.email, "password": registered_user.password},
    )
    assert login_response.status == 200, login_response.text()
    token_payload = login_response.json()
    access_token = token_payload.get("access_token")
    token_type = token_payload.get("token_type")
    assert isinstance(access_token, str) and access_token, token_payload
    assert isinstance(token_type, str) and token_type.casefold() == "bearer", token_payload
    assert isinstance(token_payload.get("expires_in"), (int, float)), token_payload

    response = api_context.get(
        "/users/me", headers={"Authorization": f"{token_type} {access_token}"}
    )
    assert response.status == 200, response.text()
    profile = response.json()
    assert isinstance(profile, dict), profile
    assert isinstance(profile.get("id"), str) and profile["id"], profile
    assert profile.get("email") == registered_user.email, profile
