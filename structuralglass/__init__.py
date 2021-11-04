import pint

from . import resources

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

# Load the file stream for the units file
unit_file = pkg_resources.open_text(resources, 'unit_def.txt')

# Setup pint for the package
ureg = pint.UnitRegistry()
Q_ = ureg.Quantity
ureg.load_definitions(unit_file)
