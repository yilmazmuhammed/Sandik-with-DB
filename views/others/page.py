from flask import redirect, url_for, render_template


def home_page():
    # return render_template("layout.html")
    return redirect(url_for('profile'))
