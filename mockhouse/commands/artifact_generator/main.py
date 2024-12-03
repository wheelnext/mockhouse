import contextlib
import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

import dict_hash
import wheel.cli.pack as whl_pck
from wheel.cli.unpack import unpack as wheel_unpack

from mockhouse import VARIANT_HASH_LEN
from mockhouse.main import app as flask_app

VARIANTS_2_GENERATE = [
    # ************************ DEVELOPER NOTE ************************ #
    # The idea here is to provide "different architectures" which sometimes have overlapping key/val
    # sometimes they don't. Not all architectures necessarily make sense to publish all "key/val".
    # The point is most likely to inject all kind of weird cases that later `mockhouse` will be able
    # to serve and PIP + Plugin can do its thing
    #
    # Note: Humor is absolutely an integral piece of this PEP.
    # ************************ DEVELOPER NOTE ************************ #
    # {
    #     "fictional_hw": {
    #         "architecture": "*",
    #         "compute_capability": ">1",
    #         "compute_accuracy": ">1",
    #         "humor": ">1"
    #     }
    # },
    {
        "fictional_hw": {
            "architecture": "deepthought",
            "compute_capability": 10,  # It knows the ultimate answer to life, the
            # universe, and everything!
            "compute_accuracy": 10,  # It knows the ultimate answer to life, the
            # universe, and everything! Humor is obviously undefined for deepthought.
        }
    },
    {
        "fictional_hw": {
            "architecture": "tars",
            "compute_capability": 8,  # Handles complex space missions and emotional AI
            # interactions.
            "compute_accuracy": 8,  # Can get you through a black hole, but don't push
            # the humor settings too high!
            "humor": 10,  # Adjustable humor settings from deadpan to hilarious
        }
    },
    {
        "fictional_hw": {
            "architecture": "HAL9000",
            "compute_capability": 6,  # Extremely reliable until it starts to question
            # human commands ...
            # `compute_accuracy` is obviously undefined for HAL9000 since it questions
            # Human commands.
            "humor": 2,  # A bit of a cold operator, though it tries to be polite.
        }
    },
    {
        "fictional_hw": {
            "architecture": "mother",
            "compute_capability": 4,  # Efficient at monitoring and mission control -
            # not ground shaking
            # `compute_accuracy` is obviously undefined for mother -- the concept does
            # not make sense
            # `humor` is obviously undefined for mother (No jokes, just facts.) -- the
            # concept does not make sense
        }
    },
    {
        "gcc": {
            "version": "1.2.3",
        }
    },
]


def wheel_pack(
    directory: str,
    dest_dir: str,
    build_number: str | None = None,
    variant_hash: str | None = None,
) -> None:
    """Repack a previously unpacked wheel directory into a new wheel file.

    The .dist-info/WHEEL file must contain one or more tags so that the target
    wheel file name can be determined.

    :param directory: The unpacked wheel directory
    :param dest_dir: Destination directory (defaults to the current directory)
    """
    # Find the .dist-info directory
    dist_info_dirs = [
        fn
        for fn in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, fn)) and whl_pck.DIST_INFO_RE.match(fn)  # noqa: PTH112, PTH118
    ]
    if len(dist_info_dirs) > 1:
        raise whl_pck.WheelError(
            f"Multiple .dist-info directories found in {directory}"
        )
    if not dist_info_dirs:
        raise whl_pck.WheelError(f"No .dist-info directories found in {directory}")

    # Determine the target wheel filename
    dist_info_dir = dist_info_dirs[0]
    name_version = whl_pck.DIST_INFO_RE.match(dist_info_dir).group("namever")

    # Read the tags and the existing build number from .dist-info/WHEEL
    wheel_file_path = os.path.join(directory, dist_info_dir, "WHEEL")  # noqa: PTH118
    with open(wheel_file_path, "rb") as f:  # noqa: PTH123
        info = whl_pck.BytesParser(policy=whl_pck.email.policy.compat32).parse(f)
        tags: list[str] = info.get_all("Tag", [])
        existing_build_number = info.get("Build")

        if not tags:
            raise whl_pck.WheelError(
                f"No tags present in {dist_info_dir}/WHEEL; cannot determine target "
                f"wheel filename"
            )

    # Set the wheel file name and add/replace/remove the Build tag in .dist-info/WHEEL
    build_number = build_number if build_number is not None else existing_build_number
    if build_number is not None:
        del info["Build"]
        if build_number:
            info["Build"] = build_number
            name_version += "-" + build_number

        if build_number != existing_build_number:
            with open(wheel_file_path, "wb") as f:  # noqa: PTH123
                whl_pck.BytesGenerator(f, maxheaderlen=0).flatten(info)

    if variant_hash is not None:
        variant_hash_pattern = rf"^[a-fA-F0-9]{{{VARIANT_HASH_LEN}}}$"
        # if the hash is not a valid hash value, drop the value and ignore
        variant_hash = variant_hash[:VARIANT_HASH_LEN]
        if re.match(variant_hash_pattern, variant_hash):
            name_version += f"-#{variant_hash}"

    # Reassemble the tags for the wheel file
    tagline = whl_pck.compute_tagline(tags)

    # Repack the wheel
    wheel_path = os.path.join(dest_dir, f"{name_version}-{tagline}.whl")  # noqa: PTH118
    with whl_pck.WheelFile(wheel_path, "w") as wf:
        logging.info(f"Repacking wheel as {wheel_path}...")
        wf.write_files(directory)

    return wheel_path


