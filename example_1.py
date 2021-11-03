
# Example from NCSEA Engineering Structural Glass Design Guide chapter 8 example 5

from structuralglass import ureg, Q_
import structuralglass.glass_types as gt
import structuralglass.layers as lay
import structuralglass.equiv_thick_models as et
import structuralglass.demands as dem

# Plate dimensions
a = 4000 * ureg.mm
b = 2000 * ureg.mm
t1nom = 6 * ureg.mm
t2nom = 6 * ureg.mm
t3nom = 6 * ureg.mm

# Panel force
windLoad = 1.436 * ureg.kPa

# Allowable stress
ft = gt.GlassType.from_abbr("FT")
# NCSEA uses a coef of variation of 0.2 so overriding the material specific value
ft.coef_variation = 0.2
# The allowable stress is greater than shown in NCSEA as it looks like NCSEA 
# used the HS 10 year load duration factor. Here the FT 3s load duration factor 
# is used.
allow_stress = ft.prob_breakage_factor(1/1000) \
    * ft.load_duration_factor(3 *ureg.sec) \
    * ft.surf_treat_factor("None") * ft.stress_edge

# Allowable deflection
defl_max = min(a,b)/75

# Plys
ply1 = lay.GlassPly.from_nominal_thickness(t1nom)
ply2 = lay.GlassPly.from_nominal_thickness(t2nom)
ply3 = lay.GlassPly.from_nominal_thickness(t3nom)

# Package specifying the model type
package1 = et.MonolithicMethod([ply1, ply2])
package2 = et.MonolithicMethod([ply3])
buildup = [package1, package2]

# Panel
panel = dem.IGUWindDemands(buildup, windLoad, dim_x=a , dim_y=b)
panel.solve()

# Results
print("-------------Package values-------------")
print("Effective displacement thickness of package 1: {:.2f~P}".format(package1.h_efw))
print("Effective stress thickness of package 2 with reference to the 1st ply: {:.2f~P}".format(package2.h_efs[ply3]))
print("-------------LSF values of panel-------------")
print("Load share factor of package 1: {:.3f~P}".format(panel.LSF[package1]))
print("Load share factor of package 2: {:.3f~P}".format(panel.LSF[package2]))
print("-------------Stress and utilizations values of plys-------------")
print("Allowable stress: {:.2f~P}".format(allow_stress))
print("Stress in ply 1: {:.2f~P} => {:.2%~P}".format(panel.stress[ply1], (panel.stress[ply1]/allow_stress).to_reduced_units()))
print("Stress in ply 2: {:.2f~P} => {:.2%~P}".format(panel.stress[ply2], (panel.stress[ply2]/allow_stress).to_reduced_units()))
print("Stress in ply 3: {:.2f~P} => {:.2%~P}".format(panel.stress[ply3], (panel.stress[ply3]/allow_stress).to_reduced_units()))
print("-------------Displacement values of the package-------------")
print("Allowable deflection: {:.2f~P}".format(defl_max))
print("Deflection of package 1: {:.2f~P} => {:.2%~P}".format(panel.deflection[package1], abs(panel.deflection[package1]/defl_max)))
print("Deflection of package 2: {:.2f~P} => {:.2%~P}".format(panel.deflection[package2].to(ureg.mm), abs(panel.deflection[package1]/defl_max)))

