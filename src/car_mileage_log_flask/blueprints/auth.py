"""
Auth flask blueprint
"""

import os
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == os.getenv("AUTH_USERNAME") and password == os.getenv(
            "AUTH_PASSWORD"
        ):
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("auth.login"))
