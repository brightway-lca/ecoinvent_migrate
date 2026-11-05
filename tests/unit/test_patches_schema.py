import pytest

from ecoinvent_migrate.patches import (
    TECHNOSPHERE_PATCHES_MISSING_DATA,
    TECHNOSPHERE_PATCHES_REPLACEMENT_DATA,
)
from ecoinvent_migrate.wrangling import apply_missing_patches, relabel

REQUIRED_SOURCE_KEYS = {"activity_name", "product_name", "geography", "unit"}
RELABELED_KEYS = {"name", "reference product", "location"}

ALL_PATCHES = [
    pytest.param(patch, id=f"{label}-{versions[0]}-{versions[1]}-{index}")
    for label, collection in [
        ("missing", TECHNOSPHERE_PATCHES_MISSING_DATA),
        ("replacement", TECHNOSPHERE_PATCHES_REPLACEMENT_DATA),
    ]
    for versions, patches in collection.items()
    for index, patch in enumerate(patches)
]


@pytest.mark.parametrize("patch", ALL_PATCHES)
def test_patches_use_ecospold2_labels(patch):
    """Patches must use the same labels as change report rows; `relabel` runs later."""
    assert REQUIRED_SOURCE_KEYS.issubset(patch["source"])
    targets = patch["targets"] if "targets" in patch else [patch["target"]]
    for dct in [patch["source"], *targets]:
        assert not RELABELED_KEYS.intersection(dct)


@pytest.mark.parametrize("versions", list(TECHNOSPHERE_PATCHES_MISSING_DATA))
def test_missing_patches_can_be_relabeled(versions):
    data = apply_missing_patches([], list(TECHNOSPHERE_PATCHES_MISSING_DATA[versions]))
    for obj in data:
        for kind in ("source", "target"):
            result = relabel(obj[kind])
            assert RELABELED_KEYS.issubset(result)
