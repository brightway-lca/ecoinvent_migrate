from ecoinvent_migrate.wrangling import drop_absent_sources


def _obj(geography):
    return {
        "source": {"activity_name": "a", "product_name": "p", "geography": geography, "unit": "kg"},
        "target": {"activity_name": "b"},
    }


def test_drop_absent_sources():
    lookup = {("a", "RER", "p", "kg"): {}}
    assert drop_absent_sources([_obj("RER"), _obj("US")], lookup, "db") == [_obj("RER")]
