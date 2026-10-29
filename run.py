import sys

from app import create_app

app = create_app()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create-admin":
        login, password = sys.argv[2], sys.argv[3]
        if not app.users.by_login(login):
            app.users.create(login, "Администратор портала", password, "admin@konferencii.test", "+79000000000", "admin")
            print("Администратор создан")
        else:
            print("Такой логин уже есть")
    else:
        app.run(host="127.0.0.1", port=5000, debug=False)
