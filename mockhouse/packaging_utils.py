# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import typing
import zipfile
from pathlib import Path

import packaging.metadata as pmeta  # noqa: E402


# ========================= MONKEY PATCHING PACKING ========================= #
"""Packaging needs to be monkey path in order to add `variant` support"""

pmeta._STRING_FIELDS.add("variant_hash")
pmeta._LIST_FIELDS.add("variants")
pmeta._EMAIL_TO_RAW_MAPPING["variant-hash"] = "variant_hash"
pmeta._RAW_TO_EMAIL_MAPPING["variant_hash"] = "variant-hash"
pmeta._EMAIL_TO_RAW_MAPPING["variant"] = "variants"
pmeta._RAW_TO_EMAIL_MAPPING["variants"] = "variant"


class MetadataRebuildMeta(type):
    """This class is necessary otherwise getatrr() would fail.
    Metadata is not a trivial class to MonkeyPatch to the weird
    data access patterns. The only way is to rebuild the class
    from scratch.
    `RawMetadata` actually wouldn't need a full class rebuild."""

    def __new__(mcs, name, bases, namespace):
        # for k, v in inspect.getmembers(original_class):
        for k, v in vars(pmeta.Metadata).items():
            if callable(v) or isinstance(v, classmethod) or k.startswith('__'):
                continue
            namespace[k] = v
        return super().__new__(mcs, name, bases, namespace)


# Define the Metadata class with the metaclass
class RawMetadata(pmeta.RawMetadata):
    """Variants-Augmented RawMetadata Representation."""

    # Define additional attributes
    variant_hash: str
    variants: list[str]  # type: ignore


# Define the Metadata class with the metaclass
class Metadata(pmeta.Metadata, metaclass=MetadataRebuildMeta):
    """Variants-Augmented Metadata Representation."""

    # Define additional attributes
    # NOTE: For some reason the `METADATA` version shipped in 3.13 is 2.1,
    # which means you can not specify a version any higher. Otherwise you get this:
    # packaging.metadata.InvalidMetadata: variant introduced in metadata version 2.2, not 2.1
    variant_hash: pmeta._Validator[str | None] = pmeta._Validator(added="2.1")
    variants: pmeta._Validator[list[str] | None] = pmeta._Validator(added="2.1")
    """:external:ref:`core-metadata-variants`"""


pmeta.RawMetadata = RawMetadata
pmeta.Metadata = Metadata

# %%%%%%%%%%%%%%%%%%%%%%%%% MONKEY PATCHING PACKING %%%%%%%%%%%%%%%%%%%%%%%%% #


class NoMetadataError(Exception):
    pass


def parse_metadata_file_content(content: bytes | None) -> pmeta.Metadata:
    # We prefer to parse metadata from the content, which will typically come
    # from extracting a METADATA or PKG-INFO file from an artifact.
    if content is not None:
        return pmeta.Metadata.from_email(content, validate=True)

    # If we don't have contents or form data, then we don't have any metadata
    # and the only thing we can do is error.
    raise NoMetadataError


def wheel_to_metadata_dict(wheelpath: Path) -> dict[str, typing.Any]:
    with zipfile.ZipFile(wheelpath, 'r') as whl:
        # Locate the METADATA file within the wheel package
        metadata_file = next(
            (f for f in whl.namelist() if f.endswith("METADATA")), None
        )

        if metadata_file:
            with whl.open(metadata_file) as f:
                metadata_content = f.read()
                # Parse the content to a dictionary
                metadata_dict = parse_metadata_file_content(metadata_content).__dict__
                with contextlib.suppress(KeyError):
                    del metadata_dict["_raw"]
                return metadata_dict

        else:
            raise FileNotFoundError("No METADATA file found in this wheel package.")


if __name__ == "__main__":

    import pprint
    wheel_path = Path(__file__).parent.parent / "static/artifacts"
    for wheel_file in wheel_path.glob('*.whl'):
        metadata_dict = wheel_to_metadata_dict(wheel_path / wheel_file)

        print("\n---------------------------------\n")
        pprint.pprint(metadata_dict)
