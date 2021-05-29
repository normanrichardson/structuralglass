import FourSidedGlassCalc as fsgc
import unittest

class TestGlassPly(unittest.TestCase):
    def test_from_nominal_thickness(self):
        tnom = 8*fsgc.ureg.mm
        tmin = fsgc.lookupT[tnom.to(fsgc.ureg.mm).magnitude]*fsgc.ureg.mm
        glassType = "FT"
        ply = fsgc.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertIsInstance(ply,fsgc.GlassPly)
        self.assertEqual(ply.t_nom, tnom)
        self.assertEqual(ply.t_min, tmin)
        self.assertEqual(ply.E, 71.7 * fsgc.ureg.GPa)
        self.assertEqual(ply.glassType, glassType)

    def test_from_actual_thickness(self):
        tmin = 8*fsgc.ureg.mm
        glassType = "AN"
        ply = fsgc.GlassPly.from_actual_thickness(tmin,glassType)
        self.assertIsInstance(ply,fsgc.GlassPly)
        self.assertIsNone(ply.t_nom)
        self.assertEqual(ply.t_min, tmin)
        self.assertEqual(ply.E, 71.7 * fsgc.ureg.GPa)
        self.assertEqual(ply.glassType, glassType)

    def test_invalid_lookup_from_nominal_thickness(self):
        tnom = 8.5*fsgc.ureg.mm
        glassType = "FT"
        with self.assertRaises(ValueError) as cm:
            ply = fsgc.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertEqual(str(cm.exception), "Could not find the nominal tickness of {0} in the nominal thickness lookup.".format(tnom))
        
    def test_invalid_no_unit_from_nominal_thickness(self):
        tnom = 8
        glassType = "FT"
        with self.assertRaises(ValueError) as cm:
            ply = fsgc.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertEqual(str(cm.exception), "The nominal thickness must be defined in pint length units. <class 'int'> provided.")

    def test_invalid_unit_from_nominal_thickness(self):
        tnom = 8*fsgc.ureg.mm**2
        glassType = "FT"
        with self.assertRaises(ValueError) as cm:
            ply = fsgc.GlassPly.from_nominal_thickness(tnom,glassType)
        self.assertEqual(str(cm.exception), "The nominal thickness must be defined in pint length units. [length] ** 2 provided.")

class TestInterLayer(unittest.TestCase):
    def test_constructor(self):
        G_pvb = 0.281*fsgc.ureg.MPa
        t_pvb = 0.89*fsgc.ureg.mm
        interlayer = fsgc.InterLayer(t_pvb, G_pvb)
        self.assertEqual(interlayer.t, t_pvb)
        self.assertEqual(interlayer.G, G_pvb)

class TestMonolithicMethod(unittest.TestCase):
    def setUp(self):
        self.t1nom = 8*fsgc.ureg.mm
        self.t2nom = 10*fsgc.ureg.mm
        glassType = "FT"
        self.ply1 = fsgc.GlassPly.from_nominal_thickness(self.t1nom,glassType)
        self.ply2 = fsgc.GlassPly.from_nominal_thickness(self.t2nom,glassType)
        package = [self.ply1,self.ply2]
        self.buildup = [fsgc.MonolithicMethod(package)]
    
    def test_h_efw(self):
        t_act = (fsgc.lookupT[self.t1nom.to(fsgc.ureg.mm).magnitude] + \
        fsgc.lookupT[self.t2nom.to(fsgc.ureg.mm).magnitude])*fsgc.ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efw, t_act)

    def test_h_efs(self):
        t_act = (fsgc.lookupT[self.t1nom.to(fsgc.ureg.mm).magnitude] + \
        fsgc.lookupT[self.t2nom.to(fsgc.ureg.mm).magnitude])*fsgc.ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efs[self.ply1], t_act)

class TestNonCompositeMethod(unittest.TestCase):
    def setUp(self):
        self.t1nom = 8*fsgc.ureg.mm
        self.t2nom = 6*fsgc.ureg.mm
        self.t3nom = 8*fsgc.ureg.mm
        glassType = "AN"
        self.ply1 = fsgc.GlassPly.from_nominal_thickness(self.t1nom,glassType)
        self.ply2 = fsgc.GlassPly.from_nominal_thickness(self.t2nom,glassType)
        self.ply3 = fsgc.GlassPly.from_nominal_thickness(self.t2nom,glassType)
        package = [self.ply1,self.ply2,self.ply3]
        self.buildup = [fsgc.NonCompositeMethod(package)]
    
    def test_h_efw(self):
        t_act = 9.09479121*fsgc.ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efw, t_act)
        
    def test_h_efs(self):
        t_act = 10.8112719*fsgc.ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efs[self.ply3], t_act)

class TestShearTransferCoefMethod(unittest.TestCase):
    def setUp(self):
        self.a = 1000 * fsgc.ureg.mm
        self.t1nom = 8*fsgc.ureg.mm
        self.t2nom = 6*fsgc.ureg.mm
        G_pvb = 0.44*fsgc.ureg.MPa
        t_pvb = 1.52*fsgc.ureg.mm
        glassType = "FT"
        self.ply1 = fsgc.GlassPly.from_nominal_thickness(self.t1nom,glassType)
        self.ply2 = fsgc.GlassPly.from_nominal_thickness(self.t2nom,glassType)
        self.interlayer = fsgc.InterLayer(t_pvb, G_pvb)
        package = [self.ply1, self.interlayer, self.ply2]
        self.buildup = [fsgc.ShearTransferCoefMethod(package, self.a)]

    def test_h_efw(self):
        t_act = 9.53304352*fsgc.ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efw, t_act)
    
    def test_h_efs(self):
        t_act1 = 10.2650672*fsgc.ureg.mm
        t_act2 = 11.4310515*fsgc.ureg.mm
        self.assertAlmostEqual(self.buildup[0].h_efs[self.ply1], t_act1)
        self.assertAlmostEqual(self.buildup[0].h_efs[self.ply2], t_act2)
    
    def test_invalid_packages(self):
        # invalid package
        ply3 = fsgc.GlassPly.from_nominal_thickness(self.t1nom, "FT")
        pac_invalid_1 = [self.ply1, self.ply2]
        pac_invalid_2 = [self.ply1, self.ply2, self.interlayer]
        pac_invalid_3 = [self.ply1, self.interlayer, self.ply2, self.interlayer, ply3]

        with self.assertRaises(AssertionError) as cm:
            buildup = [fsgc.ShearTransferCoefMethod(pac_invalid_1,self.a)]
        self.assertEqual(str(cm.exception), "Method is only valid for 2 ply glass laminates")

        with self.assertRaises(AssertionError) as cm:
            buildup = [fsgc.ShearTransferCoefMethod(pac_invalid_2,self.a)]
        self.assertEqual(str(cm.exception), "Method is only valid for 2 ply glass laminates")

        with self.assertRaises(AssertionError) as cm:
            buildup = [fsgc.ShearTransferCoefMethod(pac_invalid_3,self.a)]
        self.assertEqual(str(cm.exception), "Method is only valid for 2 ply glass laminates")

if __name__ == '__main__':
    unittest.main()