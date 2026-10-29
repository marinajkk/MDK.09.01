import re
from datetime import date

CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
SPACES_RE = re.compile(r"[ \t]+")


def clean(value, limit=200):
    value = CONTROL_RE.sub("", value or "")
    return SPACES_RE.sub(" ", value).strip()[:limit]


INT_RE = re.compile(r"^[0-9]{1,9}$")


def to_int(value):
    value = (value or "").strip()
    return int(value) if INT_RE.match(value) else None


LOGIN_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^(\+7|8)\d{10}$")


ROOMS = ["Малый зал", "Большой зал", "Конференц-зал", "Переговорная"]
PAYMENTS = ["Банковская карта", "Наличные на месте", "Перевод по счёту"]


class FormValidator:
    def __init__(self, data):
        self.data = data
        self.errors = {}

    def field(self, name):
        return clean(self.data.get(name))

    def fail(self, name, text):
        self.errors.setdefault(name, text)

    @property
    def ok(self):
        return not self.errors


class RegisterForm(FormValidator):
    def __init__(self, data, users):
        super().__init__(data)
        self.users = users
        self.check()

    def check(self):
        login = self.field("login")
        if not LOGIN_RE.match(login):
            self.fail("login", "Логин: 3-20 символов, латиница, цифры и подчёркивание")
        elif self.users.by_login(login):
            self.fail("login", "Такой логин уже занят")
        if len(self.field("full_name")) < 5:
            self.fail("full_name", "Введите фамилию, имя и отчество")
        if not 8 <= len(self.data.get("password") or "") <= 128:
            self.fail("password", "Пароль должен быть не короче 8 символов (не больше 128)")
        if not EMAIL_RE.match(self.field("email")):
            self.fail("email", "Введите почту в формате name@example.ru")
        phone = self.field("phone").replace(" ", "").replace("-", "")
        if not PHONE_RE.match(phone):
            self.fail("phone", "Телефон: +7XXXXXXXXXX или 8XXXXXXXXXX")


class RequestForm(FormValidator):
    def __init__(self, data, events):
        super().__init__(data)
        self.events = events
        self.check()

    def check(self):
        event = self.events.get(to_int(self.field("event_id")) or 0)
        if not event:
            self.fail("event_id", "Выберите мероприятие")
        elif event["event_date"] < date.today().isoformat():
            self.fail("event_id", "Это мероприятие уже прошло")
        if self.field("room") not in ROOMS:
            self.fail("room", "Выберите помещение из списка")
        if self.field("payment") not in PAYMENTS:
            self.fail("payment", "Выберите способ оплаты из списка")
        seats = to_int(self.field("seats"))
        if seats is None or not 1 <= seats <= 50:
            self.fail("seats", "Количество мест: от 1 до 50")


class EditRequestForm(FormValidator):
    def __init__(self, data):
        super().__init__(data)
        if self.field("room") not in ROOMS:
            self.fail("room", "Выберите помещение из списка")
        if self.field("payment") not in PAYMENTS:
            self.fail("payment", "Выберите способ оплаты из списка")
        seats = to_int(self.field("seats"))
        if seats is None or not 1 <= seats <= 50:
            self.fail("seats", "Количество мест: от 1 до 50")


class ReviewForm(FormValidator):
    def __init__(self, data):
        super().__init__(data)
        rating = to_int(self.field("rating"))
        if rating is None or not 1 <= rating <= 5:
            self.fail("rating", "Поставьте оценку от 1 до 5")
        if len(self.field("body")) < 10:
            self.fail("body", "Напишите отзыв не короче 10 символов")
