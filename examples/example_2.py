# Example from NCSEA Engineering Structural Glass Design Guide chapter 8
# example 3

import structuralglass.equiv_thick_models as et
import structuralglass.layers as lay
from structuralglass import Q_

# Plate dimensions
a = Q_(1, "m")
t1nom = Q_(12, "mm")
t2nom = Q_(12, "mm")

# Interlayer PVB at 30degC for 1 day load duration
G_pvb = Q_(0.281, "MPa")
t_pvb = Q_(0.89, "mm")
interlayer = lay.Interlayer.from_static(t_pvb, G_pvb)

# Plys
ply1 = lay.GlassPly.from_nominal_thickness(t1nom)
ply2 = lay.GlassPly.from_nominal_thickness(t2nom)

# Package specifying the model type
package = et.ShearTransferCoefMethod([ply1, interlayer, ply2], a)

# Results
print("-------------Package values-------------")
print("Effective displacement thickness:", end=" ")
print(f"{package.h_efw:.3f~P} ({ package.h_efw.to('in') :.3f~P})")
print("Eff. package thickness for stress with reference to ply1:", end=" ")
print(f"{package.h_efs[ply1]:.3f~P} ({package.h_efs[ply1].to('in'):.3f~P})")
print("Eff. package thickness for stress with reference to ply2:", end=" ")
print(f"{package.h_efs[ply2]:.3f~P} ({package.h_efs[ply2].to('in'):.3f~P})")
