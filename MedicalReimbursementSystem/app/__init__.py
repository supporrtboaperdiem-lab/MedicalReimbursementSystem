import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask

from app.config import config_by_name
from app.extensions import db, migrate, csrf


def create_app(config_name="development"):
    app = Flask(__name__)

    config_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_class)

    init_extensions(app)
    register_blueprints(app)
    configure_logging(app)

    return app


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)


def register_blueprints(app):
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)


def configure_logging(app):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=1024 * 1024,
        backupCount=5
    )

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s "
        "[in %(pathname)s:%(lineno)d]"
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(app.config.get("LOG_LEVEL", "INFO"))

    app.logger.addHandler(file_handler)