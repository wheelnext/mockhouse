from __future__ import annotations

import argparse
import pathlib
import shlex
import subprocess

from jinja2 import Environment
from jinja2 import FileSystemLoader


def analyze_wheel(wheel_path) -> str | None:
    try:
        result = subprocess.run(  # noqa: S603
            shlex.split(f"variantlib analyze-wheel -i {wheel_path}"),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout  # noqa: TRY300
    except subprocess.CalledProcessError as e:
        raise RuntimeError from e


def generate_index(args: list[str]) -> None:
    parser = argparse.ArgumentParser(
        prog="generate_index_json",
        description="Generate a JSON index of all package variants",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=pathlib.Path,
        required=True,
        help="Directory to process",
    )

    parsed_args = parser.parse_args(args)

    directory: pathlib.Path = parsed_args.directory.resolve()

    if not (directory.exists() and directory.is_dir()):
        raise NotADirectoryError(f"Directory not found: `{directory}`")

    project_name = directory.name
    wheels = []
    for wheel_f in directory.glob("*.whl"):
        wheel_path = pathlib.Path(wheel_f)
        print(f"Processing wheel: {wheel_path}")
        if not wheel_path.is_file():
            raise FileNotFoundError(f"File not found: `{wheel_path}`")
        wheels.append(
            {
                "filename": wheel_path.name,
                "variant_data": [
                    line.strip()
                    for line in analyze_wheel(wheel_path).splitlines()
                    if line.strip()
                ],
            }
        )

    # Load template
    current_dir = pathlib.Path(__file__).parent.parent
    env = Environment(
        loader=FileSystemLoader(current_dir / "templates"),
        autoescape=True,
    )
    template = env.get_template("project_index.html.j2")

    # Render template
    output = template.render(
        project_name=project_name,
        # Non Variants first - Then by filename
        wheels=sorted(wheels, key=lambda x: x["filename"]),
        variants_json_files=[fp.name for fp in directory.glob("variants-*.json")],
    )

    with pathlib.Path("index.html").open(mode="w") as f:
        f.write(output)


if __name__ == "__main__":
    generate_index()
