from flask import redirect, url_for, render_template, session, request

from views.others.auxiliary import set_translation, get_translation


def home_page():
    # return render_template("layout.html")
    return redirect(url_for('profile'))


def set_language(language):
    session['language'] = language

    set_translation()

    next_page = request.args.get("next", url_for("home_page"))
    return redirect(next_page)


def zoom_video_indir():
    return render_template("zoom_video_indir.html", layout_page={'title': "Zoom Video İndir", "translation": get_translation()})
