from functools import partial

SYNCOAL_PRODUCTS = [
    "1-propanol",
    "acetone, liquid",
    "ammonia, anhydrous, liquid",
    "butyl acrylate",
    "chemical, organic",
    "diesel, low-sulfur",
    "ethanol, without water, in 99.7% solution state, from ethylene",
    "ethylene",
    "heavy fuel oil",
    "isobutanol",
    "liquefied petroleum gas",
    "methanol",
    "methyl ethyl ketone",
    "natural gas, high pressure",
    "pitch",
    "propylene",
    "sulfur",
]

ACETIC_ACID_BYPRODUCTS = [
    "acetone, liquid",
    "ethyl acetate",
    "formic acid",
    "methyl acetate",
    "methyl ethyl ketone",
    "propionic acid",
]


def byproduct(
    old_name: str,
    new_name: str,
    product: str,
    geography: str,
    unit: str,
    comment: str = "By-product production missed in change report during name change",
) -> dict:
    return {
        "source": {
            "activity_name": old_name,
            "product_name": product,
            "unit": unit,
            "geography": geography,
        },
        "target": {
            "activity_name": new_name,
        },
        "comment": comment,
    }


acetic_acid_production_311 = partial(
    byproduct,
    old_name="acetic acid production, butane oxidation",
    new_name="acetic acid production, from n-butane oxidation",
    comment="3.11 change report section 7.7.3. Change report is missing by-products of new model",
    unit="kg",
)

scrap_tin_sanitary_311 = partial(
    byproduct,
    old_name="treatment of scrap tin sheet, sanitary landfill",
    new_name="treatment of waste tin sheet, sanitary landfill",
)

# Synthetic fuel production, from coal, high temperature Fisher-Tropsch operations in South Africa
# Completed changed but not well-documented in change report
syncoal_311 = partial(
    byproduct,
    old_name="synthetic fuel production, from coal, high temperature Fisher-Tropsch operations",
    unit="kg",
    geography="ZA",
    new_name="synthetic fuel production, from coal, high temperature Fischer-Tropsch operations",
)


