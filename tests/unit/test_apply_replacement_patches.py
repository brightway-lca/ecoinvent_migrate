from ecoinvent_migrate.wrangling import apply_replacement_patches


def test_apply_replacement_patches_source():
    given = [
        {
            "source": {
                "activity_name": "treatment of used refrigerant R134a, reclamation",
                "product_name": "used refrigerant R134a",
                "unit": "kg",
                "geography": "GLO",
            },
            "target": {
                "activity_name": "treatment of used refrigerant R134a, reclamation",
                "product_name": "used refrigerant R134a",
                "unit": "kg",
                "geography": "GLO",
            },
        }
    ]
    patches = [
        {
            "source": {
                "activity_name": "treatment of used refrigerant R134a, reclamation",
                "product_name": "used refrigerant R134a",
                "unit": "kg",
                "geography": "GLO",
            },
            "target": {"product_name": "refrigerant R134a"},
            "comment": "Data error in original dataset; should have treated used refrigerant.",
            "context": "source",
        }
    ]
    expected = [
        {
            "source": {
                "activity_name": "treatment of used refrigerant R134a, reclamation",
                "product_name": "refrigerant R134a",
                "unit": "kg",
                "geography": "GLO",
            },
            "target": {
                "activity_name": "treatment of used refrigerant R134a, reclamation",
                "product_name": "used refrigerant R134a",
                "unit": "kg",
                "geography": "GLO",
            },
            "comment": "Data error in original dataset; should have treated used refrigerant.",
        }
    ]
    assert apply_replacement_patches(given, patches) == expected


def test_apply_replacement_patches_target():
    given = [
        {
            "source": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "comment": "Line 7 in some_file.xlsx",
        }
    ]
    patches = [
        {
            "source": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "geography": "Europe without Switzerland",
            },
            "context": "target",
            "comment": "Data error in change report geography",
        },
    ]
    expected = [
        {
            "source": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "activity_name": "market for straw",
                "geography": "Europe without Switzerland",
                "product_name": "straw",
                "unit": "kg",
            },
            "comment": "Line 7 in some_file.xlsx. Patched with comment 'Data error in change report geography'.",
        }
    ]
    assert apply_replacement_patches(given, patches) == expected


def test_apply_replacement_patches_missing(caplog):
    patches = [
        {
            "source": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "geography": "Europe without Switzerland",
            },
            "context": "target",
            "comment": "Data error in change report geography",
        },
    ]
    apply_replacement_patches([], patches)
    assert "Expected to patch the following" in caplog.text


def test_apply_replacement_patches_target_twice():
    given = [
        {
            "source": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "comment": "Line 7 in some_file.xlsx",
        },
        {
            "source": {
                "activity_name": "something",
                "geography": "something",
                "product_name": "danger",
                "unit": "zone",
            },
            "target": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "comment": "Line 7 in some_file.xlsx",
        },
    ]
    patches = [
        {
            "source": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "geography": "Europe without Switzerland",
            },
            "context": "target",
            "comment": "Data error in change report geography",
        },
    ]
    expected = [
        {
            "source": {
                "activity_name": "market for straw",
                "geography": "RER",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "activity_name": "market for straw",
                "geography": "Europe without Switzerland",
                "product_name": "straw",
                "unit": "kg",
            },
            "comment": "Line 7 in some_file.xlsx. Patched with comment 'Data error in change report geography'.",
        },
        {
            "source": {
                "activity_name": "something",
                "geography": "something",
                "product_name": "danger",
                "unit": "zone",
            },
            "target": {
                "activity_name": "market for straw",
                "geography": "Europe without Switzerland",
                "product_name": "straw",
                "unit": "kg",
            },
            "comment": "Line 7 in some_file.xlsx. Patched with comment 'Data error in change report geography'.",
        },
    ]
    assert apply_replacement_patches(given, patches) == expected
