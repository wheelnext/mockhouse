#!/usr/bin/env python

import importlib.metadata
from pathlib import Path

from flask import Flask

__version__ = importlib.metadata.version("mockhouse")

ARTIFACTS_FOLDER = Path(__file__).parent / "static/packages"
VARIANT_HASH_LEN = 8

from mockhouse.simpleA.routes import simpleA_bp  # noqa: E402
from mockhouse.simpleB.routes import simpleB_bp  # noqa: E402


def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(simpleA_bp, url_prefix="/simpleA")
    app.register_blueprint(simpleB_bp, url_prefix="/simpleB")

    return app
