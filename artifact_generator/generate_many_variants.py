import shutil
import tempfile
from pathlib import Path

import dict_hash

hash_keep_length = 8

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


if __name__ == "__main__":

    ___base_whl__ = Path("dist/dummy_project-0.0.1-py3-none-any.whl")

    if not ___base_whl__.exists():
        raise FileNotFoundError(___base_whl__)

    from wheel.cli.unpack import unpack as wheel_unpack
    from wheel.cli.pack import pack as wheel_pack

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

            wheel_pack(directory=wheel_dir, dest_dir=tmpdir, build_number=f'0+v{variant_hash[:hash_keep_length]}')

            final_whl = tmpdir / f"{dirname}-0+v{variant_hash[:hash_keep_length]}-py3-none-any.whl"

            if not final_whl.exists():
                raise FileNotFoundError(final_whl)

            shutil.copy(final_whl, "dist/")

            print()
