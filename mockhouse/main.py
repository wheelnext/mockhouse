import os
import sys

from flask import render_template
from flask.cli import main

from mockhouse import create_app

app = create_app()


@app.route("/")
def index():
    return render_template("index.html")


def run():
    os.environ["FLASK_APP"] = "mockhouse.main"
    sys.argv = ["flask", "run"] + sys.argv[1:]
    main()