TECHNOSPHERE_PATCHES_MISSING_DATA = {
    ("3.9.1", "3.10"): [
        {
            "source": {
                "name": "modified Solvay process, Hou's process",
                "location": "GLO",
                "reference product": "ammonium chloride",
                "unit": "kg",
            },
            "target": {
                "name": "soda ash production, dense, Hou's process",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "name": "Mannheim process",
                "location": "RER",
                "reference product": "sodium sulfate, anhydrite",
                "unit": "kg",
            },
            "target": {
                "name": "hydrochloric acid production, Mannheim process",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "name": "Mannheim process",
                "location": "RoW",
                "reference product": "sodium sulfate, anhydrite",
                "unit": "kg",
            },
            "target": {
                "name": "hydrochloric acid production, Mannheim process",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "name": "wheat production, Swiss integrated production, intensive",
                "location": "CH",
                "reference product": "straw",
                "unit": "kg",
            },
            "target": {
                "name": "wheat grain production, Swiss integrated production, intensive",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "name": "wheat production, Swiss integrated production, extensive",
                "location": "CH",
                "reference product": "straw",
                "unit": "kg",
            },
            "target": {
                "name": "wheat grain production, Swiss integrated production, extensive",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "name": "air separation, cryogenic",
                "reference product": "nitrogen, liquid",
                "location": "RER",
                "unit": "kg",
            },
            "target": {
                "name": "industrial gases production, cryogenic air separation",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "name": "air separation, cryogenic",
                "reference product": "nitrogen, liquid",
                "location": "RoW",
                "unit": "kg",
            },
            "target": {
                "name": "industrial gases production, cryogenic air separation",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "name": "air separation, cryogenic",
                "reference product": "argon, crude, liquid",
                "location": "RER",
                "unit": "kg",
            },
            "target": {
                "name": "industrial gases production, cryogenic air separation",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "name": "air separation, cryogenic",
                "reference product": "argon, crude, liquid",
                "location": "RoW",
                "unit": "kg",
            },
            "target": {
                "name": "industrial gases production, cryogenic air separation",
            },
            "comment": "By-product production missed in change report during name change",
        },
    ],
    ("3.10.1", "3.11"): (
        [syncoal_311(product=product) for product in SYNCOAL_PRODUCTS]
        + [
            {
                "source": {
                    "activity_name": "synthetic fuel production, from coal, high temperature Fisher-Tropsch operations",
                    "product_name": "1-butanol",
                    "unit": "kg",
                    "geography": "ZA",
                },
                "target": {
                    "activity_name": "synthetic fuel production, from coal, high temperature Fischer-Tropsch operations",
                    "product_name": "n-butanol",
                },
                "comment": "By-product production missed in change report during name change.",
            },
        ]
        + [
            scrap_tin_sanitary_311(product="electricity, medium voltage", unit="kWh", geography=geo)
            for geo in ("EC", "PE", "RoW")
        ]
        + [
            scrap_tin_sanitary_311(
                product="heat, district or industrial, other than natural gas",
                unit="MJ",
                geography=geo,
            )
            for geo in ("EC", "PE", "RoW")
        ]
        + [
            acetic_acid_production_311(geography=geo, product=product)
            for geo in ("RER", "RoW")
            for product in ACETIC_ACID_BYPRODUCTS
        ]
        + [
            # Natural gas transport modelling changed
            {
                "source": {
                    "activity_name": "natural gas, high pressure, import from NL",
                    "product_name": "natural gas, high pressure",
                    "unit": "m3",
                    "geography": "IT",
                },
                "target": {
                    "activity_name": "natural gas, high pressure, import from BE",
                },
                "comment": "3.11 change report section 5.3.3.4, Table 30. Hard to understand text above table 30; best-effort replacement activity.",
            },
            {
                "source": {
                    "activity_name": "natural gas, high pressure, import from NL",
                    "product_name": "natural gas, high pressure",
                    "unit": "m3",
                    "geography": "FR",
                },
                "target": {
                    "activity_name": "natural gas, high pressure, import from BE",
                },
                "comment": "3.11 change report section 5.3.3.4, Table 30. Hard to understand text above table 30; best-effort replacement activity.",
            },
            {
                "source": {
                    "activity_name": "natural gas, high pressure, import from NL",
                    "product_name": "natural gas, high pressure",
                    "unit": "m3",
                    "geography": "GB",
                },
                "target": {
                    "activity_name": "natural gas, high pressure, import from NO",
                },
                "comment": "3.11 change report section 5.3.3.4, Table 30. Hard to understand text above table 30; best-effort replacement activity.",
            },
            {
                "source": {
                    "activity_name": "natural gas, high pressure, import from FR",
                    "product_name": "natural gas, high pressure",
                    "unit": "m3",
                    "geography": "NL",
                },
                "target": {
                    "activity_name": "natural gas, high pressure, import from BE",
                },
                "comment": "3.11 change report section 5.3.3.4, Table 30. Hard to understand text above table 30; best-effort replacement activity.",
            },
            # Kraft paper update removed some by-products
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
                "comment": "By-product production removed and not documented in 3.11 change report (see section 14.2); Technology switch as best-effort replacement",
            },
            # Swiss crop production disaggregated by space and time missing by-products
            {
                "source": {
                    "activity_name": "wheat grain production, organic",
                    "product_name": "straw, organic",
                    "unit": "kg",
                    "geography": "CH",
                },
                "targets": [
                    {
                        f"activity_name": f"wheat grain production, {season}, organic, {region} region",
                    }
                    for season in ("spring", "winter")
                    for region in ("hill", "mountain", "plain")
                ]
                + [
                    {"activity_name": f"wheat grain, feed production, organic, {region} region"}
                    for region in ("hill", "mountain", "plain")
                ],
                "comment": "By-product production missed in change report during name change (see section 12.2)",
            },
            {
                "source": {
                    "activity_name": "barley grain production, organic",
                    "product_name": "straw, organic",
                    "unit": "kg",
                    "geography": "CH",
                },
                "targets": [
                    {
                        "activity_name": f"barley grain production, winter, organic, {region} region",
                    }
                    for region in ("hill", "mountain", "plain")
                ],
                "comment": "By-product production missed in change report during name change (see section 12.2)",
            },
            {
                "source": {
                    "activity_name": "rye production, organic",
                    "product_name": "straw, organic",
                    "unit": "kg",
                    "geography": "CH",
                },
                "targets": [
                    {
                        "activity_name": f"rye grain production, winter, organic, {region} region",
                    }
                    for region in ("hill", "mountain", "plain")
                ],
                "comment": "By-product production missed in change report during name change (see section 12.2)",
            },
            # This needs a more specialized approach as global average is 25 years out of date...
            # ] + [
            #     # Some natural gas transport datasets deleted
            #     {
            #         "source": {
            #             "activity_name": 'transport, pipeline, onshore, long distance, natural gas',
            #             "product_name": "transport, pipeline, onshore, long distance, natural gas",
            #             "unit": "metric ton*km",
            #             "geography": geo,
            #         },
            #         "target": {
            #             "activity_name": 'transport, pipeline, onshore, long distance, natural gas',
            #             "product_name": "transport, pipeline, onshore, long distance, natural gas",
            #             "unit": "metric ton*km",
            #             "geography": geo,
            #         }
            #         "comment": "By-product production missed in change report during name change (see section 12.2)",
            #     } for geo in ("AE","BR","CN","CO","DE","EC","GB","IQ","KW","MY","NG","QA","RO","SA","VE")
        ]
    ),
}


