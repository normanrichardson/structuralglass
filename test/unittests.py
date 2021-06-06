import unittest
import pint
from structuralglass import ureg, Q_
import structuralglass.glass_types as gt
import structuralglass.layers as lay
import structuralglass.equiv_thick_models as et
import structuralglass.demands as dem

class TestGlassPly(unittest.TestCase):
    def test_from_nominal_thickness_metric(self):
        tnom = 8*ureg.mm
        tmin = lay.t_min_lookup_metric[tnom.to(ureg.mm).magnitude]*ureg.mm
        glassType = "FT"
        ply = lay.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertIsInstance(ply,lay.GlassPly)
        self.assertEqual(ply.t_nom, tnom)
        self.assertEqual(ply.t_min, tmin)
        self.assertEqual(ply.E, 71.7 * ureg.GPa)
        self.assertEqual(ply.glassType, glassType)

    def test_from_nominal_thickness_imperial(self):
        tnom = 3/8*ureg.inch
        tmin = lay.t_min_lookup_imperial[tnom.to(ureg.inch).magnitude]*ureg.mm
        glassType = "FT"
        ply = lay.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertIsInstance(ply,lay.GlassPly)
        self.assertEqual(ply.t_nom, tnom)
        self.assertEqual(ply.t_min, tmin)
        self.assertEqual(ply.E, 71.7 * ureg.GPa)
        self.assertEqual(ply.glassType, glassType)

    def test_from_actual_thickness(self):
        tmin = 8*ureg.mm
        glassType = "AN"
        ply = lay.GlassPly.from_actual_thickness(tmin,glassType)
        self.assertIsInstance(ply,lay.GlassPly)
        self.assertIsNone(ply.t_nom)
        self.assertEqual(ply.t_min, tmin)
        self.assertEqual(ply.E, 71.7 * ureg.GPa)
        self.assertEqual(ply.glassType, glassType)

    def test_invalid_lookup_from_nominal_thickness(self):
        tnom = 8.5*ureg.mm
        glassType = "FT"
        with self.assertRaises(ValueError) as cm:
            ply = lay.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertEqual(str(cm.exception), "Could not find the nominal tickness of {0} in the nominal thickness lookup.".format(tnom))
        
    def test_invalid_no_unit_from_nominal_thickness(self):
        tnom = 8
        glassType = "FT"
        with self.assertRaises(pint.DimensionalityError) as cm:
            ply = lay.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertEqual(str(cm.exception), "Cannot convert from '8' (dimensionless) to 'a quantity of' ([length])")

    def test_invalid_unit_from_nominal_thickness(self):
        tnom = 8*ureg.mm**2
        glassType = "FT"
        with self.assertRaises(pint.DimensionalityError) as cm:
            ply = lay.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertEqual(str(cm.exception), "Cannot convert from '8 millimeter ** 2' ([length] ** 2) to 'a quantity of' ([length])")

class TestInterLayer(unittest.TestCase):
    def test_constructor(self):
        G_pvb = 0.281*ureg.MPa
        t_pvb = 0.89*ureg.mm
        interlayer = lay.InterLayer(t_pvb, G_pvb)
        self.assertEqual(interlayer.t, t_pvb)
        self.assertEqual(interlayer.G, G_pvb)

class TestMonolithicMethod(unittest.TestCase):
    def setUp(self):
        self.t1nom = 8*ureg.mm
        self.t2nom = 10*ureg.mm
        glassType = "FT"
        self.ply1 = lay.GlassPly.from_nominal_thickness(self.t1nom,glassType)
        self.ply2 = lay.GlassPly.from_nominal_thickness(self.t2nom,glassType)
        package = [self.ply1,self.ply2]
        self.buildup = [et.MonolithicMethod(package)]
    
    def test_h_efw(self):
        t_act = (lay.t_min_lookup_metric[self.t1nom.to(ureg.mm).magnitude] + \
        lay.t_min_lookup_metric[self.t2nom.to(ureg.mm).magnitude])*ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efw, t_act)

    def test_h_efs(self):
        t_act = (lay.t_min_lookup_metric[self.t1nom.to(ureg.mm).magnitude] + \
        lay.t_min_lookup_metric[self.t2nom.to(ureg.mm).magnitude])*ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efs[self.ply1], t_act)

class TestNonCompositeMethod(unittest.TestCase):
    def setUp(self):
        self.t1nom = 8*ureg.mm
        self.t2nom = 6*ureg.mm
        self.t3nom = 8*ureg.mm
        glassType = "AN"
        self.ply1 = lay.GlassPly.from_nominal_thickness(self.t1nom,glassType)
        self.ply2 = lay.GlassPly.from_nominal_thickness(self.t2nom,glassType)
        self.ply3 = lay.GlassPly.from_nominal_thickness(self.t2nom,glassType)
        package = [self.ply1,self.ply2,self.ply3]
        self.buildup = [et.NonCompositeMethod(package)]
    
    def test_h_efw(self):
        t_act = 9.09479121*ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efw, t_act)
        
    def test_h_efs(self):
        t_act = 10.8112719*ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efs[self.ply3], t_act)

