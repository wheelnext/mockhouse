from flask import Blueprint
from flask import render_template

from mockhouse import ARTIFACTS_FOLDER
from mockhouse import VARIANT_HASH_LEN
from mockhouse.packaging_utils import wheel_to_metadata_dict

simpleB_bp = Blueprint("simpleB", __name__)  # noqa: N816


def get_file_per_variant() -> dict:
    wheels = ARTIFACTS_FOLDER.glob("*.whl")
    files_by_variant = {}
    for wheel in wheels:
        wheel_metadata = wheel_to_metadata_dict(wheelpath=wheel)
        files_by_variant[wheel_metadata.get("variant_hash")] = wheel_metadata
    return files_by_variant


@simpleB_bp.route("/<name>/variants")
def variants_list(name):
    return render_template(
        "variants.html", name=name, variants=[k for k in get_file_per_variant() if k]
    )


@simpleB_bp.route("/<name>/variant/<variant>")
def variant_detail(name, variant):
    wheel_metadata = get_file_per_variant().get(variant)
    # todo: make this a proper lookup, not a string match
    files = [
        {
            "url": f"/static/artifacts/dummy_project-0.0.1-0+v{variant[:VARIANT_HASH_LEN]}-py3-none-any.whl",
            "hashes": {
                "sha256": "e4d430bf9cee170db16d6fab21c1fb493005199e3e85be85b6ed4cb1d8feb742"
            },
            "filename": f"dummy_project-0.0.1-0+v{variant[:VARIANT_HASH_LEN]}-py3-none-any.whl",
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
