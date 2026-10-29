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
        return self.db.query("SELECT * FROM events ORDER BY event_date < date('now', 'localtime'), event_date")

    def upcoming(self):
        return self.db.query("SELECT * FROM events WHERE event_date >= date('now', 'localtime') ORDER BY event_date")

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
        return self.db.query(
            "SELECT * FROM (" + self.BASE + ") q LEFT JOIN (SELECT request_id AS reviewed_id FROM reviews) rv ON rv.reviewed_id = q.id "
            "WHERE q.user_id = ? ORDER BY q.id DESC", (user_id,))

    def get(self, request_id):
        return self.db.one(self.BASE + "WHERE r.id = ?", (request_id,))

    FLOW = {"новая": "назначено", "назначено": "завершено"}

    def set_status(self, request_id, name):
        status = self.db.one("SELECT id FROM statuses WHERE name = ?", (name,))
        self.db.execute("UPDATE requests SET status_id = ? WHERE id = ?", (status["id"], request_id))

    def update(self, request_id, room, payment, seats):
        self.db.execute("UPDATE requests SET room = ?, payment = ?, seats = ? WHERE id = ?", (room, payment, seats, request_id))

    def delete(self, request_id):
        con = self.db.connect()
        try:
            con.execute("DELETE FROM reviews WHERE request_id = ?", (request_id,))
            con.execute("DELETE FROM requests WHERE id = ?", (request_id,))
            con.commit()
        finally:
            con.close()

    def all(self, status=None, event_id=None, search=None):
        sql, args, where = self.BASE, [], []
        if status:
            where.append("s.name = ?")
            args.append(status)
        if event_id:
            where.append("r.event_id = ?")
            args.append(event_id)
        if search:
            where.append("u.full_name LIKE ?")
            args.append("%" + search + "%")
        if where:
            sql += "WHERE " + " AND ".join(where) + " "
        return self.db.query(sql + "ORDER BY r.id DESC", args)


class ReviewRepository:
    def __init__(self, db):
        self.db = db

    def create(self, request_id, body, rating):
        return self.db.execute("INSERT INTO reviews (request_id, body, rating) VALUES (?, ?, ?)", (request_id, body, rating))

    def by_request(self, request_id):
        return self.db.one("SELECT * FROM reviews WHERE request_id = ?", (request_id,))

    def by_event(self, event_id):
        return self.db.query(
            "SELECT rv.*, u.full_name FROM reviews rv JOIN requests r ON r.id = rv.request_id "
            "JOIN users u ON u.id = r.user_id WHERE r.event_id = ? ORDER BY rv.id DESC", (event_id,))
