import json
from dataclasses import asdict, dataclass
from pathlib import Path

from ecoinvent_interface import EcoinventRelease, ReleaseType
from loguru import logger
from lxml import objectify
from tqdm import tqdm

from ecoinvent_migrate.errors import VersionJump
from ecoinvent_migrate.utils import cache_dir
from ecoinvent_migrate.wrangling import tuple_key_for_data


@dataclass
class SOUPInfo:
    """
    Single-output unit process

    Has unique combination of activity name, product name, geography, and unit.
    """

    activity_name: str
    product_name: str
    unit: str
    geography: str
    production_volume: float
    filename: str

    def as_tuple(self) -> tuple[str]:
        return tuple_key_for_data(asdict(self))


def soupinfo_for_file(fp: Path) -> SOUPInfo:
    root = objectify.parse(open(fp)).getroot()
    if hasattr(root, "activityDataset"):
        stem = root.activityDataset
    else:
        stem = root.childActivityDataset

    for prod_exc in stem.flowData.iterchildren():
        if hasattr(prod_exc, "outputGroup") and prod_exc.outputGroup.text == "0":
            break
    else:
        raise ValueError("Can't find production exchange")

    return SOUPInfo(
        activity_name=stem.activityDescription.activity.activityName.text.strip(),
        product_name=prod_exc.name.text.strip(),
        unit=prod_exc.unitName.text.strip(),
        geography=stem.activityDescription.geography.shortname.text.strip(),
        production_volume=float(prod_exc.get("productionVolumeAmount") or 0),
        filename=fp.name,
    )


def load_release_data(version: str, system_model: str, release: EcoinventRelease) -> None:
    cache_filepath = cache_dir() / f"ecoinvent-{version}-{system_model}.json"
    if cache_filepath.is_file():
        return {tuple_key_for_data(obj): obj for obj in json.load(open(cache_filepath))}
    else:
        logger.info(
            "Downloading ecoinvent version {version} {system_model}",
            version=version,
            system_model=system_model,
        )
        release.get_release(version, system_model, ReleaseType.ecospold)

        dirpath = release.get_release(version, system_model, ReleaseType.ecospold) / "datasets"
        assert dirpath.is_dir(), f"Release cache at {dirpath.parent} missing `datasets` directory"

        data = [
            asdict(soupinfo_for_file(fp))
            for fp in tqdm(
                filter(lambda x: x.suffix.lower() in {".xml", ".spold"}, dirpath.iterdir())
            )
        ]
        with open(cache_filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {tuple_key_for_data(obj): obj for obj in data}


def get_change_report(
    source_version: str,
    target_version: str,
    release: EcoinventRelease,
) -> Path:
    """Get the source/target change report filepath, and setup Brightway project with needed data.

    Source and target must be one release apart from each other, i.e. 3.4 to 3.5 or 3.7 to 3.7.1.

    Returns the `Path` of the generated file."""
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
    return excel_filepath


def get_change_report_filepath(version: str, release: EcoinventRelease) -> Path:
    """Get the filepath to the Excel change report file.

    Download a list of extra files from ecoinvent and do pattern matching."""
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
