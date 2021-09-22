from flask import (
    Blueprint,
    request,
    session,
)
from flask_login import LoginManager
from flask_login import current_user, login_user, logout_user
from functools import wraps

from core.consts import ROLES_PRIORITY
from core.models import User

user_blueprint = Blueprint("user_blueprint", __name__, url_prefix="/user")

login_manager = LoginManager()
login_manager.login_view = "user_blueprint.login"


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    data = request.get_json(force=True)
    if current_user.is_authenticated:
        _user = current_user.as_dict()
        _user.pop("password_hash")
        return {"code": 200, "user": _user}
    if request.method == "POST":
        data = {
            "password": data["password"],
            "username": data["username"],
        }
        password = data["password"]
        username = data["username"]
        user = User.query.filter(User.username == username).first()

        if user is None or not user.check_password(password):
            return {"code": 404}
        else:
            print(session.get("user", {}))
            login_user(user, remember=True)
            _user = user.as_dict()
            _user.pop("password_hash")
            session["user"] = "123123"
            print(session.get("user", {}))
            return {"code": 200, "user": _user}


@user_blueprint.route("/logout")
def logout():
    logout_user()
    return {}


@login_manager.user_loader
def load_user(idx):
    return User.query.filter(User.id == idx).first()


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            enough_role_priority = ROLES_PRIORITY.index(
                role
            ) <= ROLES_PRIORITY.index(current_user.role)
            if not enough_role_priority and role != "ANY":
                return login_manager.unauthorized()
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper
