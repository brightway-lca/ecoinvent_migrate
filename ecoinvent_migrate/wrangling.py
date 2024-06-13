import itertools

from .errors import Mismatch, Uncombinable


def split_by_semicolon(row: dict, version: str) -> list[dict]:
    """Possible split a data row into"""
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
    versions = [
        x.split(" - ")[-1].strip() for x in row if x.startswith("Activity Name")
    ]
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

    return [{"source": s, "target": t} for s, t in zip(sources, targets)]
