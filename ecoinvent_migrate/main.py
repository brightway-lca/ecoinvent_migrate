import warnings
from pathlib import Path
from typing import List, Optional, Union
import itertools

import pandas as pd
from ecoinvent_interface import EcoinventRelease, Settings, ReleaseType, CachedStorage
from loguru import logger
from randonneur import Datapackage, MappingConstants
import xmltodict

from . import __version__
from .data_io import get_brightway_databases, get_change_report_filepath, setup_project
from .errors import VersionJump
from .patches import TECHNOSPHERE_PATCHES
from .utils import configure_logs, setup_output_directory
from .wrangling import (
    resolve_glo_row_rer_roe,
    source_target_biosphere_pair,
    source_target_pair_as_bw_dict,
    split_replace_disaggregate,
)


def get_change_report_context(
    source_version: str,
    target_version: str,
    project_name: str,
    system_model: str = "cutoff",
    ecoinvent_username: Optional[str] = None,
    ecoinvent_password: Optional[str] = None,
) -> Path:
    """Get the source/target change report filepath, and setup Brightway project with needed data.

    Source and target must be one release apart from each other, i.e. 3.4 to 3.5 or 3.7 to 3.7.1.

    Returns the `Path` of the generated file."""
    if ecoinvent_username is not None or ecoinvent_password is not None:
        warnings.warn(
            """
Username and/or password supplied via function call.
Please consider setting these permanently. See:
https://github.com/brightway-lca/ecoinvent_interface?tab=readme-ov-file#authentication-via-settings-object
            """
        )
        settings = Settings(username=ecoinvent_username, password=ecoinvent_password)
    else:
        settings = Settings()
    release = EcoinventRelease(settings)
    versions = release.list_versions()

    if source_version not in versions:
        raise ValueError(
            f"Given source version {source_version} not in available versions: {versions}"
        )
    if target_version not in versions:
        raise ValueError(
            f"Given target version {source_version} not in available versions: {versions}"
        )

    logger.info("Versions available for this license: {versions}", versions=versions)

    excel_filepath = get_change_report_filepath(version=target_version, release=release)
    if source_version not in excel_filepath.name.replace(target_version, ""):
        raise VersionJump(
            f"""
Source ({source_version}) and target ({target_version}) don't have a change report.
Usually this is the case when one jumps across multiple releases, but not always.
For example, the change report for 3.7.1 is from 3.6, not 3.7.
The change report we have available is:
{excel_filepath.name}
        """
        )
    logger.info("Using change report annex file {filename}", filename=excel_filepath.name)

    setup_project(
        source_version=source_version,
        target_version=target_version,
        project_name=project_name,
        system_model=system_model,
        ecoinvent_username=ecoinvent_username,
        ecoinvent_password=ecoinvent_password,
    )
    return excel_filepath


