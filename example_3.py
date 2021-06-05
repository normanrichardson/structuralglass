
# Example from E1300-16 example 13

from structuralglass import ureg, Q_
import structuralglass.materials as mat
import structuralglass.equiv_thick_models as et

# Plate dimensions
a = 1000 * ureg.mm
t1nom = 10*ureg.mm
t2nom = 10*ureg.mm

# Interlayer PVB at 30degC for 1 day load duration
G_pvb = 0.44*ureg.MPa
t_pvb = 1.52*ureg.mm
interlayer = mat.InterLayer(t_pvb, G_pvb)

# Plys
ply1 = mat.GlassPly.from_nominal_thickness(t1nom,"FT")
ply2 = mat.GlassPly.from_nominal_thickness(t2nom,"FT")

# Package specifying the model type
package = et.ShearTransferCoefMethod([ply1,interlayer, ply2],a)

print("-------------Package values-------------")
print("Effective displacement thickness: {:.3f~P} ({:.3f~P})".format(package.h_efw, package.h_efw.to(ureg.inch)))
print("Effective stress thickness of the package with reference to ply1: {:.3f~P} ({:.3f~P})".format(package.h_efs[ply1], package.h_efs[ply1].to(ureg.inch)))
print("Effective stress thickness of the package with reference to ply2: {:.3f~P} ({:.3f~P})".format(package.h_efs[ply2], package.h_efs[ply2].to(ureg.inch)))