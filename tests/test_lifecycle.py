from conftest import login, logout, post, register

REQUEST = {"event_id": "1", "room": "Малый зал", "payment": "Банковская карта", "seats": "2"}


def participant_with_request(client):
    register(client)
    login(client)
    post(client, "/requests/new", REQUEST)
    logout(client)


def as_admin(client):
    login(client, "admin", "Admin2026!")


def status(app, request_id=1):
    return app.requests_repo.get(request_id)["status"]


def test_admin_moves_status_forward(client, app):
    participant_with_request(client)
    as_admin(client)
    assert status(app) == "новая"
    post(client, "/admin/requests/1/next", {}, "/admin/")
    assert status(app) == "назначено"
    post(client, "/admin/requests/1/next", {}, "/admin/")
    assert status(app) == "завершено"


def test_completed_request_cannot_move_further(client, app):
    participant_with_request(client)
    as_admin(client)
    post(client, "/admin/requests/1/next", {}, "/admin/")
    post(client, "/admin/requests/1/next", {}, "/admin/")
    resp = post(client, "/admin/requests/1/next", {}, "/admin/")
    assert resp.status_code == 400
    assert status(app) == "завершено"


def test_participant_cannot_change_status(client, app):
    participant_with_request(client)
    login(client)
    resp = client.post("/admin/requests/1/next", data={})
    assert resp.status_code in (400, 403)
    assert status(app) == "новая"


def test_status_change_needs_csrf(client, app):
    participant_with_request(client)
    as_admin(client)
    assert client.post("/admin/requests/1/next", data={}).status_code == 400
    assert status(app) == "новая"


def test_unknown_request_gives_404(client):
    as_admin(client)
    assert post(client, "/admin/requests/99/next", {}, "/admin/").status_code == 404


def test_participant_edits_new_request(client, app):
    participant_with_request(client)
    login(client)
    post(client, "/requests/1/edit", {"room": "Переговорная", "payment": "Наличные на месте", "seats": "5"}, "/requests/1/edit")
    item = app.requests_repo.get(1)
    assert (item["room"], item["payment"], item["seats"]) == ("Переговорная", "Наличные на месте", 5)


def test_edit_validation(client, app):
    participant_with_request(client)
    login(client)
    html = post(client, "/requests/1/edit", {"room": "Подвал", "payment": "Банковская карта", "seats": "99"}, "/requests/1/edit").get_data(as_text=True)
    assert "из списка" in html and "от 1 до 50" in html
    assert app.requests_repo.get(1)["seats"] == 2


def test_assigned_request_cannot_be_edited_or_cancelled(client, app):
    participant_with_request(client)
    as_admin(client)
    post(client, "/admin/requests/1/next", {}, "/admin/")
    logout(client)
    login(client)
    assert client.get("/requests/1/edit").status_code == 403
    assert post(client, "/requests/1/delete", {}, "/requests").status_code == 403
    assert app.requests_repo.get(1) is not None


def test_participant_cancels_new_request(client, app):
    participant_with_request(client)
    login(client)
    post(client, "/requests/1/delete", {}, "/requests")
    assert app.requests_repo.get(1) is None


def test_cannot_touch_other_users_request(client):
    participant_with_request(client)
    register(client, login="other_user", email="o@example.ru", phone="+79170000000")
    login(client, "other_user")
    assert client.get("/requests/1/edit").status_code == 404
    assert post(client, "/requests/1/delete", {}, "/requests").status_code == 404


def test_admin_deletes_request_with_review(client, app):
    participant_with_request(client)
    as_admin(client)
    post(client, "/admin/requests/1/next", {}, "/admin/")
    post(client, "/admin/requests/1/next", {}, "/admin/")
    logout(client)
    login(client)
    post(client, "/requests/1/review", {"rating": "5", "body": "Всё прошло хорошо"}, "/requests/1/review")
    logout(client)
    as_admin(client)
    post(client, "/admin/requests/1/delete", {}, "/admin/")
    assert app.requests_repo.get(1) is None
    assert app.reviews.by_request(1) is None


def test_full_cycle_new_assigned_done_review(client, app):
    participant_with_request(client)
    as_admin(client)
    post(client, "/admin/requests/1/next", {}, "/admin/")
    post(client, "/admin/requests/1/next", {}, "/admin/")
    logout(client)
    login(client)
    assert "Оставить отзыв" in client.get("/requests").get_data(as_text=True)
    post(client, "/requests/1/review", {"rating": "4", "body": "Было интересно и полезно"}, "/requests/1/review")
    assert app.reviews.by_request(1)["rating"] == 4
