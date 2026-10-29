import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    app.users.create("admin", "Администратор портала", "Admin2026!", "admin@konferencii.test", "+79000000000", "admin")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, **extra):
    data = {"login": "marina_k", "full_name": "Хачатрян Марине Артаковна", "password": "Parol2026",
            "email": "marine@example.ru", "phone": "+79161234567"}
    data.update(extra)
    return client.post("/register", data=data)


def login(client, login="marina_k", password="Parol2026"):
    return client.post("/login", data={"login": login, "password": password})
