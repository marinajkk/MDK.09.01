from conftest import login, logout, post, register


def test_register_ok(client, app):
    resp = register(client)
    assert resp.status_code == 302
    assert app.users.by_login("marina_k")["role"] == "participant"


def test_register_short_password(client):
    resp = register(client, password="1234567")
    assert "не короче 8 символов" in resp.get_data(as_text=True)


def test_register_duplicate_login(client):
    register(client)
    resp = register(client)
    assert "уже занят" in resp.get_data(as_text=True)


def test_register_bad_phone_and_email(client):
    resp = register(client, phone="12345", email="без-собаки")
    html = resp.get_data(as_text=True)
    assert "Телефон:" in html and "name@example.ru" in html


def test_password_is_not_stored_in_clear(client, app):
    register(client)
    assert app.users.by_login("marina_k")["password_hash"] != "Parol2026"


def test_login_wrong_password(client):
    register(client)
    resp = login(client, password="неверный")
    assert "Неверный логин или пароль" in resp.get_data(as_text=True)


def test_create_request_and_see_it(client):
    register(client)
    login(client)
    post(client, "/requests/new", {"event_id": "1", "room": "Зал А", "payment": "Карта", "seats": "2"})
    html = client.get("/requests").get_data(as_text=True)
    assert "Цифровая школа" in html and "новая" in html


def test_request_requires_login(client):
    resp = client.get("/requests/new")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]


def test_admin_sees_all_requests(client):
    register(client)
    login(client)
    post(client, "/requests/new", {"event_id": "2", "room": "Зал Б", "payment": "Наличные", "seats": "1"})
    logout(client)
    login(client, "admin", "Admin2026!")
    html = client.get("/admin/").get_data(as_text=True)
    assert "Умный город" in html


def test_admin_forbidden_for_participant(client):
    register(client)
    login(client)
    assert client.get("/admin/").status_code == 403
