from flask import Flask
from flask_login import LoginManager

from views import others, sandik, webuser
from views.webuser.auxiliary import FlaskUser
import views.transaction.page as transaction_page

lm = LoginManager()


@lm.user_loader
def load_user(username):
    return FlaskUser(username)


def create_sandik_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    # Normal kullanıcıların genel işlemleri
    app.add_url_rule("/signup", view_func=webuser.signup, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=webuser.login, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=webuser.logout)
    app.add_url_rule("/profile", view_func=webuser.profile)
    app.add_url_rule("/", view_func=others.home_page)

    # Site yöneticisinin işlemleri
    app.add_url_rule("/add-webuser", view_func=webuser.add_webuser_page, methods=["GET", "POST"])

    # Sandık yöneticilerin sandıkla ilgili işlemleri
    app.add_url_rule("/new-sandik", view_func=sandik.new_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/import-data", view_func=others.import_data, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/management-panel", view_func=sandik.sandik_management_page)
    app.add_url_rule("/sandik/<int:sandik_id>/add-member",
                     view_func=sandik.add_member_to_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/members", view_func=sandik.members_page)
    app.add_url_rule("/sandik/<int:sandik_id>/add-custom-transaction",
                     view_func=transaction_page.add_custom_transaction_for_admin_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/transactions", view_func=sandik.transactions_page)
    app.add_url_rule("/sandik/<int:sandik_id>/export-csv", view_func=transaction_page.csv_raw_transactions_page)

    # Üyelerin sandıklarla ilgili işlemleri
    app.add_url_rule("/sandik/<int:sandik_id>/cm/transactions", view_func=webuser.transactions_in_sandik)
    app.add_url_rule("/sandik/<int:sandik_id>/cm/add-contribution",
                     view_func=transaction_page.add_contribution_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/cm/add-debt",
                     view_func=transaction_page.add_debt_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/cm/add-payment",
                     view_func=transaction_page.add_payment_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/cm/add-transaction",
                     view_func=transaction_page.add_transaction_page, methods=["GET", "POST"])

    lm.init_app(app)
    lm.login_view = "login"
    lm.login_message_category = 'danger'

    return app


sandik_app = create_sandik_app()

if __name__ == "__main__":
    port = sandik_app.config.get("PORT", 5000)
    sandik_app.run()
