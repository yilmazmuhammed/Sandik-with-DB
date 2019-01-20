# TODO Flash mesajlarını layout dışından değiştir, eğer form sayfası ise form başlığı altında göster
# TODO Members sayfasında üyelere tıklanınca altta hisseleri açılsın

from flask import Flask
from flask_login import LoginManager

from views import webuser, others, sandik
from views.webuser import FlaskUser
from views.sandik import member
from views import asa

lm = LoginManager()


@lm.user_loader
def load_user(username):
    return FlaskUser(username)


def create_sandik_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    app.add_url_rule("/signup", view_func=webuser.signup_page, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=webuser.login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=webuser.logout_page)
    app.add_url_rule("/", view_func=others.home_page)

    app.add_url_rule("/new-sandik", view_func=sandik.new_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/management-panel", view_func=sandik.sandik_management_page)
    app.add_url_rule("/sandik/<int:sandik_id>/add-member", view_func=member.add_member_to_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/members", view_func=member.members_page)

    lm.init_app(app)
    lm.login_view = "webuser.login_page"

    return app


sandik_app = create_sandik_app()

if __name__ == "__main__":
    port = sandik_app.config.get("PORT", 5000)
    sandik_app.run()
