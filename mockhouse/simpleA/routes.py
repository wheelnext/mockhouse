import hashlib
import os
from pathlib import Path

from flask import Blueprint
from flask import render_template

from mockhouse import ARTIFACTS_FOLDER

# from mockhouse import VARIANT_HASH_LEN
# from mockhouse.packaging_utils import wheel_to_metadata_dict

simpleA_bp = Blueprint("simpleA", __name__)  # noqa: N816


@simpleA_bp.route("/")
def home():
    packages = sorted([f.name for f in os.scandir(ARTIFACTS_FOLDER) if f.is_dir()])
    return render_template("simple.html", packages=packages)


@simpleA_bp.route("/<name>/")
def detail_packages(name: str):
    whl_dir = ARTIFACTS_FOLDER / name
    whl_files = whl_dir.glob("*.whl")

    data = [
        {
            "name": whl_f.name,
            "path": whl_f,
            "url": whl_f.relative_to(ARTIFACTS_FOLDER.parent),
            "sha256": hashlib.sha256(whl_f.read_bytes()).hexdigest(),
        }
        for whl_f in whl_files
    ]
    return render_template(
        "simple_detail.html",
        name=name,
        wheel_files=sorted(data, key=lambda pkg: pkg["name"], reverse=True),
    )
