from flask import render_template
from flask_login import current_user


def home_page():
    if current_user.is_authenticated:
        print("Giriş yapıldı")
    else:
        print("Giriş yapılamadı, anonim kullanıcı")
    return render_template("layout.html")