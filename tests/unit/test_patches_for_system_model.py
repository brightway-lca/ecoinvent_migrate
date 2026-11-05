import pytest

from ecoinvent_migrate.patches import (
    TECHNOSPHERE_PATCHES_MISSING_DATA,
    TECHNOSPHERE_PATCHES_REPLACEMENT_DATA,
)
from ecoinvent_migrate.wrangling import (
    SYSTEM_MODELS,
    apply_missing_patches,
    patches_for_system_model,
    warn_on_absent_patch_results,
)

SOURCE = {
    "activity_name": "pelletising of polyethylene terephthalate",
    "geography": "RER",
    "product_name": "polyethylene terephthalate, flakes, recycled",
    "unit": "kg",
}


def test_patches_for_system_model_without_list_applies_everywhere():
    patches = [{"source": SOURCE, "target": {"product_name": "x"}, "context": "target"}]
    for sm in SYSTEM_MODELS:
        assert patches_for_system_model(patches, sm) == patches


def test_patches_for_system_model_filters_and_strips_key():
    patch = {
        "source": SOURCE,
        "target": {"product_name": "x"},
        "context": "target",
        "system_models": ["cutoff", "EN15804"],
    }
    expected = [{"source": SOURCE, "target": {"product_name": "x"}, "context": "target"}]
    assert patches_for_system_model([patch], "cutoff") == expected
    assert patches_for_system_model([patch], "EN15804") == expected
    assert patches_for_system_model([patch], "consequential") == []
    assert patches_for_system_model([patch], "apos") == []
    # Input isn't modified
    assert patch["system_models"] == ["cutoff", "EN15804"]


def test_patches_for_system_model_unknown_system_model():
    patch = {"source": SOURCE, "target": {}, "context": "target", "system_models": ["cut-off"]}
    with pytest.raises(ValueError):
        patches_for_system_model([patch], "cutoff")


def test_system_models_key_not_in_missing_patch_output():
    patch = {"source": SOURCE, "target": {"product_name": "x"}, "system_models": ["cutoff"]}
    data = apply_missing_patches([], patches_for_system_model([patch], "cutoff"))
    assert all("system_models" not in obj for obj in data)


@pytest.mark.parametrize("system_model", sorted(SYSTEM_MODELS))
def test_all_patch_system_models_are_valid(system_model):
    for collection in (TECHNOSPHERE_PATCHES_MISSING_DATA, TECHNOSPHERE_PATCHES_REPLACEMENT_DATA):
        for patches in collection.values():
            for patch in patches_for_system_model(list(patches), system_model):
                assert "system_models" not in patch


def _key(dct):
    return (dct["activity_name"], dct["geography"], dct["product_name"], dct["unit"])


def test_warn_on_absent_patch_results(caplog):
    patch = {
        "source": SOURCE,
        "target": {"product_name": "polyethylene terephthalate, pellets, recycled"},
        "context": "target",
    }
    pellets = _key(SOURCE | patch["target"])

    warn_on_absent_patch_results([patch], {}, {pellets: {}}, "src", "tgt")
    assert "does this patch need" not in caplog.text

    warn_on_absent_patch_results([patch], {}, {_key(SOURCE): {}}, "src", "tgt")
    assert "does this patch need" in caplog.text


def test_warn_on_absent_patch_results_allows_row(caplog):
    source = SOURCE | {"geography": "GLO"}
    patch = {"source": source, "target": {"product_name": "y"}, "context": "source"}
    row = ("pelletising of polyethylene terephthalate", "RoW", "y", "kg")
    warn_on_absent_patch_results([patch], {row: {}}, {}, "src", "tgt")
    assert "does this patch need" not in caplog.text
