import re

CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
SPACES_RE = re.compile(r"[ \t]+")


def clean(value, limit=200):
    value = CONTROL_RE.sub("", value or "")
    return SPACES_RE.sub(" ", value).strip()[:limit]


LOGIN_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^(\+7|8)\d{10}$")


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
        event_id = self.field("event_id")
        if not event_id.isdigit() or not self.events.get(int(event_id)):
            self.fail("event_id", "Выберите мероприятие")
        if len(self.field("room")) < 2:
            self.fail("room", "Укажите помещение")
        if len(self.field("payment")) < 2:
            self.fail("payment", "Укажите способ оплаты")
        seats = self.field("seats")
        if not seats.isdigit() or not 1 <= int(seats) <= 50:
            self.fail("seats", "Количество мест: от 1 до 50")
