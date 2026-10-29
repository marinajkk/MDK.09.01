import re

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "SECRET_KEY": "test", "DATABASE": str(tmp_path / "test.db")})
    app.users.create("admin", "Администратор портала", "Admin2026!", "admin@konferencii.test", "+79000000000", "admin")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def token(client, url="/login"):
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([0-9a-f]+)"', html).group(1)


def post(client, url, data, form_url=None):
    data = dict(data, csrf_token=token(client, form_url or url))
    return client.post(url, data=data)


def register(client, **extra):
    data = {"login": "marina_k", "full_name": "Хачатрян Марине Артаковна", "password": "Parol2026",
            "email": "marine@example.ru", "phone": "+79161234567"}
    data.update(extra)
    return post(client, "/register", data)


def login(client, login="marina_k", password="Parol2026"):
    return post(client, "/login", {"login": login, "password": password})


def logout(client):
    return post(client, "/logout", {}, "/")
