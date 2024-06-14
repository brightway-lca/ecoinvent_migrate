from pathlib import Path
from typing import Optional

import bw2data as bd
import bw2io as bi
from ecoinvent_interface import EcoinventRelease
from loguru import logger

from .errors import MissingDatabase


def get_change_report_filepath(version: str, release: EcoinventRelease) -> Path:
    """Get the filepath to the Excel change report file"""
    files = release.list_extra_files(version)
    candidates = [key for key in files if "change report" in key.lower() and "annex" in key.lower()]
    if not candidates:
        raise ValueError(
            "Can't find suitable change report filename from release files:\n\t{}".format(
                "\n\t".join([f.name for f in files])
            )
        )
    elif len(candidates) > 1:
        raise ValueError(
            "Found multiple candidates for change report filename:\n\t{}".format(
                "\n\t".join([c.name for c in candidates])
            )
        )

    files = list(release.get_extra(version, candidates[0]).iterdir())
    candidates = [
        fp
        for fp in files
        if (
            fp.name.lower().startswith("change report annex")
            or fp.name.lower().startswith("change_report_annex")
        )
        and fp.suffix.lower() == ".xlsx"
    ]
    if not candidates:
        raise ValueError(
            "Can't find suitable change report file from archive:\n\t{}".format(
                "\n\t".join([f.name for f in files])
            )
        )
    elif len(candidates) > 1:
        raise ValueError(
            "Found multiple candidates for change report file:\n\t{}".format(
                "\n\t".join([c.name for c in candidates])
            )
        )
    return candidates[0]


def setup_project(
    source_version: str,
    target_version: str,
    project_name: str,
    system_model: str = "cutoff",
    ecoinvent_username: Optional[str] = None,
    ecoinvent_password: Optional[str] = None,
) -> None:
    bd.projects.set_current(project_name)

    if f"ecoinvent-{source_version}-{system_model}" not in bd.databases:
        logger.info(
            "Downloading ecoinvent source version {version} {system_model} to resolve GLO/RoW and RER/RoE",
            version=source_version,
            system_model=system_model,
        )
        bi.import_ecoinvent_release(
            source_version,
            system_model,
            lcia=False,
            username=ecoinvent_username,
            password=ecoinvent_password,
        )
    if f"ecoinvent-{target_version}-{system_model}" not in bd.databases:
        logger.info(
            "Downloading ecoinvent target version {version} {system_model} to resolve GLO/RoW and RER/RoE",
            version=target_version,
            system_model=system_model,
        )
        bi.import_ecoinvent_release(
            target_version,
            system_model,
            lcia=False,
            username=ecoinvent_username,
            password=ecoinvent_password,
        )


def get_brightway_databases(source_version: str, target_version: str, system_model: str):
    source_db_name = f"ecoinvent-{source_version}-{system_model}"
    target_db_name = f"ecoinvent-{target_version}-{system_model}"
    if source_db_name not in bd.databases:
        raise MissingDatabase(f"Missing source database: {source_db_name}")
    if target_db_name not in bd.databases:
        raise MissingDatabase(f"Missing target database: {target_db_name}")

    logger.info("Loading source database {db} to cache data attributes", db=source_db_name)
    source_lookup = {
        tuple([o[attr] for attr in ("name", "location", "reference product")]): o
        for o in bd.Database(source_db_name)
    }
    logger.info("Loading target database {db} to cache data attributes", db=target_db_name)
    target_lookup = {
        tuple([o[attr] for attr in ("name", "location", "reference product")]): o
        for o in bd.Database(target_db_name)
    }
    return source_db_name, target_db_name, source_lookup, target_lookup
