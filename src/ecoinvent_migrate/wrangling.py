import itertools
import math
from collections import defaultdict
from copy import copy
from numbers import Number
from typing import List, Union

from loguru import logger

from ecoinvent_migrate.errors import Mismatch, Uncombinable


def isnan(o: Union[str, Number]) -> bool:
    return isinstance(o, Number) and math.isnan(o)


def tuple_key_for_data(obj: dict) -> tuple:
    if "reference product" in obj:
        return tuple([obj[field] for field in ("name", "location", "reference product", "unit")])
    else:
        return tuple(
            [obj[field] for field in ("activity_name", "geography", "product_name", "unit")]
        )


def split_by_semicolon(row: dict, version: str) -> list[dict]:
    """Turn a data `row` into one or more dictionaries.

    Splits reference product and unit values by `;\n`."""
    if isinstance(row[f"Activity Name - {version}"], Number) and math.isnan(
        row[f"Activity Name - {version}"]
    ):
        return []

    len_product = len(row[f"Reference Product - {version}"].split(";\n"))
    len_unit = len(row[f"Reference Product Unit - {version}"].split(";\n"))
    if len_product != len_unit:
        raise Mismatch(f"Can't match {len_product} products to {len_unit} units")

    return [
        {
            "activity_name": row[f"Activity Name - {version}"],
            "geography": row[f"Geography - {version}"],
            "product_name": x,
            "unit": y,
        }
        for x, y in zip(
            row[f"Reference Product - {version}"].split(";\n"),
            row[f"Reference Product Unit - {version}"].split(";\n"),
        )
    ]


def relabel(obj: dict) -> dict:
    """Change from ecospold2-ish labels to Randonneur constants.ECOSPOLD2 labels"""
    obj = copy(obj)
    obj["name"] = obj.pop("activity_name")
    obj["reference product"] = obj.pop("product_name")
    obj["location"] = obj.pop("geography")
    return obj


def source_target_pair_as_dict(
    row: dict, row_index: int, filename: str, source_version: str, target_version: str
) -> list[dict]:
    """Transform a row from the change report dataframe into one or more dicts.

    Can be more than one because the change report is for master data which can have
    multiple reference products.

    Only include the attributes we use for linking:

    * activity_name
    * product_name
    * unit
    * geography

    Example usage:

    ```python
    >>> given = {
        'Activity Name - 3.9.1': 'baling',
        'Geography - 3.9.1': 'GLO',
        'Reference Product - 3.9.1': 'baling',
        'Reference Product Unit - 3.9.1': 'unit',
        'Activity Name - 3.10': 'baling',
        'Geography - 3.10': 'GLO',
        'Reference Product - 3.10': 'baling',
        'Reference Product Unit - 3.10': 'unit',
    }
    >>> source_target_pair_as_dict(given)
    [{
        'source': {
            'activity_name': 'baling',
            'geography': 'GLO',
            'product_name': 'baling',
            'unit': 'unit'
        },
        'target': {
            'name': 'baling',
            'geography': 'GLO',
            'product_name': 'baling',
            'unit': 'unit'
        }
    }]
    ```

    But multiple pairs are returned when more than one reference product is present:

    ```python
    >>> given = {
        'Activity Name - 3.9.1': 'autoclaved aerated concrete block production',
        'Geography - 3.9.1': 'IN',
        'Reference Product - 3.9.1': 'autoclaved aerated concrete block;\nhard coal ash',
        'Reference Product Unit - 3.9.1': 'kg;\nkg',
        'Activity Name - 3.10': 'autoclaved aerated concrete block production',
        'Geography - 3.10': 'IN',
        'Reference Product - 3.10': 'autoclaved aerated concrete block;\nhard coal ash',
        'Reference Product Unit - 3.10': 'kg;\nkg',
    }
    >>> source_target_pair_as_dict(given)
    [{
        'source': {
            'activity_name': 'autoclaved aerated concrete block production',
            'geography': 'IN',
            'product_name': 'autoclaved aerated concrete block',
            'unit': 'kg'
        },
        'target': {
            'activity_name': 'autoclaved aerated concrete block production',
            'geography': 'IN',
            'product_name': 'autoclaved aerated concrete block',
            'unit': 'kg'
        }
    }, {
        'source': {
            'activity_name': 'autoclaved aerated concrete block production',
            'geography': 'IN',
            'product_name': 'hard coal ash',
            'unit': 'kg'
        },
        'target': {
            'activity_name': 'autoclaved aerated concrete block production',
            'geography': 'IN',
            'product_name': 'hard coal ash',
            'unit': 'kg'
        }
    }]
    ```

    The line breaks are in the change report, and are from individual rows which refer to multiple
    products.

    """
    versions = [x.split(" - ")[-1].strip() for x in row if x.startswith("Activity Name")]
    if f"Activity Name - {source_version}" not in row:
        raise ValueError(
            f"""Can't find source version {source_version} in data row.
    Versions found: {versions}"""
        )
    if f"Activity Name - {target_version}" not in row:
        raise ValueError(
            f"""Can't find target version {target_version} in data row.
    Versions found: {versions}"""
        )

    sources = split_by_semicolon(row, source_version)
    if not sources:
        # New unit process dataset, no source objects
        return []

    targets = split_by_semicolon(row, target_version)
    if len(sources) > 1 and len(targets) > 1 and len(sources) != len(targets):
        raise Uncombinable(
            f"Can't do M:N combination of {len(sources)} source and {len(targets)} target datasets."
        )
    elif len(sources) == 1 and len(targets) == 1:
        return [
            {
                "source": sources[0],
                "target": targets[0],
                "comment": f"Line {row_index} in change report file `{filename}`",
            }
        ]
    elif len(sources) == 1:
        sources = itertools.repeat(sources[0])
    elif len(targets) == 1:
        targets = itertools.repeat(targets[0])

    return [
        {
            "source": s,
            "target": t,
            "comment": f"Line {row_index} in change report file `{filename}`",
        }
        for s, t in zip(sources, targets)
        if all(v.lower() != "nan" for v in itertools.chain(s.values(), t.values()))
    ]


