from flask import Flask
from flask_login import LoginManager

from views import webuser
from database.dbinit import WebUser

lm = LoginManager()


@lm.user_loader
def load_user(username):
    return WebUser.get(username=username)


def create_sandik_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    app.add_url_rule("/signup", view_func=webuser.signup_page, methods=["GET", "POST"])
    # app.add_url_rule("/login", view_func=webuser.login_page, methods=["GET", "POST"])
    # app.add_url_rule("/logout", view_func=webuser.logout_page)

    lm.init_app(app)
    lm.login_view = "login_page"


    return app


sandik_app = create_sandik_app()

if __name__ == "__main__":
    port = sandik_app.config.get("PORT", 5000)
    sandik_app.run()
