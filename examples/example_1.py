# Example from NCSEA Engineering Structural Glass Design Guide chapter 8
# example 5

import structuralglass.demands as dem
import structuralglass.equiv_thick_models as et
import structuralglass.glass_types as gt
import structuralglass.layers as lay
from structuralglass import Q_

# Plate dimensions
a = Q_(4, "m")
b = Q_(2, "m")
t1nom = Q_(6, "mm")
t2nom = Q_(6, "mm")
t3nom = Q_(6, "mm")

# Panel force
windLoad = Q_(1.436, "kPa")

# Allowable stress
ft = gt.GlassType.from_abbr("FT")
# NCSEA uses a coef of variation of 0.2 so
# overriding the material specific value
ft.coef_variation = 0.2
# The allowable stress is greater than shown in NCSEA as it looks like NCSEA
# used the HS 10 year load duration factor. Here the FT 3s load duration factor
# is used.
allow_stress = ft.prob_breakage_factor(1/1000) \
    * ft.load_duration_factor(Q_(3, "sec")) \
    * ft.surf_treat_factor("None") * ft.stress_edge

# Allowable deflection
defl_max = min(a, b)/75

# Plys
ply1 = lay.GlassPly.from_nominal_thickness(t1nom)
ply2 = lay.GlassPly.from_nominal_thickness(t2nom)
ply3 = lay.GlassPly.from_nominal_thickness(t3nom)

# Package specifying the model type
package1 = et.MonolithicMethod([ply1, ply2])
package2 = et.MonolithicMethod([ply3])
buildup = [package1, package2]

# Panel
panel = dem.IGUWindDemands(buildup, windLoad, dim_x=a, dim_y=b)
panel.solve()

# Results
print("-------------Ply values-------------")
print("Ply 1 min allowable thickness:", end=" ")
print(f"{ ply1.t_min.to('in') :.2f~P}", end="\n\n")

print("-------------Package values-------------")
print("Effective displacement thickness of package 1:", end=" ")
print(f"{ package1.h_efw.to('in') :.2f~P}")
print(
    "Effective stress thickness of package 2 with reference to the 1st ply:",
    end=" "
)
print(f"{ package2.h_efs[ply3].to('in') :.2f~P}", end="\n\n")

print("-------------LSF values of panel-------------")
print(f"Load share factor of package 1: { panel.LSF[package1] :.3f~P}")
print(
    f"Load share factor of package 2: { panel.LSF[package2] :.3f~P}",
    end="\n\n"
)

print("-------------Stress and utilizations values of plys-------------")
print(f"Allowable stress: { allow_stress.to('ksi') :.2f~P}")
print(f"Stress in ply 1: { panel.stress[ply1].to('ksi') :.2f~P} =>", end=" ")
print(f"{ (panel.stress[ply1]/allow_stress).to_reduced_units() :.2%~P}")
print(f"Stress in ply 2: { panel.stress[ply2].to('ksi') :.2f~P} =>", end=" ")
print(f"{ (panel.stress[ply2]/allow_stress).to_reduced_units() :.2%~P}")
print(f"Stress in ply 3: { panel.stress[ply3].to('ksi') :.2f~P} =>", end=" ")
print(
    f"{ (panel.stress[ply3]/allow_stress).to_reduced_units() :.2%~P}",
    end="\n\n"
)

print("-------------Displacement values of the package-------------")
print(f"Allowable deflection: { defl_max.to('in') :.2f~P}")
print("Deflection of package 1:", end=" ")
print(f"{ panel.deflection[package1].to('in') :.2f~P} =>", end=" ")
print(f"{ abs(panel.deflection[package1]/defl_max).to_reduced_units() :.2%~P}")
print("Deflection of package 2:", end=" ")
print(f"{ panel.deflection[package2].to('in') :.2f~P} =>", end=" ")
print(f"{ abs(panel.deflection[package1]/defl_max).to_reduced_units() :.2%~P}")
