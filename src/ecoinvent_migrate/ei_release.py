import warnings
from pathlib import Path

from ecoinvent_interface import EcoinventRelease, Settings


def get_ei_release(
    ecoinvent_username: str | None = None,
    ecoinvent_password: str | None = None,
) -> Path:
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
    return EcoinventRelease(settings)