def resolve_glo_row_rer_roe(
    data: List[dict],
    source_db_name: str,
    target_db_name: str,
    source_lookup: dict,
    target_lookup: dict,
) -> List[dict]:
    """Iterate through `data`, and change `geography` attribute to `RoW` or `RoE` when needed.

    Looks in actual database to get correct `geography` attributes."""

    warned = set()

    for obj in data:
        source_missing = None
        for kind, lookup, db_name in [
            ("source", source_lookup, source_db_name),
            ("target", target_lookup, target_db_name),
        ]:
            key = tuple_key_for_data(obj[kind])
            if key in lookup:
                continue
            elif (
                key not in lookup
                and obj[kind]["geography"] == "GLO"
                and (key[0], "RoW", key[2], key[3]) in lookup
            ):
                obj[kind]["geography"] = "RoW"
                logger.debug(
                    "{kind} process {name} geography corrected to 'RoW'",
                    kind=kind,
                    name=obj[kind]["activity_name"],
                )
            elif (
                key not in lookup
                and obj[kind]["geography"] == "RER"
                and (key[0], "RoE", key[2], key[3]) in lookup
            ):
                obj[kind]["geography"] = "RoE"
                logger.debug(
                    "{kind} process {name} geography corrected to 'RoE'",
                    kind=kind,
                    name=obj[kind]["activity_name"],
                )
            else:
                if kind == "target" and source_missing:
                    # Missing in both source and target for this system model
                    source_missing = None
                    continue
                elif kind == "source":
                    source_missing = obj[kind]
                else:
                    # Only missing in target database - but this is a big problem, we don't have a
                    # suitable target for existing edges to relink to.
                    if key := tuple_key_for_data(obj[kind]) not in warned:
                        warned.add(key)
                        logger.warning(
                            "{kind} process given in change report but missing in {db_name} lookup: {ds}",
                            kind=kind.title(),
                            db_name=db_name,
                            ds=obj[kind],
                        )
        if source_missing:
            # Only a debug message because this won't break anything - there is no process in the
            # source database to miss a link from.
            logger.debug(
                "Source process given in change report but missing in {db_name} lookup: {ds}",
                db_name=source_db_name,
                ds=source_missing,
            )

    return data


