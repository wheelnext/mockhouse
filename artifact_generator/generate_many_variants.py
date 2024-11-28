import os
import re
import shutil
import tempfile
from pathlib import Path


from wheel.cli.unpack import unpack as wheel_unpack
import wheel.cli.pack as whl_pck

import dict_hash

VARIANT_HASH_LEN = 8

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
            "compute_capability": 10,  # It knows the ultimate answer to life, the universe, and everything!
            "compute_accuracy": 10  # It knows the ultimate answer to life, the universe, and everything!
            # `humor` is obviously undefined for deepthought -- the concept does not make sense
        }
    },
    {
        "fictional_hw": {
            "architecture": "tars",
            "compute_capability": 8,  # Handles complex space missions and emotional AI interactions.
            "compute_accuracy": 8,  # Can get you through a black hole, but don’t push the humor settings too high!
            "humor": 10  # Adjustable humor settings from deadpan to hilarious
        }
    },
    {
        "fictional_hw": {
            "architecture": "HAL9000",
            "compute_capability": 6,  # Extremely reliable until it starts to question human commands…
            # `compute_accuracy` is obviously undefined for HAL9000 -- the concept does not make sense
            "humor": 2  # A bit of a cold operator, though it tries to be polite.
        }
    },
    {
        "fictional_hw": {
            "architecture": "mother",
            "compute_capability": 4,  # Efficient at monitoring and mission control - not ground shaking
            # `compute_accuracy` is obviously undefined for mother -- the concept does not make sense
            # `humor` is obviously undefined for mother (No jokes, just facts.) -- the concept does not make sense
        }
    },
    {
        "gcc": {
            "version": "1.2.3",
        }
    }
]


def wheel_pack(directory: str, dest_dir: str, build_number: str | None = None, variant_hash: str | None = None) -> None:
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
        if os.path.isdir(os.path.join(directory, fn)) and whl_pck.DIST_INFO_RE.match(fn)
    ]
    if len(dist_info_dirs) > 1:
        raise whl_pck.WheelError(f"Multiple .dist-info directories found in {directory}")
    elif not dist_info_dirs:
        raise whl_pck.WheelError(f"No .dist-info directories found in {directory}")

    # Determine the target wheel filename
    dist_info_dir = dist_info_dirs[0]
    name_version = whl_pck.DIST_INFO_RE.match(dist_info_dir).group("namever")

    # Read the tags and the existing build number from .dist-info/WHEEL
    wheel_file_path = os.path.join(directory, dist_info_dir, "WHEEL")
    with open(wheel_file_path, "rb") as f:
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
            with open(wheel_file_path, "wb") as f:
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
    wheel_path = os.path.join(dest_dir, f"{name_version}-{tagline}.whl")
    with whl_pck.WheelFile(wheel_path, "w") as wf:
        print(f"Repacking wheel as {wheel_path}...", flush=True)
        wf.write_files(directory)

    return wheel_path


if __name__ == "__main__":

    ___base_whl__ = Path("dist/dummy_project-0.0.1-py3-none-any.whl")

    if not ___base_whl__.exists():
        raise FileNotFoundError(___base_whl__)

    for variant_id, variant_nfo in enumerate(VARIANTS_2_GENERATE):
        with tempfile.TemporaryDirectory() as tmpdir:

            tmpdir = Path(tmpdir)
            source_whl = tmpdir / ___base_whl__.name

            shutil.copy(___base_whl__, source_whl)

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

            # keep only the first part of the hash. Like git hash, uniqueness is all that matters,
            # and 8 characters is plenty when considering that a given package will have relative
            # few variants.
            variant_hash = dict_hash.shake_128(variant_nfo)

            with metadata_f.open(mode='r+') as file:
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

            final_whl = wheel_pack(directory=wheel_dir, dest_dir=tmpdir, variant_hash=variant_hash)

            if not Path(final_whl).exists():
                raise FileNotFoundError(final_whl)

            shutil.copy(final_whl, "dist/")

            print()
