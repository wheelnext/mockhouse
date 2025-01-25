import os

from flask import Blueprint
from flask import render_template

from mockhouse import ARTIFACTS_FOLDER
from mockhouse import VARIANT_HASH_LEN
from mockhouse.packaging_utils import wheel_to_metadata_dict

simpleB_bp = Blueprint("simpleB", __name__)  # noqa: N816


def get_file_per_variant(package_name: str) -> dict:
    package_dir = ARTIFACTS_FOLDER / package_name

    if not package_dir.exists():
        raise FileNotFoundError

    wheels = package_dir.glob("*.whl")
    files_by_variant = {}
    for wheel in wheels:
        wheel_metadata = wheel_to_metadata_dict(wheelpath=wheel)
        variant_hash = wheel_metadata.get("variant_hash")
        if variant_hash is None:
            continue
        # cutoff after `VARIANT_HASH_LEN` chars
        files_by_variant[variant_hash[:VARIANT_HASH_LEN]] = wheel_metadata
    return files_by_variant


@simpleB_bp.route("/")
def home():
    packages = [f.name for f in os.scandir(ARTIFACTS_FOLDER) if f.is_dir()]
    return render_template("simple.html", packages=packages)


@simpleB_bp.route("/<name>/variants/")
def variants_list(name):
    return render_template(
        "variants.html",
        name=name,
        variants=[k for k in get_file_per_variant(package_name=name) if k],
    )


@simpleB_bp.route("/<name>/variant/<variant>/")
def variant_detail(name, variant):
    variant = variant[:VARIANT_HASH_LEN]  # cutoff after `VARIANT_HASH_LEN` chars
    wheel_metadata = get_file_per_variant(package_name=name).get(variant)
    # todo: make this a proper lookup, not a string match
    files = [
        {
            "url": f"/static/artifacts/dummy_project-0.0.1-@{variant[:VARIANT_HASH_LEN]}-py3-none-any.whl",
            "hashes": {
                "sha256": "e4d430bf9cee170db16d6fab21c1fb493005199e3e85be85b6ed4cb1d8feb742"
            },
            "filename": f"dummy_project-0.0.1-@{variant[:VARIANT_HASH_LEN]}-py3-none-any.whl",
            "requires-python": "",
            "core-metadata": {
                "sha256": "e4d430bf9cee170db16d6fab21c1fb493005199e3e85be85b6ed4cb1d8feb742"
            },
            "yanked": False,
        },
    ]
    # TODO: empty list of files - not sure how to do these.
    return render_template(
        "detail.html",
        name=name,
        variant_hash=variant,
        variant_value=wheel_metadata["variants"],
        files=files,
    )
