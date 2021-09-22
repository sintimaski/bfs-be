import datetime

from flask import Flask
from flask_cors import CORS
from flask_session import Session

from core.blueprints import user_blueprint, listings_blueprint
from core.blueprints.mapper import mapper_blueprint
from core.blueprints.presets import presets_blueprint
from core.blueprints.updater import updater_blueprint
from core.blueprints.user import login_manager
from core.db_connector import db, migrate
from core.models import import_db_models


def create_app():
    # Create app.
    new_app = Flask(
        __name__, instance_relative_config=True, static_folder="static"
    )
    new_app.config.from_pyfile("flask.cfg")
    new_app.config["CORS_HEADERS"] = "Content-Type"

    # Register blueprints.
    new_app.register_blueprint(user_blueprint)
    new_app.register_blueprint(listings_blueprint)
    new_app.register_blueprint(mapper_blueprint)
    new_app.register_blueprint(presets_blueprint)
    new_app.register_blueprint(updater_blueprint)

    # Import models, init DB.
    import_db_models()
    db.init_app(new_app)
    with new_app.app_context():
        db.create_all()
        db.session.commit()
    new_app.app_context().push()

    # Initialize migrations.
    migrate.init_app(new_app, db)

    # Initialize login.
    login_manager.init_app(new_app)
    login_manager.session_protection = "strong"

    # Add Session
    new_app.config["SESSION_PERMANENT"] = True
    new_app.config["SESSION_TYPE"] = "filesystem"
    new_app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(hours=5)
    Session(new_app)

    # Add cors.
    CORS(new_app)

    return new_app


app = create_app()


@app.context_processor
def inject_template_globals():
    return {
        "nowts": datetime.datetime.utcnow(),
    }


@app.after_request
def apply_caching(response):
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Origin, X-Requested-With, Content-Type, Accept, x-auth",
    )
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    # from scrappers.cars.carnance import CarnanceScrapper
    # scrapper = CarnanceScrapper()
    # scrapper.send_rest()
