from flask import Flask
from flask_login import LoginManager

from views import others, sandik, transaction, webuser
from views.sandik import member as sandik_member
from views.webuser.auxiliary import FlaskUser

lm = LoginManager()


@lm.user_loader
def load_user(username):
    return FlaskUser(username)


def create_sandik_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    app.add_url_rule("/signup", view_func=webuser.signup, methods=["GET", "POST"])
    app.add_url_rule("/add-webuser", view_func=webuser.add_webuser, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=webuser.login, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=webuser.logout)
    app.add_url_rule("/profile", view_func=webuser.profile)
    app.add_url_rule("/", view_func=others.home_page)

    app.add_url_rule("/new-sandik", view_func=sandik.new_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/import-data", view_func=others.import_data, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/management-panel", view_func=sandik.sandik_management_page)
    app.add_url_rule("/sandik/<int:sandik_id>/add-member",
                     view_func=sandik_member.add_member_to_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/members", view_func=sandik_member.members_page)
    app.add_url_rule("/sandik/<int:sandik_id>/transactions", view_func=webuser.transactions_in_sandik)
    app.add_url_rule("/sandik/<int:sandik_id>/add-contribution",
                     view_func=transaction.add_contribution_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/add-debt", view_func=transaction.add_debt_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/add-payment",
                     view_func=transaction.add_payment_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/add-transaction",
                     view_func=transaction.add_transaction_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/add-custom-transaction",
                     view_func=transaction.add_custom_transaction_for_admin_page, methods=["GET", "POST"])

    lm.init_app(app)
    lm.login_view = "login"
    lm.login_message_category = 'danger'

    return app


sandik_app = create_sandik_app()

if __name__ == "__main__":
    port = sandik_app.config.get("PORT", 5000)
    sandik_app.run()
