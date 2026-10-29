from conftest import login, logout, post, register

REQUEST = {"event_id": "1", "room": "Малый зал", "payment": "Банковская карта", "seats": "2"}


def make_request(client, **extra):
    return post(client, "/requests/new", dict(REQUEST, **extra))


def finish(app, request_id=1):
    app.db.execute("UPDATE requests SET status_id = (SELECT id FROM statuses WHERE name = 'завершено') WHERE id = ?", (request_id,))


def test_room_outside_list_is_rejected(client):
    register(client)
    login(client)
    html = make_request(client, room="Подвал").get_data(as_text=True)
    assert "Выберите помещение из списка" in html


def test_payment_outside_list_is_rejected(client):
    register(client)
    login(client)
    html = make_request(client, payment="Биткоины").get_data(as_text=True)
    assert "Выберите способ оплаты из списка" in html


def test_form_keeps_entered_values_after_error(client):
    register(client)
    login(client)
    html = make_request(client, seats="0", room="Большой зал").get_data(as_text=True)
    assert "от 1 до 50" in html
    assert "<option selected>Большой зал</option>" in html


def test_review_not_available_before_finish(client):
    register(client)
    login(client)
    make_request(client)
    assert client.get("/requests/1/review").status_code == 403
    resp = post(client, "/requests/1/review", {"rating": "5", "body": "Очень понравилось"}, "/requests")
    assert resp.status_code in (400, 403)


def test_review_after_finish(client, app):
    register(client)
    login(client)
    make_request(client)
    finish(app)
    assert "Оставить отзыв" in client.get("/requests").get_data(as_text=True)
    post(client, "/requests/1/review", {"rating": "5", "body": "Очень понравилось, всё чётко"}, "/requests/1/review")
    assert "Отзыв отправлен" in client.get("/requests").get_data(as_text=True)
    assert "Очень понравилось" in client.get("/events/1").get_data(as_text=True)


def test_only_one_review_per_request(client, app):
    register(client)
    login(client)
    make_request(client)
    finish(app)
    data = {"rating": "4", "body": "Хорошая конференция"}
    post(client, "/requests/1/review", data, "/requests/1/review")
    post(client, "/requests/1/review", data, "/requests")
    assert len(app.reviews.by_event(1)) == 1


def test_review_validation(client, app):
    register(client)
    login(client)
    make_request(client)
    finish(app)
    html = post(client, "/requests/1/review", {"rating": "9", "body": "ок"}, "/requests/1/review").get_data(as_text=True)
    assert "от 1 до 5" in html and "не короче 10" in html


def test_cannot_review_someone_elses_request(client, app):
    register(client)
    login(client)
    make_request(client)
    finish(app)
    logout(client)
    register(client, login="other_user", email="o@example.ru", phone="+79170000000")
    login(client, "other_user")
    assert client.get("/requests/1/review").status_code == 404


def test_admin_filters(client, app):
    register(client)
    login(client)
    make_request(client)
    make_request(client, event_id="2")
    finish(app, 2)
    logout(client)
    login(client, "admin", "Admin2026!")
    assert "Найдено заявок: 2" in client.get("/admin/").get_data(as_text=True)
    assert "Найдено заявок: 1" in client.get("/admin/?status=завершено").get_data(as_text=True)
    assert "Найдено заявок: 1" in client.get("/admin/?event_id=1").get_data(as_text=True)
    assert "Найдено заявок: 2" in client.get("/admin/?q=Хачатрян").get_data(as_text=True)
    assert "Найдено заявок: 0" in client.get("/admin/?q=Иванов").get_data(as_text=True)


def test_admin_filter_ignores_garbage(client):
    login(client, "admin", "Admin2026!")
    assert client.get("/admin/?status=x'--&event_id=abc&q=%27%20OR%201=1").status_code == 200