def get_generated_whl_file(folder: str | Path) -> Path:
    # Find all .whl files in the folder
    whl_files = list(Path(folder).glob("*.whl"))

    if len(whl_files) == 0:
        raise FileNotFoundError("No .whl files found in the folder.")
    if len(whl_files) > 1:
        raise RuntimeError(f"Multiple .whl files found: {whl_files}")

    return Path(whl_files[0])


def generate_variants(source_folder: str | Path, dest_folder: str | Path):
    base_whl_f = get_generated_whl_file(Path(source_folder) / "dist")

    if not base_whl_f.exists():
        raise FileNotFoundError(base_whl_f)

    for variant_nfo in VARIANTS_2_GENERATE:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)  # noqa: PLW2901
            source_whl = tmpdir / base_whl_f.name

            shutil.copy(base_whl_f, source_whl)

            if not source_whl.exists():
                raise FileNotFoundError(source_whl)

            wheel_unpack(path=source_whl, dest=tmpdir)

            dirname = source_whl.name.split("-py3")[0]
            wheel_dir = tmpdir / dirname

            if not wheel_dir.exists():
                raise FileNotFoundError(wheel_dir)

            distinfo_dir = wheel_dir / f"{dirname}.dist-info"

            if not distinfo_dir.exists():
                raise FileNotFoundError(distinfo_dir)

            metadata_f = distinfo_dir / "METADATA"

            if not metadata_f.exists():
                raise FileNotFoundError(metadata_f)

            # keep only the first part of the hash. Like git hash, uniqueness is all
            # that matters, and 8 characters is plenty when considering that a given
            # package will have relative few variants.
            variant_hash = dict_hash.shake_128(variant_nfo)

            with metadata_f.open(mode="r+") as file:
                # Read all lines
                lines = file.readlines()

                # Remove trailing empty lines
                while lines and lines[-1].strip() == "":
                    lines.pop()

                # Move the file pointer to the beginning
                file.seek(0)

                # Write back the non-empty content
                file.writelines(lines)

                # Truncate the file to remove any remaining old content
                file.truncate()

                file.write(f"Variant-hash: {variant_hash}\n")
                for variant_provider, variant_data in variant_nfo.items():
                    for key, val in variant_data.items():
                        # Variant: fictional_hw :: <key> :: <val>
                        file.write(f"Variant: {variant_provider} :: {key} :: {val}\n")

            dest_whl_path = wheel_pack(
                directory=wheel_dir, dest_dir=tmpdir, variant_hash=variant_hash
            )

            if not Path(dest_whl_path).exists():
                raise FileNotFoundError(dest_whl_path)

            if not isinstance(dest_folder, (str, Path)):
                raise TypeError(f"Expected: str|Path, received: {type(dest_folder)}")

            shutil.copy(dest_whl_path, dest_folder)
            logging.info(f"Copying wheel to {dest_folder}...\n")


@contextmanager
def temp_wd(path: str | Path):
    cwd = Path.cwd()
    os.chdir(path)
    yield
    os.chdir(cwd)


def reset_folder(folder_path: str | Path):
    folder = Path(folder_path)
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(folder)  # Delete the folder and all its contents
    folder.mkdir(parents=True)  # Recreate the folder


def generate_artifacts(*args, **kwargs):
    # Set the logger to `INFO` level.
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    base_directory = Path(os.path.realpath(__file__)).parent
    with temp_wd(base_directory):
        base_dest_folder = Path(flask_app.static_folder) / "packages"

        projects = [
            "dummy_project",
            "sandbox_project",
        ]

        for project_name in projects:
            source_folder = base_directory / project_name
            dest_folder = base_dest_folder / project_name

            # Wiping any previous files
            reset_folder(dest_folder)

            logging.info("*************************************************")
            logging.info(f"Processing: `{project_name}`")
            logging.info(f"{source_folder=}")
            logging.info(f"{dest_folder=}\n")

            with temp_wd(source_folder):
                result = subprocess.run(  # noqa: S603
                    shlex.split("make build"),
                    capture_output=True,
                    text=True,
                    check=False,
                )

            if result.returncode != 0:
                logging.info(f"{result.stdout=}")
                logging.info(f"{result.stderr=}")
                sys.exit(result.returncode)

            dest_folder.mkdir(exist_ok=True, parents=True)
            generate_variants(source_folder, dest_folder)
            logging.info("-------------------------------------------------\n")


if __name__ == "__main__":
    generate_artifacts()
