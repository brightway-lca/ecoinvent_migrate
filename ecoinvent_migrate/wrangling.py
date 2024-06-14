import itertools
import math
from numbers import Number
from typing import List

import bw2data as bd
from loguru import logger

from .errors import Mismatch, MissingDatabase, Uncombinable


def split_by_semicolon(row: dict, version: str) -> list[dict]:
    """Possible split a data row into"""
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
            "name": row[f"Activity Name - {version}"],
            "location": row[f"Geography - {version}"],
            "reference product": x,
            "unit": y,
        }
        for x, y in zip(
            row[f"Reference Product - {version}"].split(";\n"),
            row[f"Reference Product Unit - {version}"].split(";\n"),
        )
    ]


def source_target_pair_as_bw_dict(
    row: dict, source_version: str, target_version: str
) -> list[dict]:
    """Transform a row from the change report dataframe into one or more dicts.

    Can be more than one because the change report is for master data which can have
    multiple reference products.

    Only include the attributes we use for linking:

    * name
    * reference product
    * unit
    * location

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
    >>> source_target_pair_as_bw_dict(given)
    [{
        'source': {
            'name': 'baling',
            'location': 'GLO',
            'reference product': 'baling',
            'unit': 'unit'
        },
        'target': {
            'name': 'baling',
            'location': 'GLO',
            'reference product': 'baling',
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
    >>> source_target_pair_as_bw_dict(given)
    [{
        'source': {
            'name': 'autoclaved aerated concrete block production',
            'location': 'IN',
            'reference product': 'autoclaved aerated concrete block',
            'unit': 'kg'
        },
        'target': {
            'name': 'autoclaved aerated concrete block production',
            'location': 'IN',
            'reference product': 'autoclaved aerated concrete block',
            'unit': 'kg'
        }
    }, {
        'source': {
            'name': 'autoclaved aerated concrete block production',
            'location': 'IN',
            'reference product': 'hard coal ash',
            'unit': 'kg'
        },
        'target': {
            'name': 'autoclaved aerated concrete block production',
            'location': 'IN',
            'reference product': 'hard coal ash',
            'unit': 'kg'
        }
    }]
    ```

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
        return [{"source": sources[0], "target": targets[0]}]
    elif len(sources) == 1:
        sources = itertools.repeat(sources[0])
    elif len(targets) == 1:
        targets = itertools.repeat(targets[0])

    return [
        {"source": s, "target": t}
        for s, t in zip(sources, targets)
        if all(v.lower() != "nan" for v in itertools.chain(s.values(), t.values()))
    ]


def resolve_glo_row_rer_roe(
    data: List[dict], source_version: str, target_version: str, system_model: str
) -> List[dict]:
    """Iterate through `data`, and change `location` attribute to `RoW` or `RoE` when needed.

    Looks in actual database to get correct `location` attributes."""
    source_db_name = f"ecoinvent-{source_version}-{system_model}"
    target_db_name = f"ecoinvent-{target_version}-{system_model}"
    if source_db_name not in bd.databases:
        raise MissingDatabase(f"Missing source database: {source_db_name}")
    if target_db_name not in bd.databases:
        raise MissingDatabase(f"Missing target database: {target_db_name}")

    logger.info("Loading source database {db} to cache data attributes", db=source_db_name)
    source_lookup = {
        tuple([o[attr] for attr in ("name", "location", "reference product")])
        for o in bd.Database(source_db_name)
    }
    logger.info("Loading target database {db} to cache data attributes", db=target_db_name)
    target_lookup = {
        tuple([o[attr] for attr in ("name", "location", "reference product")])
        for o in bd.Database(target_db_name)
    }

    for obj in data:
        source_missing = None
        for kind, lookup, db_name in [
            ("source", source_lookup, source_db_name),
            ("target", target_lookup, target_db_name),
        ]:
            key = tuple([obj[kind][attr] for attr in ("name", "location", "reference product")])
            if key in lookup:
                continue
            elif (
                key not in lookup
                and obj[kind]["location"] == "GLO"
                and (key[0], "RoW", key[2]) in lookup
            ):
                obj[kind]["location"] = "RoW"
                logger.debug(
                    "{kind} process {name} location corrected to 'RoW'",
                    kind=kind,
                    name=obj[kind]['name'],
                )
            elif (
                key not in lookup
                and obj[kind]["location"] == "RER"
                and (key[0], "RoE", key[2]) in lookup
            ):
                obj[kind]["location"] = "RoE"
                logger.debug(
                    "{kind} process {name} location corrected to 'RoE'",
                    kind=kind,
                    name=obj[kind]['name'],
                )
            else:
                if kind == 'target' and source_missing:
                    # Missing in both source and target for this system model
                    source_missing = None
                    continue
                elif kind == "source":
                    source_missing = obj[kind]
                else:
                    # Only missing in target database - but this is a big problem, we don't have a
                    # suitable target for existing edges to relink to.
                    logger.warning(
                        "{kind.title()} process given in change report but missing in {db_name} lookup: {ds}",
                        kind=kind,
                        db_name=db_name,
                        ds=obj[kind],
                    )
                # raise KeyError(
                #     f"""Can't find {kind} object in database {db_name}: {obj[kind]}"""
                # )
        if source_missing:
            # Only a debug message because this won't break anything - there is no process in the
            # source database to miss a link from.
            logger.debug(
                "Source process given in change report but missing in {db_name} lookup: {ds}",
                db_name=source_db_name,
                ds=source_missing,
            )

    return data
