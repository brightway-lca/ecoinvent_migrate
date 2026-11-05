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
                "activity_name": "modified Solvay process, Hou's process",
                "geography": "GLO",
                "product_name": "ammonium chloride",
                "unit": "kg",
            },
            "target": {
                "activity_name": "soda ash production, dense, Hou's process",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "activity_name": "Mannheim process",
                "geography": "RER",
                "product_name": "sodium sulfate, anhydrite",
                "unit": "kg",
            },
            "target": {
                "activity_name": "hydrochloric acid production, Mannheim process",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "activity_name": "Mannheim process",
                "geography": "RoW",
                "product_name": "sodium sulfate, anhydrite",
                "unit": "kg",
            },
            "target": {
                "activity_name": "hydrochloric acid production, Mannheim process",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "activity_name": "wheat production, Swiss integrated production, intensive",
                "geography": "CH",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "activity_name": "wheat grain production, Swiss integrated production, intensive",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "activity_name": "wheat production, Swiss integrated production, extensive",
                "geography": "CH",
                "product_name": "straw",
                "unit": "kg",
            },
            "target": {
                "activity_name": "wheat grain production, Swiss integrated production, extensive",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "activity_name": "air separation, cryogenic",
                "product_name": "nitrogen, liquid",
                "geography": "RER",
                "unit": "kg",
            },
            "target": {
                "activity_name": "industrial gases production, cryogenic air separation",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "activity_name": "air separation, cryogenic",
                "product_name": "nitrogen, liquid",
                "geography": "RoW",
                "unit": "kg",
            },
            "target": {
                "activity_name": "industrial gases production, cryogenic air separation",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "activity_name": "air separation, cryogenic",
                "product_name": "argon, crude, liquid",
                "geography": "RER",
                "unit": "kg",
            },
            "target": {
                "activity_name": "industrial gases production, cryogenic air separation",
            },
            "comment": "By-product production missed in change report during name change",
        },
        {
            "source": {
                "activity_name": "air separation, cryogenic",
                "product_name": "argon, crude, liquid",
                "geography": "RoW",
                "unit": "kg",
            },
            "target": {
                "activity_name": "industrial gases production, cryogenic air separation",
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
    # Change report v3.12 - v3.13 only lists reference products; these by-products follow
    # their parent activity's mapping. Not patched (no equivalent in 3.13):
    #   * bark chips from folding boxboard carton production (by-product dropped)
    #   * steam (kg) from formaldehyde production, methanol oxidation; now
    #     "heat, from steam, in chemical industry" in MJ with no documented conversion
    #   * NL residual mix electricity datasets (deleted, no replacement)
    ("3.12", "3.13"): (
        [
            byproduct(
                old_name="propylene oxide production, from isobutene, PO/TBA process",
                new_name="propylene oxide production, from isobutane, PO/TBA process",
                product="tert-butanol",
                geography=geo,
                unit="kg",
            )
            for geo in ("RER", "US")
        ]
        + [
            byproduct(
                old_name=old_name,
                new_name="cartonboard production, virgin",
                product="turpentine",
                geography=geo,
                unit="kg",
            )
            for old_name, geo in (
                ("folding boxboard carton production", "RER"),
                ("folding boxboard carton production", "RoW"),
                ("solid bleached and unbleached board carton production", "RER"),
            )
        ]
        + [
            # APOS only; skipped in other system models where this by-product has no dataset
            byproduct(
                old_name=old_name,
                new_name=new_name,
                product="waste paper, sorted",
                geography=geo,
                unit="kg",
            )
            for old_name, new_name in (
                ("folding boxboard carton production", "cartonboard production, virgin"),
                ("white lined chipboard carton production", "cartonboard production, recycled"),
            )
            for geo in ("RER", "RoW")
        ]
        + [
            byproduct(
                old_name="calcined petroleum coke production",
                new_name="calcined petroleum coke production, vertical shaft",
                product="gypsum, mineral",
                geography="CN",
                unit="kg",
            )
        ]
        + [
            {
                "source": {
                    "activity_name": "lithium carbonate production, from spodumene",
                    "product_name": "sodium sulfate, anhydrite",
                    "unit": "kg",
                    "geography": geo,
                },
                "target": {
                    "activity_name": "lithium carbonate production, battery grade, from spodumene concentrate, Shehong",
                    "geography": "CN",
                },
                "comment": "By-product production missed in change report during name change; follows reference product mapping",
            }
            for geo in ("CN", "RoW")
        ]
        + [
            {
                "source": {
                    "activity_name": "treatment of used Li-ion battery, hydrometallurgical treatment",
                    "product_name": "lithium carbonate",
                    "unit": "kg",
                    "geography": "GLO",
                },
                "target": {
                    "product_name": "lithium carbonate, battery grade",
                },
                "comment": "By-product renamed and not documented in change report",
            }
        ]
    ),
}


TECHNOSPHERE_PATCHES_REPLACEMENT_DATA = {
    # This is for cases where there is an entry in the change report, but that entry is incorrect.
    #
    # The change report describes the unallocated database, not any system model, so a correction
    # can be right for one system model and wrong for another. Patches which only apply to some
    # system models list them in `system_models`; patches without it apply to all. Lists were set
    # by checking which system models contain the patched (and the unpatched) dataset.
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
            # Consequential 3.10.1 only has `used refrigerant R134a`, which the change report
            # already gives correctly
            "system_models": ["cutoff", "apos", "EN15804"],
        },
        # Both change report and change documentation think product is `flakes`, but it's actually
        # `pellets` in cutoff, APOS (food grade only) and EN15804. Consequential 3.11 has `flakes`,
        # so the change report is correct there. APOS 3.11 has no non-food grade pelletising
        # datasets at all.
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
            "system_models": ["cutoff", "EN15804"],
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
            "system_models": ["cutoff", "EN15804"],
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
            "system_models": ["cutoff", "apos", "EN15804"],
        },
        # Change report uses unsorted reference product. That's correct for consequential and
        # EN15804, where the reference product is the unsorted waste; cutoff uses the sorted
        # output. APOS 3.10.1 only has a RoW dataset, and APOS 3.11 has both products.
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
            "system_models": ["cutoff"],
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
            "system_models": ["cutoff"],
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
            "system_models": ["cutoff", "apos"],
        },
    ]
}

