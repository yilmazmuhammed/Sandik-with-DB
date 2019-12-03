from flask import redirect, url_for, render_template, session, request

from views.others.auxiliary import set_translation


def home_page():
    # return render_template("layout.html")
    return redirect(url_for('profile'))


def set_language(language):
    session['language'] = language

    set_translation()

    next_page = request.args.get("next", url_for("home_page"))
    return redirect(next_page)