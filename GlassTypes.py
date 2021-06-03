import abc
import FourSidedGlassCalc as fsgc
import scipy.stats as ss

class GlassType:
    __metaclass__ = abc.ABCMeta
    def __init__(self, stress_surface, stress_edge, duration_factor, surf_factors, coef_variation = 0.2):
        self.stress_surface = stress_surface
        self.stress_edge = stress_edge
        self.duration_factor = duration_factor
        self.coef_variation = coef_variation
        self.surf_factors = surf_factors
    
    @fsgc.ureg.check(None, '[time]')
    def load_duration_factor(self, time = 3*fsgc.ureg.sec):
        return 1 / ((time.to(fsgc.ureg.sec).magnitude/3)**(1/self.duration_factor))
    def design_factor(self, ratio):
        return 1 / ( 1 - self.coef_variation*ss.norm.ppf(1-ratio) )
    def prob_breakage_factor(self, ratio):
        return self.design_factor(0.008) / self.design_factor(ratio)
    def surf_treat_factor(self, surf_treat):
        return self.surf_factors[surf_treat]
        
class Annealed(GlassType):
    def __init__(self):
        stress_surface = 23.3 * fsgc.ureg.MPa
        stress_edge    = 18.3 * fsgc.ureg.MPa
        duration_factor = 16
        coef_variation = 0.22
        surf_factors = {
            "None" : 1,
            "Fritted" : 1,
            "Acid etching" : 0.5,
            "Sandblasting" : 0.5
        }
        super(Annealed, self).__init__(stress_surface, stress_edge, duration_factor, surf_factors, coef_variation)

class HeatStrengthened(GlassType):
    def __init__(self):
        stress_surface = 46.6 * fsgc.ureg.MPa
        stress_edge    = 36.5 * fsgc.ureg.MPa
        duration_factor = 31.7
        coef_variation = 0.15
        surf_factors = {
            "None" : 1,
            "Fritted" : 1,
            "Acid etching" : 0.5,
            "Sandblasting" : 0.5
        }
        super(HeatStrengthened, self).__init__(stress_surface, stress_edge, duration_factor, surf_factors, coef_variation)

class FullyTempered(GlassType):
    def __init__(self):
        stress_surface = 93.1 * fsgc.ureg.MPa
        stress_edge    = 73.0 * fsgc.ureg.MPa
        duration_factor = 47.5
        coef_variation = 0.1
        surf_factors = {
            "None" : 1,
            "Fritted" : 1,
            "Acid etching" : 0.5,
            "Sandblasting" : 0.5
        }
        super(FullyTempered, self).__init__(stress_surface, stress_edge, duration_factor, surf_factors, coef_variation)
