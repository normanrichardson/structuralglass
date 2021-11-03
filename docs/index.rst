structuralglass
===============

structuralglass is a python package for facade/enclosure designers and engineers that are exploring the topic of structural glass. The aim is not to create a single tool that solves a problem, but to provide a collection of tools that a designer will find useful to answer a variety of design topics. 

This project is aimed at the practitioners and is an attempt to extend the open-source structural engineering ecosystem of practitioners. 
It can be used to:

 * ask questions about common laminate properties and compare performance.
 * build a personal library of manufacturers' data.
 * perform stress analysis of typical glass types for a variety of environmental conditions.
 * refine and tweak the stress analysis for a particular manufactured glass.
 * perform rudimentary E1300 calculations of 4 side supported IGUs/or laminates.
 * used alongside other industry analysis tools such as Mepla and strand7, to perform capacity calculations.
 * and so on.

At present, it focuses on methods presented in the Engineering Structural Glass Design Guide by NCSEA (National Council of Structural Engineers Associations) and ASTM E1300.

This package is by no means complete and could be extended in a variety of ways. Contributions and issues are most welcome and can be made on `GitHub <https://github.com/normanrichardson/StructGlassCalcs>`_.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   rst/installation.rst
   rst/contributing.rst
   rst/layers.rst
   rst/glass_types.rst
   rst/equiv_thick_models.rst
   rst/demands.rst

Example use
-----------

.. code-block:: python

   from structuralglass import Q_
   import structuralglass.glass_types as gt
   import structuralglass.layers as lay
   import structuralglass.equiv_thick_models as et
   import structuralglass.demands as dem

   # Glass ply thickness
   t1nom = Q_(0.25,"in")
   t2nom = Q_(0.25,"in")
   t3nom = Q_(0.25,"in")

   # Plys
   ply1 = lay.GlassPly.from_nominal_thickness(t1nom)
   ply2 = lay.GlassPly.from_nominal_thickness(t2nom)
   ply3 = lay.GlassPly.from_nominal_thickness(t3nom)

   # Interlayer details
   t_pvb = Q_(1.52, "mm")
   product_name = "PVB NCSEA"
   interlayer = lay.Interlayer.from_product_table(t_pvb, product_name)
   interlayer.duration = Q_(3,"sec")
   interlayer.temperature = Q_(30,"degC")

   # Panel force
   wind_load = Q_(30,"psf")

   # Allowable stress
   ft = gt.FullyTempered()
   allow_stress = ft.prob_breakage_factor(1/1000) \
      * ft.load_duration_factor(Q_(3,"sec")) \
      * ft.surf_treat_factor("None") \
      * ft.stress_edge

   # Plate dimensions
   a = Q_(13,"ft")
   b = Q_(5,"ft")

   # Allowable deflection
   defl_max = min(a,b)/75

   # Package specifying the model type
   package1 = et.ShearTransferCoefMethod([ply1, interlayer, ply2], min(a,b))
   package2 = et.MonolithicMethod([ply3])
   buildup = [package1, package2]

   # Panel
   panel = dem.IGUWindDemands(buildup, wind_load, dim_x=a , dim_y=b)
   panel.solve()

   # Results
   print("-------------Ply values-------------")
   print("Ply 1 min allowable thickness:", end=" ")
   print(f"{ ply1.t_min.to('in') :.2f~P}", end="\n\n")

   print("-------------Interlayer values-------------")
   print("Interlayer shear modulus:", end=" ")
   print(f"{ interlayer.G.to('MPa') :.2f~P}", end="\n\n")

   print("-------------Package values-------------")
   print("Effective displacement thickness of package 1:", end=" ")
   print(f"{ package1.h_efw.to('in') :.2f~P}")
   print(f"Effective stress thickness of package 2 with reference to the 1st ply:", end=" ")
   print(f"{ package2.h_efs[ply3].to('in') :.2f~P}", end="\n\n")

   print("-------------LSF values of panel-------------")
   print(f"Load share factor of package 1: { panel.LSF[package1] :.3f~P}")
   print(f"Load share factor of package 2: { panel.LSF[package2] :.3f~P}", end="\n\n")

   print("-------------Stress and utilizations values of plys-------------")
   print(f"Allowable stress: { allow_stress.to('ksi') :.2f~P}")
   print(f"Stress in ply 1: { panel.stress[ply1].to('ksi') :.2f~P} =>", end=" ")
   print(f"{ (panel.stress[ply1]/allow_stress).to_reduced_units() :.2%~P}")
   print(f"Stress in ply 2: { panel.stress[ply2].to('ksi') :.2f~P} =>", end=" ")
   print(f"{ (panel.stress[ply2]/allow_stress).to_reduced_units() :.2%~P}")
   print(f"Stress in ply 3: { panel.stress[ply3].to('ksi') :.2f~P} =>", end=" ")
   print(f"{ (panel.stress[ply3]/allow_stress).to_reduced_units() :.2%~P}", end="\n\n")

   print("-------------Displacement values of the package-------------")
   print(f"Allowable deflection: { defl_max.to('in') :.2f~P}")
   print(f"Deflection of package 1: { panel.deflection[package1].to('in') :.2f~P} =>", end=" ")
   print(f"{ abs(panel.deflection[package1]/defl_max).to_reduced_units() :.2%~P}")
   print(f"Deflection of package 2: { panel.deflection[package2].to('in') :.2f~P} =>", end=" ")
   print(f"{ abs(panel.deflection[package1]/defl_max).to_reduced_units() :.2%~P}")

.. code-block:: text

   -------------Ply values-------------
   Ply 1 min allowable thickness: 0.22 in

   -------------Interlayer values-------------
   Interlayer shear modulus: 0.97 MPa

   -------------Package values-------------
   Effective displacement thickness of package 1: 0.40 in
   Effective stress thickness of package 2 with reference to the 1st ply: 0.22 in

   -------------LSF values of panel-------------
   Load share factor of package 1: 0.862
   Load share factor of package 2: 0.138

   -------------Stress and utilizations values of plys-------------
   Allowable stress: 9.64 ksi
   Stress in ply 1: 2.26 ksi => 23.43%
   Stress in ply 2: 2.26 ksi => 23.43%
   Stress in ply 3: 1.45 ksi => 15.06%

   -------------Displacement values of the package-------------
   Allowable deflection: 0.80 in
   Deflection of package 1: -0.43 in => 53.14%
   Deflection of package 2: -0.43 in => 53.14%
