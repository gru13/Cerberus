"""Intent: Expose the installed version of the cerberus package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cerberus")
except PackageNotFoundError:  # pragma: no cover - only when the package is not installed
    __version__ = "0.0.0"
