import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from loguru import logger
from platformdirs import user_data_dir

from . import __version__


def write_datapackage(
    data: dict,
    source_db_name: str,
    target_db_name: str,
    licenses: Optional[List[dict]] = None,
    output_directory: Optional[Path] = None,
    version: str = "1.0.0",
    description: Optional[str] = None,
) -> Path:
    now = datetime.now(timezone.utc).isoformat()
    if licenses is None:
        licenses = [
            {
                "name": "CC BY 4.0",
                "path": "https://creativecommons.org/licenses/by/4.0/",
                "title": "Creative Commons Attribution 4.0 International",
            }
        ]
    if description is None:
        description = f"Data migration file from {source_db_name} to {target_db_name} generated with `ecoinvent_migrate` version {__version__} at {now}"

    formatted = {
        "name": f"{source_db_name}-{target_db_name}",
        "licenses": licenses,
        "version": version,
        "description": description,
        "homepage": "https://github.com/brightway-lca/ecoinvent_migrate",
        "created": now,
        "contributors": [
            {"title": "ecoinvent association", "path": "https://ecoinvent.org/", "role": "author"},
            {"title": "Chris Mutel", "path": "https://chris.mutel.org/", "role": "wrangler"},
        ],
    } | data

    if output_directory is None:
        output_directory = Path(user_data_dir("ecoinvent_migrate", "pylca"))
        output_directory.mkdir(parents=True, exist_ok=True)
    elif not isinstance(output_directory, Path):
        raise ValueError(
            f"`output_directory` must be a `Path` instance; got {type(output_directory)}"
        )
    elif not output_directory.is_dir() or not os.access(output_directory, os.W_OK):
        raise ValueError(f"`output_directory` {output_directory} must be a writable directory")

    fp = output_directory / f"{source_db_name}-{target_db_name}.json"
    logger.info("Writing output file {fp}", fp=str(fp))
    with open(fp, "w") as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)

    return fp