def generate_technosphere_mapping(
    source_version: str,
    target_version: str,
    project_name: str = "ecoinvent-migration",
    system_model: str = "cutoff",
    ecoinvent_username: Optional[str] = None,
    ecoinvent_password: Optional[str] = None,
    write_logs: bool = True,
    write_file: bool = True,
    licenses: Optional[List[dict]] = None,
    output_directory: Optional[Path] = None,
    output_version: str = "2.0.0",
    description: Optional[str] = None,
) -> Union[Path, Datapackage]:
    """Generate a Randonneur mapping file for technosphere edge attributes from source to target."""
    configure_logs(write_logs=write_logs)

    excel_filepath = get_change_report_context(
        source_version=source_version,
        target_version=target_version,
        project_name=project_name,
        ecoinvent_username=ecoinvent_username,
        ecoinvent_password=ecoinvent_password,
    )

    sheet_names = pd.ExcelFile(excel_filepath).sheet_names
    candidates = [name for name in sheet_names if name.lower() == "qualitative changes"]
    if not candidates:
        raise ValueError(
            "Can't find suitable sheet name in change report file. Looking for 'qualitative changes', found:\n\t{}".format(
                "\n\t".join(sheet_names)
            )
        )
    elif len(candidates) > 1:
        raise ValueError(
            "Found multiple sheet names like 'qualitative changes' for change report file:\n\t{}".format(
                "\n\t".join(sheet_names)
            )
        )

    data = [
        pair
        for row in pd.read_excel(io=excel_filepath, sheet_name=candidates[0]).to_dict(
            orient="records"
        )
        for pair in source_target_pair_as_bw_dict(row, source_version, target_version)
    ]

    source_db_name, target_db_name, source_lookup, target_lookup = get_brightway_databases(
        source_version=source_version, target_version=target_version, system_model=system_model
    )

    if not description:
        description = f"Data migration file from {source_db_name} to {target_db_name} generated with `ecoinvent_migrate` version {__version__}"

    data = resolve_glo_row_rer_roe(
        data=data,
        source_db_name=source_db_name,
        target_db_name=target_db_name,
        source_lookup=source_lookup,
        target_lookup=target_lookup,
    )
    data = split_replace_disaggregate(data=data, target_lookup=target_lookup)

    try:
        for key, value in TECHNOSPHERE_PATCHES[(source_version, target_version)].items():
            data[key].extend(value)
    except KeyError:
        pass

    if not data["replace"] and not data["disaggregate"]:
        logger.info(
            "It seems like there are no technosphere changes for this release. Doing nothing."
        )
        return
    if not data["replace"]:
        del data["replace"]
    if not data["disaggregate"]:
        del data["disaggregate"]

    dp = Datapackage(
        name=f"{source_db_name}-{target_db_name}",
        description=description,
        contributors=[
            {"title": "ecoinvent association", "path": "https://ecoinvent.org/", "roles": ["author"]},
            {"title": "Chris Mutel", "path": "https://chris.mutel.org/", "roles": ["wrangler"]},
        ],
        mapping_source=MappingConstants.ECOSPOLD2,
        mapping_target=MappingConstants.ECOSPOLD2,
        homepage="https://github.com/brightway-lca/ecoinvent_migrate",
        version="2.0.0",
        source_id=source_db_name,
        target_id=target_db_name,
        licenses=licenses,
    )
    for key, value in data.items():
        dp.add_data(key, value)

    if write_file:
        filename = f"{source_db_name}-{target_db_name}.json"
        output_directory = setup_output_directory(output_directory)
        fp = output_directory / filename
        logger.info("Writing output file {fp}", fp=str(fp))
        return dp.to_json(fp)
    else:
        return dp


def generate_biosphere_mapping(
    source_version: str,
    target_version: str,
    keep_deletions: bool = False,
    project_name: str = "ecoinvent-migration",
    ecoinvent_username: Optional[str] = None,
    ecoinvent_password: Optional[str] = None,
    write_logs: bool = True,
    write_file: bool = True,
    licenses: Optional[List[dict]] = None,
    output_directory: Optional[Path] = None,
    output_version: str = "3.0.0",
    description: Optional[str] = None,
) -> Optional[Path]:
    """Generate a Randonneur mapping file for biosphere edge attributes from source to target."""
    configure_logs(write_logs=write_logs)

    source_db_name = f"ecoinvent-{source_version}-biosphere"
    target_db_name = f"ecoinvent-{target_version}-biosphere"

    logger.info(
        """The `EE Deletions` format is not consistent across versions.
Please check the outputs carefully before applying them."""
    )

    excel_filepath = get_change_report_context(
        source_version=source_version,
        target_version=target_version,
        project_name=project_name,
        ecoinvent_username=ecoinvent_username,
        ecoinvent_password=ecoinvent_password,
    )

    sheet_names = pd.ExcelFile(excel_filepath).sheet_names
    candidates = [name for name in sheet_names if name.lower() == "ee deletions"]
    if not candidates:
        logger.info(
            "It seems like there are no biosphere changes; no sheet name like `EE Deletions` found. Sheet names found:\n\t{sn}. Looking at actual data to see if there are changes not included in the change report.",
            sn="\n\t".join(sheet_names),
        )
        missing_sheet = True
    elif len(candidates) > 1:
        raise ValueError(
            "Found multiple sheet names like 'EE Deletions' for change report file:\n\t{}".format(
                "\n\t".join(sheet_names)
            )
        )
    else:
        missing_sheet = False

    if not description:
        description = f"Data migration file from {source_db_name} to {target_db_name} generated with `ecoinvent_migrate` version {__version__}"

    if not missing_sheet:
        # Try reading the sheet
        df = pd.read_excel(io=excel_filepath, sheet_name=candidates[0])

        # Handle the multi-index case
        if df.columns[0].startswith("**"):
            logger.debug("Detected multi-index format, adjusting reading parameters")
            df = pd.read_excel(io=excel_filepath, sheet_name=candidates[0], skiprows=1)

        # Handle the new format case
        if "deleted exchanges" in df.columns:
            logger.debug("Detected new exchange format, adjusting data structure")
            # Get the actual column headers from the first row
            new_headers = {col: val for col, val in df.iloc[0].items() if isinstance(val, str)}
            df = df.rename(columns=new_headers).iloc[1:]

        if df.empty:
            logger.info(
                "EE Deletions sheet is empty in change report for {source_v} to {target_v}. This likely means no biosphere changes.",
                source_v=source_version,
                target_v=target_version,
            )
            data = {"delete": [], "replace": []}
        else:
            data = df.to_dict(orient="records")
            data = source_target_biosphere_pair(
                data=data,
                source_version=source_version,
                target_version=target_version,
                keep_deletions=keep_deletions,
            )
            # Ensure both keys exist
            if "delete" not in data:
                data["delete"] = []
            if "replace" not in data:
                data["replace"] = []

            affected_uuids = {
                o["source"]["uuid"]
                for o in itertools.chain(data.get("replace", []), data.get("delete", []))
            }
            data = supplement_biosphere_changes_with_real_data_comparison(
                data=data,
                affected_uuids=affected_uuids,
                source_version=source_version,
                target_version=target_version,
            )
    else:
        data = supplement_biosphere_changes_with_real_data_comparison(
            data={"delete": [], "replace": []},
            affected_uuids=set(),
            source_version=source_version,
            target_version=target_version,
        )

    # Ensure we have non-empty data before creating Datapackage
    has_data = False
    cleaned_data = {}
    for key in ["delete", "replace"]:
        if data.get(key) and len(data[key]) > 0:
            cleaned_data[key] = data[key]
            has_data = True

    if not has_data:
        logger.info("No valid biosphere changes found after processing. Doing nothing.")
        return None

    dp = Datapackage(
        name=f"{source_db_name}-{target_db_name}",
        description=description,
        contributors=[
            {
                "title": "ecoinvent association",
                "path": "https://ecoinvent.org/",
                "roles": ["author"],
            },
            {"title": "Chris Mutel", "path": "https://chris.mutel.org/", "roles": ["wrangler"]},
        ],
        mapping_source=MappingConstants.ECOSPOLD2_BIO,
        mapping_target=MappingConstants.ECOSPOLD2_BIO,
        homepage="https://github.com/brightway-lca/ecoinvent_migrate",
        version="2.0.0",
        source_id=source_db_name,
        target_id=target_db_name,
        licenses=licenses,
    )

    # Only add non-empty data sections
    for key, value in cleaned_data.items():
        dp.add_data(key, value)

    if write_file:
        filename = f"{source_db_name}-{target_db_name}.json"
        output_directory = setup_output_directory(output_directory)
        fp = output_directory / filename
        logger.info("Writing output file {fp}", fp=str(fp))
        return dp.to_json(fp)
    else:
        return dp


