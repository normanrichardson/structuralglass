
# Example from E1300-16 example 13

import FourSidedGlassCalc as fsgc

# Plate dimensions
a = 1000 * fsgc.ureg.mm
t1nom = 10*fsgc.ureg.mm
t2nom = 10*fsgc.ureg.mm

# Interlayer PVB at 30degC for 1 day load duration
G_pvb = 0.44*fsgc.ureg.MPa
t_pvb = 1.52*fsgc.ureg.mm
interlayer = fsgc.InterLayer(t_pvb, G_pvb)

# Plys
ply1 = fsgc.GlassPly.from_nominal_thickness(t1nom,"FT")
ply2 = fsgc.GlassPly.from_nominal_thickness(t2nom,"FT")

# Package specifying the model type
package = fsgc.ShearTransferCoefMethod([ply1,interlayer, ply2],a)

print("-------------Package values-------------")
print("Effective displacement thickness: {:.3f~P} ({:.3f~P})".format(package.h_efw, package.h_efw.to(fsgc.ureg.inch)))
print("Effective stress thickness of the package with reference to ply1: {:.3f~P} ({:.3f~P})".format(package.h_efs[ply1], package.h_efs[ply1].to(fsgc.ureg.inch)))
print("Effective stress thickness of the package with reference to ply2: {:.3f~P} ({:.3f~P})".format(package.h_efs[ply2], package.h_efs[ply2].to(fsgc.ureg.inch)))