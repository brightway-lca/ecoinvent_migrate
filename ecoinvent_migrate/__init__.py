"""ecoinvent_migrate."""

__all__ = (
    "__version__",
    "generate_technosphere_mapping",
    "generate_biosphere_mapping",
)

__version__ = "0.0.1"

from .main import generate_technosphere_mapping, generate_biosphere_mapping