ALLYL_ALCOHOL_COMMENT = (
    "Deleted in change report without replacement; same substance (CAS 107-18-6) as existing "
    "flow 'Allyl alcohol'"
)

# Manual biosphere `replace` patches. These override change report entries with the same source UUID.
BIOSPHERE_PATCHES = {
    # v3.12 - v3.13 change report deletes 2-Propen-1-ol without replacement, but it is the same
    # substance (CAS 107-18-6) as the existing "Allyl alcohol" flows. There are no soil
    # "Allyl alcohol" flows, so those stay as deletions.
    ("3.12", "3.13"): [
        {
            "source": {
                "uuid": "0e1ad87f-928a-5f2e-990c-8f431f261416",
                "name": "2-Propen-1-ol",
                "context": ["air", "non-urban air or from high stacks"],
            },
            "target": {
                "uuid": "c8d084b4-a980-49a3-a385-8476ed020c6b",
                "name": "Allyl alcohol",
                "context": ["air", "unspecified"],
            },
            "comment": ALLYL_ALCOHOL_COMMENT + "; subcompartment 'non-urban air or from high stacks' not available, mapped to unspecified",
        },
        {
            "source": {
                "uuid": "f8828e44-6c1e-50ee-afa4-1b2f2a89590c",
                "name": "2-Propen-1-ol",
                "context": ["air", "unspecified"],
            },
            "target": {
                "uuid": "c8d084b4-a980-49a3-a385-8476ed020c6b",
                "name": "Allyl alcohol",
                "context": ["air", "unspecified"],
            },
            "comment": ALLYL_ALCOHOL_COMMENT,
        },
        {
            "source": {
                "uuid": "13368c7b-d50e-5559-b4dc-9b7bf9ef32d0",
                "name": "2-Propen-1-ol",
                "context": ["water", "surface water"],
            },
            "target": {
                "uuid": "3dbfcc62-4898-48a7-969b-74270615e36e",
                "name": "Allyl alcohol",
                "context": ["water", "unspecified"],
            },
            "comment": ALLYL_ALCOHOL_COMMENT + "; subcompartment 'surface water' not available, mapped to unspecified",
        },
        {
            "source": {
                "uuid": "0d8d3729-7b68-5669-bc51-fa692e31c561",
                "name": "2-Propen-1-ol",
                "context": ["water", "unspecified"],
            },
            "target": {
                "uuid": "3dbfcc62-4898-48a7-969b-74270615e36e",
                "name": "Allyl alcohol",
                "context": ["water", "unspecified"],
            },
            "comment": ALLYL_ALCOHOL_COMMENT,
        },
    ],
}
