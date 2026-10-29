from conftest import login, logout, post, register, token


def test_post_without_csrf_token_is_rejected(client):
    resp = client.post("/login", data={"login": "admin", "password": "Admin2026!"})
    assert resp.status_code == 400


def test_post_with_wrong_csrf_token_is_rejected(client):
    token(client)
    resp = client.post("/login", data={"login": "admin", "password": "Admin2026!", "csrf_token": "00"})
    assert resp.status_code == 400


def test_sql_injection_in_login(client):
    resp = login(client, "admin' OR '1'='1", "что-угодно")
    assert "Неверный логин или пароль" in resp.get_data(as_text=True)
    assert client.get("/admin/").status_code == 302


def test_sql_injection_in_registration(client, app):
    register(client, login="x'); DROP TABLE users;--")
    assert app.users.by_login("admin") is not None


def test_guest_cannot_open_requests(client):
    assert client.get("/requests").status_code == 302
    assert client.get("/admin/").status_code == 302


def test_participant_cannot_open_admin(client):
    register(client)
    login(client)
    assert client.get("/admin/").status_code == 403


def test_user_sees_only_own_requests(client):
    register(client)
    login(client)
    post(client, "/requests/new", {"event_id": "1", "room": "Зал А", "payment": "Карта", "seats": "1"})
    logout(client)
    register(client, login="other_user", email="other@example.ru", phone="+79170000000")
    login(client, "other_user")
    assert "Цифровая школа" not in client.get("/requests").get_data(as_text=True)


def test_session_cookie_flags(client):
    register(client)
    resp = login(client)
    cookie = resp.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


def test_security_headers(client):
    resp = client.get("/")
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in resp.headers["Content-Security-Policy"]


def test_login_locked_after_five_failures(client):
    register(client)
    for _ in range(5):
        login(client, password="неверный1")
    resp = login(client)
    assert resp.status_code == 429


def test_html_in_form_is_escaped(client):
    register(client, full_name="<script>alert(1)</script> Иванов")
    login(client)
    html = client.get("/requests").get_data(as_text=True)
    assert "<script>alert(1)" not in html


def test_logout_by_get_is_not_allowed(client):
    assert client.get("/logout").status_code == 405