class TestShearTransferCoefMethod(unittest.TestCase):
    def setUp(self):
        self.a = 1000 * ureg.mm
        self.t1nom = 8*ureg.mm
        self.t2nom = 6*ureg.mm
        G_pvb = 0.44*ureg.MPa
        t_pvb = 1.52*ureg.mm
        glassType = "FT"
        self.ply1 = lay.GlassPly.from_nominal_thickness(self.t1nom,glassType)
        self.ply2 = lay.GlassPly.from_nominal_thickness(self.t2nom,glassType)
        self.interlayer = lay.InterLayer(t_pvb, G_pvb)
        package = [self.ply1, self.interlayer, self.ply2]
        self.buildup = [et.ShearTransferCoefMethod(package, self.a)]

    def test_h_efw(self):
        t_act = 9.53304352*ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efw, t_act)
    
    def test_h_efs(self):
        t_act1 = 10.2650672*ureg.mm
        t_act2 = 11.4310515*ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efs[self.ply1], t_act1)
        self.assertAlmostEqual(self.buildup[0].h_efs[self.ply2], t_act2)
    
    def test_invalid_packages(self):
        # invalid package
        ply3 = lay.GlassPly.from_nominal_thickness(self.t1nom, "FT")
        pac_invalid_1 = [self.ply1, self.ply2]
        pac_invalid_2 = [self.ply1, self.ply2, self.interlayer]
        pac_invalid_3 = [self.ply1, self.interlayer, self.ply2, self.interlayer, ply3]

        with self.assertRaises(AssertionError) as cm:
            buildup = [et.ShearTransferCoefMethod(pac_invalid_1,self.a)]
        self.assertEqual(str(cm.exception), "Method is only valid for 2 ply glass laminates")

        with self.assertRaises(AssertionError) as cm:
            buildup = [et.ShearTransferCoefMethod(pac_invalid_2,self.a)]
        self.assertEqual(str(cm.exception), "Method is only valid for 2 ply glass laminates")

        with self.assertRaises(AssertionError) as cm:
            buildup = [et.ShearTransferCoefMethod(pac_invalid_3,self.a)]
        self.assertEqual(str(cm.exception), "Method is only valid for 2 ply glass laminates")


class TestAnnealedGlassType(unittest.TestCase):
    def setUp(self) -> None:
        self.an = gt.Annealed()
    def test_prob_breakage_factor(self):
        self.assertAlmostEqual(self.an.prob_breakage_factor(1/1000), 0.681114447,4)
        self.assertAlmostEqual(self.an.prob_breakage_factor(5/1000), 0.9218781646,4)
        self.assertAlmostEqual(self.an.prob_breakage_factor(8/1000), 1,4)
        self.assertAlmostEqual(self.an.prob_breakage_factor(10/1000), 1.038646695,4)
    def test_load_duration_factor(self):
        self.assertAlmostEqual(self.an.load_duration_factor(10*ureg.year), 0.315,3)
        self.assertAlmostEqual(self.an.load_duration_factor(12*ureg.hour), 0.550,3)
    def test_surf_factors(self):
        self.assertAlmostEqual(self.an.surf_factors["None"], 1)

class TestHeatStrengthenedGlassType(unittest.TestCase):
    def setUp(self) -> None:
        self.hs = gt.HeatStrengthened()
    def test_prob_breakage_factor(self):
        self.assertAlmostEqual(self.hs.prob_breakage_factor(1/1000), 0.8399834341,4)
        self.assertAlmostEqual(self.hs.prob_breakage_factor(3/1000), 0.9204133016,4)
        self.assertAlmostEqual(self.hs.prob_breakage_factor(8/1000), 1,4)
        self.assertAlmostEqual(self.hs.prob_breakage_factor(9/1000), 1.010169699,4)
    def test_load_duration_factor(self):
        self.assertAlmostEqual(self.hs.load_duration_factor(10*ureg.year), 0.558,3)
        self.assertAlmostEqual(self.hs.load_duration_factor(12*ureg.hour), 0.739,3)
    def test_surf_factors(self):
        self.assertAlmostEqual(self.hs.surf_factors["Fritted"], 1)

class TestFullyTemperedGlassType(unittest.TestCase):
    def setUp(self) -> None:
        self.ft = gt.FullyTempered()
    def test_prob_breakage_factor(self):
        self.assertAlmostEqual(self.ft.prob_breakage_factor(1/1000), 0.9102486076,4)
        self.assertAlmostEqual(self.ft.prob_breakage_factor(4/1000), 0.9679689847,4)
        self.assertAlmostEqual(self.ft.prob_breakage_factor(8/1000), 1,4)
        self.assertAlmostEqual(self.ft.prob_breakage_factor(10/1000), 1.01087724,4)
    def test_prob_breakage_factor_in_NCSEA(self):
        # NCSEA uses a coef of var of 0.2 irrespective of the glass type
        self.ft.coef_variation = 0.2
        self.assertAlmostEqual(self.ft.prob_breakage_factor(1/1000), 0.7370555907,4)
        self.assertAlmostEqual(self.ft.prob_breakage_factor(4/1000), 0.9061588218,4)
        self.assertAlmostEqual(self.ft.prob_breakage_factor(8/1000), 1,4)
        self.assertAlmostEqual(self.ft.prob_breakage_factor(10/1000), 1.031867021,4)
    def test_load_duration_factor(self):
        self.assertAlmostEqual(self.ft.load_duration_factor(10*ureg.year), 0.678,3)
        self.assertAlmostEqual(self.ft.load_duration_factor(12*ureg.hour), 0.817,3)
    def test_surf_factors(self):
        self.assertAlmostEqual(self.ft.surf_factors["Acid etching"], 0.5)
        

if __name__ == '__main__':
    unittest.main()