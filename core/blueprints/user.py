import json

from flask import redirect, url_for, Blueprint, request, render_template
from flask_login import LoginManager
from flask_login import current_user, login_user, logout_user
from functools import wraps

from core.models import User

user_blueprint = Blueprint("user_blueprint", __name__, url_prefix="/user")

login_manager = LoginManager()
login_manager.login_view = "user_blueprint.login"


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        data = {
            "password": request.form["password"],
            "username": request.form["username"],
            "remember_me": request.form.get("remember_me", False),
        }
        password = data["password"]
        username = data["username"]
        remember_me = data["remember_me"]
        user = User.query.filter(User.username == username).first()
        if user is None or not user.check_password(password):
            return redirect(url_for("user_blueprint.login"))
        else:
            login_user(user, remember=remember_me)
            return redirect("/")
    else:
        return render_template("login.html")


@user_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("user_blueprint.login"))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role != role and role != "ANY":
                return login_manager.unauthorized()
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper
