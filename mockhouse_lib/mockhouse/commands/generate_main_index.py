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
            shlex.split(f"variantlib analyze_wheel -i {wheel_path}"),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout  # noqa: TRY300
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")  # noqa: T201
        return None


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

    # Load template
    current_dir = pathlib.Path(__file__).parent.parent
    env = Environment(
        loader=FileSystemLoader(current_dir / "templates"),
        autoescape=True,
    )
    template = env.get_template("main_index.html.j2")

    # Render template
    output = template.render(
        directories=sorted(
            [dirpath.name for dirpath in directory.iterdir() if dirpath.is_dir()],
        )
    )

    with pathlib.Path("index.html").open(mode="w") as f:
        f.write(output)


if __name__ == "__main__":
    generate_index()
