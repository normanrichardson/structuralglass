import pint
# Create the default pint unit registry
ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

# Add psf
ureg.define('pound_force_per_square_foot = pound * gravity / foot ** 2 = psf')