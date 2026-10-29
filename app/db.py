import os
import sqlite3

SCHEMA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.sql")

STATUSES = ["новая", "назначено", "завершено"]

EVENTS = [
    ("Конференция «Цифровая школа»", "2026-11-20", "Москва, ул. Тверская, 12", "Опыт внедрения электронных дневников и онлайн-курсов в школах и колледжах."),
    ("Форум «Умный город»", "2026-12-04", "Казань, Кремлёвская, 8", "Транспорт, ЖКХ и городские сервисы: доклады и круглые столы."),
    ("Семинар по кибербезопасности", "2026-12-15", "Санкт-Петербург, Невский пр., 30", "Защита учётных записей, резервное копирование и разбор реальных инцидентов."),
    ("Мастер-класс «Веб-разработка с нуля»", "2026-10-10", "Екатеринбург, ул. Ленина, 5", "Практикум по вёрстке и серверной части для начинающих."),
    ("Конференция «Данные и ИИ»", "2026-09-18", "Новосибирск, Красный пр., 51", "Анализ данных в бизнесе, примеры из банков и логистики."),
]


class Database:
    def __init__(self, path):
        self.path = path

    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def query(self, sql, args=()):
        con = self.connect()
        try:
            return con.execute(sql, args).fetchall()
        finally:
            con.close()

    def one(self, sql, args=()):
        rows = self.query(sql, args)
        return rows[0] if rows else None

    def execute(self, sql, args=()):
        con = self.connect()
        try:
            cur = con.execute(sql, args)
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def init(self):
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        con = self.connect()
        with open(SCHEMA, encoding="utf-8") as f:
            con.executescript(f.read())
        if con.execute("SELECT COUNT(*) FROM statuses").fetchone()[0] == 0:
            con.executemany("INSERT INTO statuses (name) VALUES (?)", [(s,) for s in STATUSES])
        if con.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
            con.executemany("INSERT INTO events (title, event_date, place, description) VALUES (?, ?, ?, ?)", EVENTS)
        con.commit()
        con.close()
