from conftest import login, post, register

REQUEST = {"event_id": "1", "room": "Малый зал", "payment": "Банковская карта", "seats": "2"}


def test_request_for_past_event_is_rejected(client, app):
    register(client)
    login(client)
    past = [e for e in app.events.all() if e["event_date"] < "9999"][-1]
    html = post(client, "/requests/new", dict(REQUEST, event_id=str(past["id"]))).get_data(as_text=True)
    assert "уже прошло" in html
    assert app.requests_repo.by_user(2) == []


def test_new_request_page_lists_only_upcoming_events(client):
    register(client)
    login(client)
    html = client.get("/requests/new").get_data(as_text=True)
    assert "Цифровая школа" in html
    assert "Данные и ИИ" not in html


def test_superscript_digit_in_seats_gives_error_not_500(client):
    register(client)
    login(client)
    resp = post(client, "/requests/new", dict(REQUEST, seats="²"))
    assert resp.status_code == 200
    assert "от 1 до 50" in resp.get_data(as_text=True)


def test_superscript_digit_in_admin_filter_does_not_crash(client):
    login(client, "admin", "Admin2026!")
    assert client.get("/admin/?event_id=²").status_code == 200


def test_superscript_digit_in_rating_gives_error_not_500(client, app):
    register(client)
    login(client)
    post(client, "/requests/new", REQUEST)
    app.requests_repo.set_status(1, "завершено")
    resp = post(client, "/requests/1/review", {"rating": "²", "body": "Нормальный отзыв"}, "/requests/1/review")
    assert resp.status_code == 200
