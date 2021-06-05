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
    def __init__(self, width, height, buildup, windLoad):
        # Check that the list unique instances and that only a single type of effective thickness model is used.
        assert len(buildup) == len(set(buildup)), "The buildup must contain unique objects, use deep copy."
        assert len(set(map(lambda x: type(x), buildup)))==1, "Mixing of effective thickness models. Only one model should be used."
        self.windLoad = windLoad
        self.buildup = buildup
        if width<height:
            self.a, self.b = height, width
        else:
            self.b, self.a = height, width

        E_glass = 71.7 * ureg.GPa
        r4s = Roarks4side((self.a/self.b).magnitude)

        # Determine the load share factor
        denom = sum(map(lambda x: (x.h_efw)**3 , self.buildup))
        self.LSF = dict(zip(self.buildup,map(lambda x: x.h_efw**3/denom , self.buildup)))

        self.stress = {}
        self.deflection = {}
        for lite in self.buildup:
            for ply, h_efs in lite.h_efs.items():
                self.stress[ply] = (r4s.beta * self.windLoad * self.LSF[lite] * self.b**2 / (h_efs**2)).to('MPa')

            self.deflection[lite] =(r4s.alpha * self.windLoad * self.LSF[lite] * self.b**4 / (E_glass * lite.h_efw**3)).to('mm') 
