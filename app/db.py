import os
import sqlite3
from datetime import date, timedelta

SCHEMA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.sql")

STATUSES = ["новая", "назначено", "завершено"]

DAY = date.today()

EVENTS = [
    ("Конференция «Цифровая школа»", DAY + timedelta(days=22), "Москва, ул. Тверская, 12", "Опыт внедрения электронных дневников и онлайн-курсов в школах и колледжах."),
    ("Форум «Умный город»", DAY + timedelta(days=36), "Казань, Кремлёвская, 8", "Транспорт, ЖКХ и городские сервисы: доклады и круглые столы."),
    ("Семинар по кибербезопасности", DAY + timedelta(days=47), "Санкт-Петербург, Невский пр., 30", "Защита учётных записей, резервное копирование и разбор реальных инцидентов."),
    ("Мастер-класс «Веб-разработка с нуля»", DAY - timedelta(days=19), "Екатеринбург, ул. Ленина, 5", "Практикум по вёрстке и серверной части для начинающих."),
    ("Конференция «Данные и ИИ»", DAY - timedelta(days=41), "Новосибирск, Красный пр., 51", "Анализ данных в бизнесе, примеры из банков и логистики."),
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
            con.executemany("INSERT INTO events (title, event_date, place, description) VALUES (?, ?, ?, ?)", [(t, d.isoformat(), p, o) for t, d, p, o in EVENTS])
        con.commit()
        con.close()
