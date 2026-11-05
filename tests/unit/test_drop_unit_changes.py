from ecoinvent_migrate.wrangling import biosphere_unit_change_allowed, drop_unit_changes


def _obj(geography, target_unit, source_unit="kg"):
    return {
        "source": {
            "activity_name": "a",
            "product_name": "p",
            "geography": geography,
            "unit": source_unit,
        },
        "target": {"activity_name": "b", "geography": geography, "unit": target_unit},
    }


def test_drop_unit_changes_keeps_same_unit():
    data = [_obj("RER", "kg")]
    assert drop_unit_changes(data) == data


def test_drop_unit_changes_keeps_target_without_unit():
    data = [_obj("RER", "kg")]
    del data[0]["target"]["unit"]
    assert drop_unit_changes(data) == data


def test_drop_unit_changes_drops_replacement():
    assert drop_unit_changes([_obj("RER", "ha"), _obj("CH", "kg")]) == [_obj("CH", "kg")]


def test_drop_unit_changes_drops_whole_disaggregation():
    disaggregation = [_obj("RoW", "kg"), _obj("RoW", "unit")]
    disaggregation[0]["target"]["geography"] = "BR"
    assert drop_unit_changes(disaggregation + [_obj("CH", "kg")]) == [_obj("CH", "kg")]


def test_biosphere_unit_change_allowed():
    assert biosphere_unit_change_allowed("kg", "kg")
    assert biosphere_unit_change_allowed("m3", "Sm3")
    assert not biosphere_unit_change_allowed("kBq", "kg")
    assert not biosphere_unit_change_allowed("Sm3", "m3")
