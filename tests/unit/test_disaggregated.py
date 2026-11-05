from ecoinvent_migrate.wrangling import disaggregated


def _obj(geography):
    return {
        "source": {"activity_name": "a", "product_name": "p", "geography": "RoW", "unit": "kg"},
        "target": {"activity_name": "a", "product_name": "p", "geography": geography, "unit": "kg"},
    }


def _lookup(volumes):
    return {
        ("a", geography, "p", "kg"): {"production_volume": pv}
        for geography, pv in volumes.items()
    }


def test_disaggregated_production_volume():
    result = disaggregated([_obj("RoW"), _obj("IN")], _lookup({"RoW": 3, "IN": 1}))
    assert result["targets"] == [
        _obj("RoW")["target"] | {"allocation": 0.75},
        _obj("IN")["target"] | {"allocation": 0.25},
    ]
    assert "comment" not in result


def test_disaggregated_equal_allocation_keeps_distinct_targets():
    result = disaggregated(
        [_obj("RoW"), _obj("IN-AS"), _obj("IN-ML")], _lookup({"RoW": 0, "IN-AS": 0, "IN-ML": 0})
    )
    assert [t["geography"] for t in result["targets"]] == ["RoW", "IN-AS", "IN-ML"]
    assert all(t["allocation"] == 1 / 3 for t in result["targets"])
    assert "Equal allocation" in result["comment"]
