import pytest

from ecoinvent_migrate.errors import Mismatch, Uncombinable
from ecoinvent_migrate.wrangling import source_target_pair_as_dict


def test_source_target_pair_as_dict_simple():
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
                "activity_name": "baling",
                "geography": "GLO",
                "product_name": "baling",
                "unit": "unit",
            },
            "target": {
                "activity_name": "baling",
                "geography": "GLO",
                "product_name": "baling",
                "unit": "unit",
            },
            "comment": "Line 42 in change report file `filename`",
        }
    ]
    assert source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10") == expected


def test_source_target_pair_as_dict_multiple():
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
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "target": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "comment": "Line 42 in change report file `filename`",
        },
        {
            "source": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "hard coal ash",
                "unit": "kg",
            },
            "target": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "hard coal ash",
                "unit": "kg",
            },
            "comment": "Line 42 in change report file `filename`",
        },
    ]
    assert source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10") == expected


def test_source_target_pair_as_dict_n_to_1():
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
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "target": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "comment": "Line 42 in change report file `filename`",
        },
        {
            "source": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "hard coal ash",
                "unit": "kg",
            },
            "target": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "comment": "Line 42 in change report file `filename`",
        },
    ]
    assert source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10") == expected


def test_source_target_pair_as_dict_1_to_n():
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
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "target": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "comment": "Line 42 in change report file `filename`",
        },
        {
            "source": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "autoclaved aerated concrete block",
                "unit": "kg",
            },
            "target": {
                "activity_name": "autoclaved aerated concrete block production",
                "geography": "IN",
                "product_name": "hard coal ash",
                "unit": "kg",
            },
            "comment": "Line 42 in change report file `filename`",
        },
    ]
    assert source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10") == expected


def test_source_target_pair_as_dict_mismatch():
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
        source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10")


def test_source_target_pair_as_dict_uncombinable():
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
        source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10")


def test_source_target_pair_as_dict_valueerror():
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
    assert source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10")
    with pytest.raises(ValueError):
        source_target_pair_as_dict(given, 42, "filename", "3.8", "3.10")
    with pytest.raises(ValueError):
        source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.11")


def test_source_target_pair_as_dict_new_dataset():
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
    assert source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10") == []


def test_source_target_pair_as_dict_multiple_some_missing():
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
                "activity_name": "p-nitrotoluene production",
                "geography": "GLO",
                "product_name": "p-nitrotoluene",
                "unit": "kg",
            },
            "target": {
                "activity_name": "nitrotoluenes production, toluene nitration",
                "geography": "GLO",
                "product_name": "p-nitrotoluene",
                "unit": "kg",
            },
            "comment": "Line 42 in change report file `filename`",
        },
    ]
    assert source_target_pair_as_dict(given, 42, "filename", "3.9.1", "3.10") == expected
