from flask import Flask
from flask_login import LoginManager
from pony.flask import Pony

from views import others, webuser, backup, get_translation
from views.others import zoom_video_indir
from views.sandik.page import new_sandik_page, sandik_management_page, add_member_to_sandik_page, \
    select_member_to_edit_page, edit_member_of_sandik_page, add_share_to_member_page, members_page, \
    add_member_authority_type_to_sandik_page, add_debt_type_to_sandik_page, remove_member_of_sandik_page, \
    remove_share_of_member_page, edit_member_settings_in_the_sandik
from views.webuser.auxiliary import FlaskUser
from views.sandik.api import api_shares_of_member
import views.transaction.page as transaction_page

lm = LoginManager()


@lm.user_loader
def load_user(username):
    return FlaskUser(username)


def create_sandik_app():
    app = Flask(__name__)
    Pony(app)
    app.config.from_object("settings")

    # Normal kullanıcıların genel işlemleri
    app.add_url_rule("/signup", view_func=webuser.signup_page, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=webuser.login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=webuser.logout)
    app.add_url_rule("/profile", view_func=webuser.profile)
    app.add_url_rule("/", view_func=others.home_page)
    app.add_url_rule("/edit-webuser-info", view_func=webuser.edit_webuser_info_page, methods=["GET", "POST"])
    app.add_url_rule("/new-sandik", view_func=new_sandik_page, methods=["GET", "POST"])

    # Site yöneticisinin işlemleri
    app.add_url_rule("/add-webuser", view_func=webuser.add_webuser_page, methods=["GET", "POST"])
    app.add_url_rule("/export-all-data", view_func=backup.export_all_datas)
    app.add_url_rule("/import-all-data", view_func=backup.import_all_datas, methods=["GET", "POST"])
    app.add_url_rule("/@<string:username>/edit-webuser-info", view_func=webuser.edit_webuser_info_by_admin_page, methods=["GET", "POST"])

    # Sandık yöneticilerinin sandıkla ilgili işlemleri
    app.add_url_rule("/sandik/<int:sandik_id>/unconfirmed-transactions", view_func=transaction_page.unconfirmed_transactions_page)
    app.add_url_rule("/sandik/<int:sandik_id>/management-panel", view_func=sandik_management_page)
    app.add_url_rule("/sandik/<int:sandik_id>/add-member",
                     view_func=add_member_to_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/edit-member",
                     view_func=select_member_to_edit_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/edit-member/<string:username>",
                     view_func=edit_member_of_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/add-share",
                     view_func=add_share_to_member_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/members", view_func=members_page)
    app.add_url_rule("/sandik/<int:sandik_id>/add-custom-transaction",
                     view_func=transaction_page.add_custom_transaction_for_admin_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/transactions", view_func=transaction_page.transactions_page)
    app.add_url_rule("/sandik/<int:sandik_id>/transactions/<int:transaction_id>",
                     view_func=transaction_page.transaction_information_page)
    app.add_url_rule("/sandik/<int:sandik_id>/add-member-authority-type",
                     view_func=add_member_authority_type_to_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/add-debt-type",
                     view_func=add_debt_type_to_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/unpaid", view_func=transaction_page.unpaid_transactions_page)
    app.add_url_rule("/sandik/<int:sandik_id>/remove-member",
                     view_func=remove_member_of_sandik_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/remove-share",
                     view_func=remove_share_of_member_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/transactions/<int:transaction_id>/delete",
                     view_func=transaction_page.delete_transaction)
    app.add_url_rule("/sandik/<int:sandik_id>/transactions/<int:transaction_id>/confirm",
                     view_func=transaction_page.confirm_transaction)

    # Üyelerin sandıklarla ilgili işlemleri
    app.add_url_rule("/sandik/<int:sandik_id>/cm/transactions",
                     view_func=transaction_page.member_transactions_in_sandik_page)
    app.add_url_rule("/sandik/<int:sandik_id>/cm/add-contribution",
                     view_func=transaction_page.add_contribution_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/cm/add-debt",
                     view_func=transaction_page.add_debt_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/cm/add-payment",
                     view_func=transaction_page.add_payment_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/cm/add-transaction",
                     view_func=transaction_page.add_transaction_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/cm/fast-pay",
                     view_func=transaction_page.fast_pay_page, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/cm/unconfirmed-transactions",
                     view_func=transaction_page.member_unconfirmed_transactions_page)
    app.add_url_rule("/sandik/<int:sandik_id>/cm/unpaid", view_func=transaction_page.unpaid_transactions_of_member_page)
    app.add_url_rule("/sandik/<int:sandik_id>/cm/member_settings",
                     view_func=edit_member_settings_in_the_sandik, methods=["GET", "POST"])
    app.add_url_rule("/sandik/<int:sandik_id>/transactions/<int:transaction_id>/cm_delete",
                     view_func=transaction_page.member_delete_transaction)
    app.add_url_rule("/sandik/<int:sandik_id>/transactions/<int:transaction_id>/cm_confirm",
                     view_func=transaction_page.member_confirm_transaction)

    # Sandık harici şeyler
    app.add_url_rule("/zoom_video_indir", view_func=zoom_video_indir, methods=["GET", "POST"])

    # Herkesin yapabileceği işlemler
    app.add_url_rule("/set_language/<string:language>", view_func=others.set_language)

    # API
    app.add_url_rule("/api/member/<int:member_id>/shares", view_func=api_shares_of_member)



    lm.init_app(app)
    lm.login_view = "login_page"
    lm.login_message = get_translation()['views']['webuser']['login_page']['login_message']
    lm.login_message_category = 'danger'

    return app


sandik_app = create_sandik_app()

if __name__ == "__main__":
    port = sandik_app.config.get("PORT", 5000)
    sandik_app.run()
