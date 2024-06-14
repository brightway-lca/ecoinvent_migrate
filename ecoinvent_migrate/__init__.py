"""ecoinvent_migrate."""

__all__ = (
    "__version__",
    "generate_technosphere_mapping",
    "generate_biosphere_mapping",
)

__version__ = "0.2.0"

from .main import generate_biosphere_mapping, generate_technosphere_mapping