def disaggregated(data: List[dict], lookup: dict) -> dict:
    """Take a list of mapping dictionaries with the same `source`, and create one `disaggregate`
    object.

    Applies `allocation` factors based on the production volumes in `lookup`

    """
    for obj in data:
        try:
            obj["pv"] = lookup[tuple_key_for_data(obj["target"])]["production_volume"]
        except KeyError:
            logger.warning(
                """Change report annex dataset missing from database.
    This is likely a publication error which you can't fix.
    Removing the following from migrations:
    {ds}""",
                ds=obj["target"],
            )
            obj["pv"] = 0

    total = sum(obj["pv"] for obj in data)
    if not total:
        logger.warning(
            "Total production from {n} targets is zero for source {s}; using equal allocation factors",
            n=len(data),
            s=data[0]["source"],
        )
        return {
            "source": data[0]["source"],
            "targets": [obj["target"] | {"allocation": 1 / len(data)} for ob in data],
        }
    elif total < 0:
        logger.warning(
            "Total production from {n} targets is less than zero for source {s}; what is happening!?",
            n=len(data),
            s=data[0]["source"],
        )

    return {
        "source": data[0]["source"],
        "targets": [obj["target"] | {"allocation": obj["pv"] / total} for obj in data if obj["pv"]],
    }


def split_replace_disaggregate(data: List[dict], target_lookup: dict) -> dict:
    """Split the transformations in `data` into `replace` and `disaggregate` sections.

    Disaggregation is needed when one dataset is replaced by multiple datasets. We lookup the
    respective production volumes to get the disaggregation factors."""
    groupie = defaultdict(list)
    for obj in data:
        groupie[tuple_key_for_data(obj["source"])].append(obj)

    return {
        "replace": [
            value[0]
            for value in groupie.values()
            if len(value) == 1 and value[0]["source"] != value[0]["target"]
        ],
        "disaggregate": [
            disaggregated(value, target_lookup) for value in groupie.values() if len(value) > 1
        ],
    }


def get_column_labels(example: dict, version: str) -> dict:
    """Guess column labels from Excel change report annex.

    Now handles multiple formats:
    - Standard format: "UUID/ID - version"
    - New format: Where labels might be in values
    """
    uuid_tries = [f"UUID - {version}", f"ID - {version}"]
    name_tries = [f"Name - {version}", f"{version} name", f"{version} - name"]

    # Try standard format first
    for uuid_try in uuid_tries:
        if uuid_try in example:
            uuid = uuid_try
            break
    else:
        # If standard format fails, check for new format
        for key, value in example.items():
            if isinstance(value, str) and any(try_pattern in value for try_pattern in uuid_tries):
                uuid = key
                break
        else:
            raise ValueError(f"Can't find uuid field for database version {version} in {example}")

    # Same pattern for name
    for name_try in name_tries:
        if name_try in example:
            name = name_try
            break
    else:
        for key, value in example.items():
            if isinstance(value, str) and any(try_pattern in value for try_pattern in name_tries):
                name = key
                break
        else:
            raise ValueError(f"Can't find name field for database version {version} in {example}")

    return {
        "uuid": uuid,
        "name": name,
    }


