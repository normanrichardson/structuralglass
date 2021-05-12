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
ply1 = fsgc.GlassPly(t1nom,"FT")
ply2 = fsgc.GlassPly(t2nom,"FT")
ply3 = fsgc.GlassPly(t3nom,"FT")

# Interlayer
#interlayer = fsgc.InterLayer(0.89*fsgc.ureg.mm, 0.281*fsgc.ureg.MPa)

# Package specifying the model type
package1 = fsgc.MonolithicMethod([ply1, ply2])
package2 = fsgc.MonolithicMethod([ply3])
buildup = [package1, package2]

# Panel
panel = fsgc.GlassPanel(a , b, buildup, windLoad)

# Results
print("-------------Package values-------------")
print(package1.h_efw)
print(package2.h_efs[ply3])
print("-------------LSF values of panel-------------")
print(panel.LSF[package1])
print(panel.LSF[package2])
print("-------------Stress values of plys-------------")
print(panel.stress[ply1])
print(panel.stress[ply2])
print(panel.stress[ply3])
print("-------------Displacement values of the package-------------")
print(panel.deflection[package1].to(fsgc.ureg.mm))
print(panel.deflection[package2].to(fsgc.ureg.mm))

