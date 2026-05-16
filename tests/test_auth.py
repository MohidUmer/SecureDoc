"""Basic auth flow smoke tests."""
from __future__ import annotations


def test_register_and_login(client):
    r = client.get("/auth/register")
    assert r.status_code == 200
    client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "longpassword1",
            "submit": "Register",
        },
        follow_redirects=True,
    )
    r2 = client.post(
        "/auth/login",
        data={
            "username": "newuser",
            "password": "longpassword1",
            "submit": "Login",
        },
        follow_redirects=False,
    )
    assert r2.status_code in (302, 303)


def test_wrong_password_shows_generic_error(client):
    client.post(
        "/auth/register",
        data={
            "username": "wrongpass_user",
            "email": "wrongpass_user@example.com",
            "password": "CorrectPassword1",
            "submit": "Register",
        },
        follow_redirects=True,
    )
    r = client.post(
        "/auth/login",
        data={
            "username": "wrongpass_user",
            "password": "IncorrectPassword1",
            "submit": "Login",
        },
        follow_redirects=True,
    )
    body = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Invalid username or password." in body