TECHNOSPHERE_PATCHES_REPLACEMENT_DATA = {
    # This is for cases where there is an entry in the change report, but that entry is incorrect.
    ("3.10.1", "3.11"): [
        # Misc. errors in change report or source data
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
            "comment": "Data error in change report geography.",
        },
        {
            "source": {
                "activity_name": "treatment of used refrigerant R134a, reclamation",
                "product_name": "used refrigerant R134a",
                "unit": "kg",
                "geography": "GLO",
            },
            "target": {"product_name": "refrigerant R134a"},
            "comment": "Data error in original dataset; should have treated used refrigerant. Change report assumes correct product.",
            "context": "source",
        },
        # Both change report and change documentation think product is `flakes`, but it's actually
        # `pellets`
        {
            "source": {
                "activity_name": "pelletising of polyethylene, high density",
                "geography": "RER",
                "product_name": "polyethylene, high density, flakes, recycled",
                "unit": "kg",
            },
            "target": {
                "product_name": "polyethylene, high density, pellets, recycled",
            },
            "context": "target",
            "comment": "Data error in change report product name.",
        },
        {
            "source": {
                "activity_name": "pelletising of polyethylene terephthalate",
                "geography": "RER",
                "product_name": "polyethylene terephthalate, flakes, recycled",
                "unit": "kg",
            },
            "target": {
                "product_name": "polyethylene terephthalate, pellets, recycled",
            },
            "context": "target",
            "comment": "Data error in change report product name.",
        },
        {
            "source": {
                "activity_name": "pelletising of polyethylene terephthalate, food grade",
                "geography": "RER",
                "product_name": "polyethylene terephthalate, flakes, food grade, recycled",
                "unit": "kg",
            },
            "target": {
                "product_name": "polyethylene terephthalate, pellets, food grade, recycled",
            },
            "context": "target",
            "comment": "Data error in change report product name.",
        },
        # Change report uses unsorted reference product
        {
            "source": {
                "activity_name": "treatment of waste polyethylene terephthalate, for recycling, unsorted, sorting",
                "geography": "CH",
                "product_name": "waste polyethylene terephthalate, for recycling, unsorted",
                "unit": "kg",
            },
            "target": {
                "product_name": "waste polyethylene terephthalate, for recycling, sorted",
            },
            "context": "source",
            "comment": "Change report has unsorted reference product, should be sorted.",
        },
        {
            "source": {
                "activity_name": "treatment of waste polyethylene terephthalate, for recycling, unsorted, sorting",
                "geography": "Europe without Switzerland",
                "product_name": "waste polyethylene terephthalate, for recycling, unsorted",
                "unit": "kg",
            },
            "target": {
                "product_name": "waste polyethylene terephthalate, for recycling, sorted",
            },
            "context": "source",
            "comment": "Change report has unsorted reference product, should be sorted.",
        },
        {
            "source": {
                "activity_name": "treatment of waste polyethylene terephthalate, for recycling, unsorted, sorting",
                "geography": "GLO",
                "product_name": "waste polyethylene terephthalate, for recycling, unsorted",
                "unit": "kg",
            },
            "target": {
                "product_name": "waste polyethylene terephthalate, for recycling, sorted",
            },
            "context": "target",
            "comment": "Change report has unsorted reference product, should be sorted.",
        },
    ]
}
