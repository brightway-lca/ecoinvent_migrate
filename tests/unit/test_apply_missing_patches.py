from ecoinvent_migrate.wrangling import apply_missing_patches


def test_apply_missing_patches_simple():
    patches = [
        {
            "source": {
                "activity_name": "kraft paper production",
                "product_name": "electricity, high voltage",
                "unit": "kWh",
                "geography": "RER",
            },
            "target": {
                "activity_name": "sulfate pulp production, from softwood, unbleached",
            },
            "comment": "By-product production removed and not documented in 3.11 change report.",
        }
    ]
    expected = [
        1,
        {
            "source": {
                "activity_name": "kraft paper production",
                "product_name": "electricity, high voltage",
                "unit": "kWh",
                "geography": "RER",
            },
            "target": {
                "activity_name": "sulfate pulp production, from softwood, unbleached",
                "product_name": "electricity, high voltage",
                "unit": "kWh",
                "geography": "RER",
            },
            "comment": "By-product production removed and not documented in 3.11 change report.",
        },
    ]
    assert apply_missing_patches([1], patches) == expected


def test_apply_missing_patches_disaggregated():
    patches = [
        {
            "source": {
                "activity_name": "wheat grain production, organic",
                "product_name": "straw, organic",
                "unit": "kg",
                "geography": "CH",
            },
            "targets": [
                {
                    "activity_name": "wheat grain production, spring, organic, hill region",
                },
                {
                    "activity_name": "wheat grain production, spring, organic, mountain region",
                },
            ],
            "comment": "Split of wheat production into many specific processes",
        }
    ]
    expected = [
        1,
        {
            "source": {
                "activity_name": "wheat grain production, organic",
                "product_name": "straw, organic",
                "unit": "kg",
                "geography": "CH",
            },
            "target": {
                "activity_name": "wheat grain production, spring, organic, hill region",
                "product_name": "straw, organic",
                "unit": "kg",
                "geography": "CH",
            },
            "comment": "Split of wheat production into many specific processes",
        },
        {
            "source": {
                "activity_name": "wheat grain production, organic",
                "product_name": "straw, organic",
                "unit": "kg",
                "geography": "CH",
            },
            "target": {
                "activity_name": "wheat grain production, spring, organic, mountain region",
                "product_name": "straw, organic",
                "unit": "kg",
                "geography": "CH",
            },
            "comment": "Split of wheat production into many specific processes",
        },
    ]
    assert apply_missing_patches([1], patches) == expected
