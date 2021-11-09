# structuralglass
structuralglass is a python package for facade/enclosure designers and engineers who design structural glass. 
The package provides a collection of utilities that a designer will find useful to answer a variety of design questions.

At present, it focuses on methods in the Engineering Structural Glass Design Guide by NCSEA (National Council of Structural Engineers Associations) and ASTM E1300.

# Installation
> pip install structuralglass

# Documentation
Find the documentation [here](https://structuralglass.readthedocs.io/en/latest/).

# Disclaimer
structuralglass is an open source engineering project. Although efforts have been made to ensure that the relevant engineering theories have been correctly implemented, it remains the user’s responsibility to confirm and accept the output.

# Functionality
## Layers:
Create glass layers for nominal and actual thicknesses. Predefined values for nominal thickness - as defined in ASTM E1300 - are provided. Nominal thickness can be extended to accommodate custom definitions.

Interlayers can be created for a "static" interlayer or from a "dynamic" interlayer. For static interlayers, a shear modulus is required. Functionality for dynamic interlayers, where manufacturing tables for the shear relaxation modulus (where the shear modulus is dependent on temperature and load duration), is provided. Predefined dynamic values for Ionoplast (SG) and PVB are provided - as defined in the NCSEA Design Guide.

## Glass Types:
Standard definitions for annealed, heat-strengthened, and fully tempered are provided - as defined in the NCSEA Design Guide.

In addition, a general definition of a glass type is provided for customization. For this, the base allowable surface stress, the base allowable edge stress, the duration factor, the treatment specific stress reduction factor, and the coefficient of variation can be customized.

## Equivalent thickness models:
Equivalent thickness models are a popular treatment of glass mechanics. So, some effort is made to accommodate common models: monolithic method, non-composite method, and shear transfer coefficient method.

### Monolithic method:
A basic/naive mechanical behavior that assumes the laminate's effective thickness is the sum of the plys minimum thicknesses.
This assumption applies to both stress and deflection effective thickness.
This model's validity decreases with load duration.

### Non-composite method:
A simple mechanical behavior that assumes the laminates effective thickness is for:
* deflection: the square root of the sum of the minimum thicknesses squared
* stress: cubed root of the sum of the minimum thicknesses cubed

This model assumes a non-composite behavior.

### Shear transfer coefficient method:
A mechanical behavior that takes the shear modulus of the laminate into consideration.
This method was originally proposed by Bennison-Wolfel and referenced in ASTM E1300.
It is only valid for a two-glass ply laminate.
Ref literature for limitations.

## Demands:
The only demand method is for the application of face loading on four-side supported glass. This condition is applicable for the design of four-side supported glass under wind load.

# Contributions
1. Fork and clone to a local working directory
2. Setup a virtual environment
> python -m venv .venv

> source env/bin/activate
3. Install in editable mode
> pip install -e .[dev]

4. Testing
> python -m unittest test.unittests