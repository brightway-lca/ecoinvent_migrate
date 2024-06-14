import pytest

from ecoinvent_migrate.errors import Mismatch, Uncombinable
from ecoinvent_migrate.wrangling import source_target_pair_as_bw_dict


def test_source_target_pair_as_bw_dict_simple():
    given = {
        "Activity Name - 3.9.1": "baling",
        "Geography - 3.9.1": "GLO",
        "Reference Product - 3.9.1": "baling",
        "Reference Product Unit - 3.9.1": "unit",
        "Activity Name - 3.10": "baling",
        "Geography - 3.10": "GLO",
        "Reference Product - 3.10": "baling",
        "Reference Product Unit - 3.10": "unit",
    }
    expected = [
        {
            "source": {
                "name": "baling",
                "location": "GLO",
                "reference product": "baling",
                "unit": "unit",
            },
            "target": {
                "name": "baling",
                "location": "GLO",
                "reference product": "baling",
                "unit": "unit",
            },
        }
    ]
    assert source_target_pair_as_bw_dict(given, "3.9.1", "3.10") == expected


def test_source_target_pair_as_bw_dict_multiple():
    given = {
        "Activity Name - 3.9.1": "autoclaved aerated concrete block production",
        "Geography - 3.9.1": "IN",
        "Reference Product - 3.9.1": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.9.1": "kg;\nkg",
        "Activity Name - 3.10": "autoclaved aerated concrete block production",
        "Geography - 3.10": "IN",
        "Reference Product - 3.10": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.10": "kg;\nkg",
    }
    expected = [
        {
            "source": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "target": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "autoclaved aerated concrete block",
                "unit": "kg",
            },
        },
        {
            "source": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "hard coal ash",
                "unit": "kg",
            },
            "target": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "hard coal ash",
                "unit": "kg",
            },
        },
    ]
    assert source_target_pair_as_bw_dict(given, "3.9.1", "3.10") == expected


def test_source_target_pair_as_bw_dict_n_to_1():
    given = {
        "Activity Name - 3.9.1": "autoclaved aerated concrete block production",
        "Geography - 3.9.1": "IN",
        "Reference Product - 3.9.1": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.9.1": "kg;\nkg",
        "Activity Name - 3.10": "autoclaved aerated concrete block production",
        "Geography - 3.10": "IN",
        "Reference Product - 3.10": "autoclaved aerated concrete block",
        "Reference Product Unit - 3.10": "kg",
    }
    expected = [
        {
            "source": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "target": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "autoclaved aerated concrete block",
                "unit": "kg",
            },
        },
        {
            "source": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "hard coal ash",
                "unit": "kg",
            },
            "target": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "autoclaved aerated concrete block",
                "unit": "kg",
            },
        },
    ]
    assert source_target_pair_as_bw_dict(given, "3.9.1", "3.10") == expected


def test_source_target_pair_as_bw_dict_1_to_n():
    given = {
        "Activity Name - 3.9.1": "autoclaved aerated concrete block production",
        "Geography - 3.9.1": "IN",
        "Reference Product - 3.9.1": "autoclaved aerated concrete block",
        "Reference Product Unit - 3.9.1": "kg",
        "Activity Name - 3.10": "autoclaved aerated concrete block production",
        "Geography - 3.10": "IN",
        "Reference Product - 3.10": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.10": "kg;\nkg",
    }
    expected = [
        {
            "source": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "target": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "autoclaved aerated concrete block",
                "unit": "kg",
            },
        },
        {
            "source": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "target": {
                "name": "autoclaved aerated concrete block production",
                "location": "IN",
                "reference product": "hard coal ash",
                "unit": "kg",
            },
        },
    ]
    assert source_target_pair_as_bw_dict(given, "3.9.1", "3.10") == expected


def test_source_target_pair_as_bw_dict_mismatch():
    given = {
        "Activity Name - 3.9.1": "autoclaved aerated concrete block production",
        "Geography - 3.9.1": "IN",
        "Reference Product - 3.9.1": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.9.1": "kg",
        "Activity Name - 3.10": "autoclaved aerated concrete block production",
        "Geography - 3.10": "IN",
        "Reference Product - 3.10": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.10": "kg;\nkg",
    }
    with pytest.raises(Mismatch):
        source_target_pair_as_bw_dict(given, "3.9.1", "3.10")


def test_source_target_pair_as_bw_dict_uncombinable():
    given = {
        "Activity Name - 3.9.1": "autoclaved aerated concrete block production",
        "Geography - 3.9.1": "IN",
        "Reference Product - 3.9.1": "autoclaved aerated concrete block;\nhard coal ash;\nsomething",
        "Reference Product Unit - 3.9.1": "kg;\nkg;\nMJ",
        "Activity Name - 3.10": "autoclaved aerated concrete block production",
        "Geography - 3.10": "IN",
        "Reference Product - 3.10": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.10": "kg;\nkg",
    }
    with pytest.raises(Uncombinable):
        source_target_pair_as_bw_dict(given, "3.9.1", "3.10")


def test_source_target_pair_as_bw_dict_valueerror():
    given = {
        "Activity Name - 3.9.1": "autoclaved aerated concrete block production",
        "Geography - 3.9.1": "IN",
        "Reference Product - 3.9.1": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.9.1": "kg;\nkg",
        "Activity Name - 3.10": "autoclaved aerated concrete block production",
        "Geography - 3.10": "IN",
        "Reference Product - 3.10": "autoclaved aerated concrete block;\nhard coal ash",
        "Reference Product Unit - 3.10": "kg;\nkg",
    }
    assert source_target_pair_as_bw_dict(given, "3.9.1", "3.10")
    with pytest.raises(ValueError):
        source_target_pair_as_bw_dict(given, "3.8", "3.10")
    with pytest.raises(ValueError):
        source_target_pair_as_bw_dict(given, "3.9.1", "3.11")


def test_source_target_pair_as_bw_dict_new_dataset():
    given = {
        "Activity Name - 3.9.1": float("NaN"),
        "Geography - 3.9.1": float("NaN"),
        "Reference Product - 3.9.1": float("NaN"),
        "Reference Product Unit - 3.9.1": float("NaN"),
        "Activity Name - 3.10": "baling",
        "Geography - 3.10": "GLO",
        "Reference Product - 3.10": "baling",
        "Reference Product Unit - 3.10": "unit",
    }
    assert source_target_pair_as_bw_dict(given, "3.9.1", "3.10") == []


def test_source_target_pair_as_bw_dict_multiple_some_missing():
    given = {
        "Activity Name - 3.9.1": "p-nitrotoluene production",
        "Geography - 3.9.1": "GLO",
        "Reference Product - 3.9.1": "nan;\nnan;\np-nitrotoluene",
        "Reference Product Unit - 3.9.1": "nan;\nnan;\nkg",
        "Activity Name - 3.10": "nitrotoluenes production, toluene nitration",
        "Geography - 3.10": "GLO",
        "Reference Product - 3.10": "m-nitrotoluene;\no-nitrotoluene;\np-nitrotoluene",
        "Reference Product Unit - 3.10": "kg;\nkg;\nkg",
    }
    expected = [
        {
            "source": {
                "name": "p-nitrotoluene production",
                "location": "GLO",
                "reference product": "p-nitrotoluene",
                "unit": "kg",
            },
            "target": {
                "name": "nitrotoluenes production, toluene nitration",
                "location": "GLO",
                "reference product": "p-nitrotoluene",
                "unit": "kg",
            },
        },
    ]
    assert source_target_pair_as_bw_dict(given, "3.9.1", "3.10") == expected