def source_target_biosphere_pair(
    data: List[dict], source_version: str, target_version: str, keep_deletions: bool
) -> List[dict]:
    """Turn pandas DataFrame rows into source/target pairs.

    The function now handles both old and new EE Deletions formats:
    - Old format: Direct source/target columns
    - New format: Deletion/replacement columns with explicit relationships
    """
    # For empty data, return empty structure
    if not data:
        return {"replace": [], "delete": []}

    # Try old format first
    source_labels = get_column_labels(example=data[0], version=source_version)
    target_labels = get_column_labels(example=data[0], version=target_version)

    # Initialize the result structure
    formatted = {"replace": [], "delete": [] if keep_deletions else None}

    # Process each row
    for row in data:
        # Skip empty or invalid rows
        if any(isnan(row.get(v)) for v in source_labels.values()):
            continue

        # Create source entry
        source_entry = {k: row[v].strip() for k, v in source_labels.items()}

        # Check if there's a valid target
        has_target = not any(isnan(row.get(v, float("nan"))) for v in target_labels.values())

        if has_target:
            comment_val = row.get("Comment")
            formatted["replace"].append(
                {
                    "source": source_entry,
                    "target": {k: row[v].strip() for k, v in target_labels.items()},
                    "conversion_factor": float(row.get("Conversion Factor (old-new)", 1.0)),
                    # Check if comment is a string before stripping, otherwise use empty string
                    "comment": comment_val.strip() if isinstance(comment_val, str) else "",
                }
            )
        elif keep_deletions:
            comment_val = row.get("Comment")
            formatted["delete"].append(
                {
                    "source": source_entry,
                    # Check if comment is a string before stripping, otherwise use empty string
                    "comment": comment_val.strip() if isinstance(comment_val, str) else "",
                }
            )

    # Clean up the formatted data
    for lst in formatted.values():
        if lst is None:
            continue
        for obj in lst:
            if "comment" in obj and (not obj["comment"] or isnan(obj["comment"])):
                del obj["comment"]
            if "conversion_factor" in obj and (
                obj["conversion_factor"] == 1.0 or isnan(obj["conversion_factor"])
            ):
                del obj["conversion_factor"]

    # Remove empty delete list if not keeping deletions
    if not keep_deletions:
        del formatted["delete"]

    return formatted


def apply_missing_patches(data: list[dict], patches: list[dict]) -> list[dict]:
    """
    Apply patches which add transformations missing from the change report.

    Patches can be 1-to-1 or disaggregation. Both versions take a complete `source` dictionary, and
    use the `target` dictionary to model the changes needed to make a successful migration. Normally
    the `target` dictionary only has the elements which change.

    1-to-1 patches look like this:

    ```python
    >>> patches = [{
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
    }]
    >>> apply_missing_patches([], patches)
    [{
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
    }]
    ```

    In disaggregation, instead of a `target` dictionary, there is a `targets` dictionary with
    multiple objects. The production volume of the targets will get added later with the
    `disaggregated` function. Disaggregation patches look like this:

    ```python
    >>> patches = [{
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
            }
        ],
        "comment": "Split of wheat production into many specific processes",
    }]
    >>> apply_missing_patches([], patches)
    [{
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
    }, {
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
    }]
    ```

    """
    for patch in patches:
        if "targets" in patch:
            for target in patch["targets"]:
                data.append(
                    {key: value for key, value in patch.items() if key != "targets"}
                    | {"target": copy(patch["source"]) | target}
                )
        else:
            data.append(
                {key: value for key, value in patch.items() if key != "target"}
                | {"target": copy(patch["source"]) | patch["target"]}
            )

    return data


def apply_replacement_patches(data: list[dict], patches: list[dict]) -> list[dict]:
    """
    Replace elements of existing `source` or `target` dictionaries in `data`.

    Uses `context` to determine which mapping dictionary to modify.
    """
    # These will be modified during the following loop, but we assume that the patches are
    # well-behaved and don't overlap.
    source_lookup = defaultdict(list)
    target_lookup = defaultdict(list)
    for obj in data:
        source_lookup[tuple_key_for_data(obj["source"])].append(obj)
        target_lookup[tuple_key_for_data(obj["target"])].append(obj)

    for patch in patches:
        patch_key = tuple_key_for_data(patch["source"])
        for kind, lookup in (("source", source_lookup), ("target", target_lookup)):
            if patch["context"] == kind:
                if patch_key not in lookup:
                    logger.warning(
                        "Expected to patch the following {k} dict but it's not in the given data: {p}",
                        k=kind,
                        p=patch["source"],
                    )
                    continue
                for obj in lookup[patch_key]:
                    logger.debug(
                        "Patching change report {k} {s} with updated values {t}",
                        k=kind,
                        s=obj,
                        t=patch["target"],
                    )
                    obj[kind].update(**patch["target"])
                    if "comment" in patch:
                        if "comment" in obj:
                            string = (
                                ("." if not obj["comment"].endswith(".") else "")
                                + f" Patched with comment '"
                                + patch["comment"]
                                + "'."
                            )
                            obj["comment"] += string
                        else:
                            obj["comment"] = patch["comment"]
    return data
