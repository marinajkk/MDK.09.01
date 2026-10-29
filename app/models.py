from werkzeug.security import generate_password_hash, check_password_hash


class UserRepository:
    def __init__(self, db):
        self.db = db

    def create(self, login, full_name, password, email, phone, role="participant"):
        return self.db.execute(
            "INSERT INTO users (login, full_name, password_hash, email, phone, role) VALUES (?, ?, ?, ?, ?, ?)",
            (login, full_name, generate_password_hash(password), email, phone, role),
        )

    def by_login(self, login):
        return self.db.one("SELECT * FROM users WHERE login = ?", (login,))

    def by_id(self, user_id):
        return self.db.one("SELECT * FROM users WHERE id = ?", (user_id,))

    def authenticate(self, login, password):
        user = self.by_login(login)
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None


class EventRepository:
    def __init__(self, db):
        self.db = db

    def all(self):
        return self.db.query("SELECT * FROM events ORDER BY event_date")

    def get(self, event_id):
        return self.db.one("SELECT * FROM events WHERE id = ?", (event_id,))


class RequestRepository:
    BASE = (
        "SELECT r.*, e.title AS event_title, e.event_date, s.name AS status, u.full_name AS user_name "
        "FROM requests r JOIN events e ON e.id = r.event_id JOIN statuses s ON s.id = r.status_id "
        "JOIN users u ON u.id = r.user_id "
    )

    def __init__(self, db):
        self.db = db

    def create(self, user_id, event_id, room, payment, seats):
        status = self.db.one("SELECT id FROM statuses WHERE name = 'новая'")
        return self.db.execute(
            "INSERT INTO requests (user_id, event_id, status_id, room, payment, seats) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, event_id, status["id"], room, payment, seats),
        )

    def by_user(self, user_id):
        return self.db.query(self.BASE + "WHERE r.user_id = ? ORDER BY r.id DESC", (user_id,))

    def all(self):
        return self.db.query(self.BASE + "ORDER BY r.id DESC")
