"""ecoinvent_migrate."""

__all__ = (
    "__version__",
    "generate_technosphere_mapping",
    "generate_biosphere_mapping",
)

__version__ = "0.6"

from ecoinvent_migrate.main import generate_biosphere_mapping, generate_technosphere_mapping
