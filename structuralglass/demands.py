from . import ureg, Q_
from .helpers import Roarks4side

class GlassPanel:
    
    """
        A class to represent a glass panel, its dimensions, buildup and windload.

        ...

        Attributes
        ----------
        windLoad : Quantity [pressure]
            The wind load on the panel.
        buildup : List[GlassLiteEquiv]
            The buildup
        a : Quantity [length]
            The larger dimention.
        b : Quantity [length]
            The smaller dimention.
        LSF : Quantity [dimensionless]
            The load share factor for each package.
        stress : Dict[GlassPly, Quantity [pressure]]
            The stress in each ply.
        deflection : Dict[GlassLiteEquiv, Quantity [pressure]]
            The deflection of each package.

        Methods
        -------
        __init__(width, height, buildup, windLoad):
            Constructor for a panels aspect ratio.
    """
    def __init__(self, buildup, wind_load, **kwargs):
        # Check that the list unique instances and that only a single type of effective thickness model is used.
        if len(buildup) != len(set(buildup)): 
            raise ValueError("The buildup must contain unique objects, use deep copy.")
        if len(set(map(lambda x: type(x), buildup)))!=1: 
            raise ("Mixing of effective thickness models. Only one model should be used.")
        
        self.wind_load = wind_load
        self.buildup = buildup
        self._stress = {}
        self._deflection = {}
        self.model_params = kwargs

    @property
    def wind_load(self):
        return self._wind_load
    
    @wind_load.setter
    @ureg.check(None, "[pressure]")
    def wind_load(self, value):
        self._wind_load = value

    @property
    def buildup(self):
        return self._buildup
    
    @buildup.setter
    def buildup(self, value):
        self._buildup = value
        denom = sum(map(lambda x: x.E*(x.h_efw)**3 , self.buildup))
        self._LSF = dict(zip(self.buildup,map(lambda x: x.E*(x.h_efw)**3/denom , self.buildup)))
    
    @property
    def stress(self):
        return self._stress
    
    @property
    def deflection(self):
        return self._deflection

    @property
    def LSF(self):
        return self._LSF 

    def solve(self):
        # Determine the load share factor
        for lite in self.buildup:
            self.model_params["E"] = lite.E
            r4s = Roarks4side(**self.model_params)
            for ply, h_efs in lite.h_efs.items():
                r4s.t = h_efs
                self.stress[ply] = r4s.stress_max(self.wind_load * self.LSF[lite])
            r4s.t = lite.h_efw
            self.deflection[lite] = r4s.deflection_max(self.wind_load * self.LSF[lite])