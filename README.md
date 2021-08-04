# structuralglass
This project is a python package for the structural analysis of glass.
At present, it focuses on methods presented in the Engineering Structural Glass Design Guide by NCSEA
(National Council of Structural Engineers Associations) and ASTM E1300.

# Functionality
## Layers:
Create glass layers for nominal and actual thicknesses. Predefined values for nominal thickness - as defined in ASTM E1300 - are provided. Nominal thickness can be extended to accommodate custom definitions.

Interlayers can be created for a "static" interlayer or from a "dynamic" interlayer. For static interlayers, a static shear modulus is provided. Functionality for dynamic interlayers, where manufacturing tables for the shear relaxation modulus (where the shear modulus is dependent on temperature and load duration), is provided. The dynamic interlayer data is interpolated if missing values are needed. Predefined dynamic values for Ionoplast (SG) and PVB are provided - as defined in the NCSEA Design Guide. Custom product data (say Trosifol® UltraClear) can be added via `structuralglass.layers.register_interlayer_product(name, data)` function.

## Glass Types:
Standard definitions for annealed, heat-strengthened, and fully tempered are provided - as defined in the NCSEA Design Guide.

In addition, a general definition of a glass type is provided for customization. For this, the base allowable surface stress, the base allowable edge stress, the duration factor, the treatment specific stress reduction factor, and the coefficient of variation can be customized.

## Equivalent thickness models:
Equivalent thickness models are a popular treatment of glass mechanics. So, some effort is made to accommodate common models: monolithic method, non-composite method, and shear transfer coefficient method

### Monolithic method:
A basic/naive mechanical behavior that assumes the laminate's effective thickness is the sum of the plys minimum thicknesses.
This assumption applies to both stress and deflection effective thickness.
This model's validity decreases with load duration.

### Non-composite method:
A simple mechanical behavior that assumes the laminates effective thickness is:
* for deflection: the square root of the minimum thicknesses squared
* for stress: the cubed root of the minimum thicknesses cubed
This model assumes a non-composite behavior.

### Shear transfer coefficient method:
A mechanical behavior that takes the shear modulus of the laminate into consideration.
This method was originally proposed by Bennison-Wolfel and referenced in ASTM E1300.
It is only valid for a two-glass ply laminate.
Ref literature for limitations.

## Demands:
The only demand method is for the application of face loading on four-side supported glass. This condition is applicable for the design of four-side supported glass under wind load.

# Development/Contributions

## Testing
python -m unittest test.unittests