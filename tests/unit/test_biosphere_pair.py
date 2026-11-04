import math

import pytest

from ecoinvent_migrate.wrangling import (
    apply_biosphere_patches,
    get_column_labels,
    source_target_biosphere_pair,
)

NAN = math.nan


def _row(**kwargs):
    row = {
        "ID - 3.11": NAN,
        "Name - 3.12": "2-Propen-1-ol",
        "Compartment - 3.12": "air",
        "Subcompartment - 3.12": "unspecified",
        "Unit - 3.12": NAN,
        "ID - 3.13": NAN,
        "Name - 3.13": NAN,
        "Compartment - 3.13": NAN,
        "Subcompartment - 3.13": NAN,
        "Unit - 3.13": NAN,
        "Conversion Factor (old-new)": NAN,
        "Comment": NAN,
    }
    row.update(kwargs)
    return row


def test_get_column_labels_mislabelled_uuid_column():
    assert get_column_labels(_row(), "3.12") == {
        "uuid": "ID - 3.11",
        "name": "Name - 3.12",
        "compartment": "Compartment - 3.12",
        "subcompartment": "Subcompartment - 3.12",
    }


def test_get_column_labels_missing_uuid_column():
    with pytest.raises(ValueError):
        get_column_labels({"Name - 3.12": "foo", "Other": 1}, "3.12")


def test_biosphere_pair_resolves_missing_uuids():
    rows = [_row(), _row(**{"Compartment - 3.12": "soil"})]
    lookup = {("2-Propen-1-ol", "air", "unspecified"): "abc"}
    result = source_target_biosphere_pair(
        rows, "3.12", "3.13", keep_deletions=True, source_uuid_lookup=lookup
    )
    # soil flow isn't in the lookup, so is skipped with a warning
    assert result == {"replace": [], "delete": [{"source": {"uuid": "abc", "name": "2-Propen-1-ol"}}]}


def test_biosphere_pair_uses_given_uuids():
    rows = [
        _row(
            **{
                "ID - 3.11": "abc",
                "ID - 3.13": "def",
                "Name - 3.13": "Allyl alcohol",
                "Conversion Factor (old-new)": 2.0,
            }
        )
    ]
    result = source_target_biosphere_pair(rows, "3.12", "3.13", keep_deletions=False)
    assert result == {
        "replace": [
            {
                "source": {"uuid": "abc", "name": "2-Propen-1-ol"},
                "target": {"uuid": "def", "name": "Allyl alcohol"},
                "conversion_factor": 2.0,
            }
        ]
    }


def test_apply_biosphere_patches():
    data = {
        "replace": [{"source": {"uuid": "b"}, "target": {"uuid": "x"}}],
        "delete": [{"source": {"uuid": "a"}}, {"source": {"uuid": "c"}}],
    }
    patches = [{"source": {"uuid": "a"}, "target": {"uuid": "y"}}]
    assert apply_biosphere_patches(data, patches) == {
        "replace": [
            {"source": {"uuid": "b"}, "target": {"uuid": "x"}},
            {"source": {"uuid": "a"}, "target": {"uuid": "y"}},
        ],
        "delete": [{"source": {"uuid": "c"}}],
    }
