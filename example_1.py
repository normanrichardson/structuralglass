
# Example from NCSEA Engineering Structural Glass Design Guide chapter 8 example 5

import FourSidedGlassCalc as fsgc

# Plate dimensions
a = 4000 * fsgc.ureg.mm
b = 2000 * fsgc.ureg.mm
t1nom = 6*fsgc.ureg.mm
t2nom = 6*fsgc.ureg.mm
t3nom = 6*fsgc.ureg.mm

# Panel force
windLoad = 1.436*fsgc.ureg.kPa

# Plys
ply1 = fsgc.GlassPly.from_nominal_thickness(t1nom,"FT")
ply2 = fsgc.GlassPly.from_nominal_thickness(t2nom,"FT")
ply3 = fsgc.GlassPly.from_nominal_thickness(t3nom,"FT")

# Package specifying the model type
package1 = fsgc.MonolithicMethod([ply1, ply2])
package2 = fsgc.MonolithicMethod([ply3])
buildup = [package1, package2]

# Panel
panel = fsgc.GlassPanel(a , b, buildup, windLoad)

# Results
print("-------------Package values-------------")
print("Effective displacement thickness of package 1: {}".format(package1.h_efw))
print("Effective stress thickness of package 2 with reference to the 1st ply: {}".format(package2.h_efs[ply3]))
print("-------------LSF values of panel-------------")
print("Load share factor of package 1: {}".format(panel.LSF[package1]))
print("Load share factor of package 2: {}".format(panel.LSF[package2]))
print("-------------Stress values of plys-------------")
print("Stress in ply 1: {}".format(panel.stress[ply1]))
print("Stress in ply 2: {}".format(panel.stress[ply2]))
print("Stress in ply 3: {}".format(panel.stress[ply3]))
print("-------------Displacement values of the package-------------")
print("Deflection of package 1: {}".format(panel.deflection[package1].to(fsgc.ureg.mm)))
print("Deflection of package 2: {}".format(panel.deflection[package2].to(fsgc.ureg.mm)))