def supplement_biosphere_changes_with_real_data_comparison(
    data: dict, affected_uuids: set, source_version: str, target_version: str
) -> dict:
    cs = CachedStorage()

    def format(ecospold: dict) -> dict:
        return {
            obj["@id"]: {
                "name": obj["name"]["#text"].strip(),
                "formula": obj.get("@formula").strip() if obj.get("@formula") else None,
                "unit": obj["unitName"]["#text"].strip(),
            }
            for obj in ecospold["validElementaryExchanges"]["elementaryExchange"]
        }

    source_ee = format(
        xmltodict.parse(
            open(
                Path(
                    cs.catalogue[
                        ReleaseType.ecospold.filename(
                            version=source_version, system_model_abbr="cutoff"
                        )
                    ]["path"]
                )
                / "MasterData"
                / "ElementaryExchanges.xml",
                "rb",
            )
        )
    )
    target_ee = format(
        xmltodict.parse(
            open(
                Path(
                    cs.catalogue[
                        ReleaseType.ecospold.filename(
                            version=target_version, system_model_abbr="cutoff"
                        )
                    ]["path"]
                )
                / "MasterData"
                / "ElementaryExchanges.xml",
                "rb",
            )
        )
    )

    # Patch changes which aren't included in the change report
    for key_source, value_source in source_ee.items():
        if key_source not in target_ee and key_source not in affected_uuids:
            if "delete" not in data:
                data["delete"] = []
            data["delete"].append(
                {
                    "source": {"uuid": key_source, "name": value_source["name"]},
                    "comment": "Deleted flow not listed in change report",
                }
            )
            continue
        elif key_source not in target_ee:
            # Included in change report
            continue

        diff = {
            key: value
            for key, value in target_ee[key_source].items()
            if value and value != value_source[key]
        }
        if diff:
            data["replace"].append(
                {
                    "source": {k: v for k, v in value_source.items() if v} | {"uuid": key_source},
                    "target": diff | {"uuid": key_source},
                    "comment": "Flow attribute change not listed in change report",
                }
            )

    return data
