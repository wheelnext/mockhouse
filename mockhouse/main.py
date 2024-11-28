import os
import sys
from pathlib import Path

from flask import Flask
from flask import render_template
from flask.cli import main

# from artifact_generator.generate_many_variants import hash_keep_length
from mockhouse.packaging_utils import wheel_to_metadata_dict

app = Flask(__name__)

hash_keep_length = 8


artifacts_folder = Path(__file__).parent / "static/artifacts"
wheels = artifacts_folder.glob("*.whl")
files_by_variant = {}
for wheel in wheels:
    wheel_metadata = wheel_to_metadata_dict(wheelpath=wheel)
    files_by_variant[wheel_metadata.get("variant_hash")] = wheel_metadata


@app.route("/")
def index():
  return render_template("index.html")

@app.route("/simple/<name>/variants")
def variants_list(name):
  return render_template("variants.html", name=name, variants=[k for k in files_by_variant if k])

@app.route("/simple/<name>/variant/<variant>")
def variant_detail(name, variant):
  wheel_metadata = files_by_variant.get(variant)
  # todo: make this a proper lookup, not a string match
  files = [
    {
      "url": f"/static/artifacts/dummy_project-0.0.1-0+v{variant[:hash_keep_length]}-py3-none-any.whl",
      "hashes": {"sha256": "e4d430bf9cee170db16d6fab21c1fb493005199e3e85be85b6ed4cb1d8feb742"},
      "filename": f"dummy_project-0.0.1-0+v{variant[:hash_keep_length]}-py3-none-any.whl",
      "requires-python": "",
      "core-metadata": {"sha256": "e4d430bf9cee170db16d6fab21c1fb493005199e3e85be85b6ed4cb1d8feb742"},
      "yanked": False,
    },
  ]
  # TODO: empty list of files - not sure how to do these.
  return render_template("detail.html", name=name, variant_hash=variant, variant_value=wheel_metadata["variants"], files=files)


def run():
  os.environ["FLASK_APP"] = "mockhouse.main"
  sys.argv = ["flask", "run"] + sys.argv[1:]
  main()
