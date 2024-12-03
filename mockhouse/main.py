import os
import sys
from pathlib import Path

from flask import Flask
from flask import render_template
from flask.cli import main

from mockhouse import create_app

# from mockhouse.packaging_utils import wheel_to_metadata_dict

app = create_app()


# artifacts_folder = Path(__file__).parent / "static/artifacts"
# wheels = artifacts_folder.glob("*.whl")
# files_by_variant = {}
# for wheel in wheels:
#     wheel_metadata = wheel_to_metadata_dict(wheelpath=wheel)
#     files_by_variant[wheel_metadata.get("variant_hash")] = wheel_metadata


@app.route("/")
def index():
    return render_template("index.html")


def run():
    os.environ["FLASK_APP"] = "mockhouse.main"
    sys.argv = ["flask", "run"] + sys.argv[1:]
    main()
