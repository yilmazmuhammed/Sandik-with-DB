from flask import render_template


def home_page():
    return render_template("layout.html")

