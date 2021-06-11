from pint.registry_helpers import check
from . import ureg, Q_
from .helpers import Roarks4side

class IGUWindDemands:
    """Calculates the demands on an IGU under wind load.
    The method uses stiffness based load sharing to distribute the wind load
    and equivalent thickness to determine stress and deflections.

    Attributes
    ----------
    windLoad : Quantity [pressure]
        The wind load on the IGU.
    buildup : List[GlassLiteEquiv]
        The buildup.
    dim_x : Quantity [length]
        The x-dimensions of the plate.
    dim_y : Quantity [length]
        The y-dimensions of the plate.
    LSF : Dict[GlassLiteEquiv, float]
        The load share factor for each package.
    stress : Dict[GlassPly, Quantity [pressure]]
        The stress in each ply.
    deflection : Dict[GlassLiteEquiv, Quantity [pressure]]
        The deflection of each package.

    Methods
    -------
    solve():
        Runs the solver.
    """
    def __init__(self, buildup, wind_load, dim_x, dim_y):
        """Constructor.

        Parameters
        ----------
        buildup : List[GlassLiteEquiv]
            The buildup.
        wind_load : Quantity [pressure]
            The wind load on the IGU.
        dim_x : Quantity [length]
            The x-dimensions of the plate.
        dim_y : Quantity [length]
            The y-dimensions of the plate.

        Raises
        ------
        ValueError
            1. If buildup contains duplicate objects, to avoid this use deep copy.
            2. If a mixture of effective thickness models is used. Only one model type should be used.
        """
        # Check that the list unique instances and that only a single type of effective thickness model is used.
        if len(buildup) != len(set(buildup)): 
            raise ValueError("The buildup must contain unique objects, use deep copy.")
        if len(set(map(lambda x: type(x), buildup)))!=1: 
            raise ValueError("Mixing of effective thickness models. Only one model should be used.")
        
        self.wind_load = wind_load
        self.buildup = buildup
        self._stress = {}
        self._deflection = {}
        self.dim_x = dim_x
        self.dim_y = dim_y

    @property
    def wind_load(self):
        """Get the wind load.

        Returns
        -------
        Quantity [pressure]
        """ 
        return self._wind_load
    
    @wind_load.setter
    @ureg.check(None, "[pressure]")
    def wind_load(self, value):
        """Set the wind load.

        Parameters
        ----------
        value : Quantity [pressure]
        """
        self._wind_load = value

    @property
    def buildup(self):
        """Get the buildup.

        Returns
        -------
        List[GlassLiteEquiv]
        """
        return self._buildup
    
    @buildup.setter
    def buildup(self, value):
        """Set the buildup.

        Parameters
        ----------
        value : List[GlassLiteEquiv]
        """
        self._buildup = value
        denom = sum(map(lambda x: x.E*(x.h_efw)**3 , self.buildup))
        self._LSF = dict(zip(self.buildup,map(lambda x: x.E*(x.h_efw)**3/denom , self.buildup)))
    
    @property
    def stress(self):
        """Get the stress.

        Returns
        -------
        Dict[GlassPly, Quantity [pressure]]
        """
        return self._stress
    
    @property
    def deflection(self):
        """Get the deflection.

        Returns
        -------
        Dict[GlassLiteEquiv, Quantity [pressure]]
        """
        return self._deflection

    @property
    def LSF(self):
        """The load share factor for each package.

        Returns
        -------
        Dict[GlassLiteEquiv, float]
        """
        return self._LSF

    @property
    def dim_x(self):
        """Get the dim_x.

        Returns
        -------
        Quantity['length']
        """
        return self._dim_x
    
    @dim_x.setter
    @ureg.check(None, '[length]')
    def dim_x(self, value):
        """Set the dim_x.

        Parameters
        ----------
        value : Quantity['length']

        Raises
        ------
        ValueError
            If the dimension is less than 0 inch/mm
        """
        if value < Q_(0,'mm'): raise ValueError("Dimensions must be greater than zero.")
        self._dim_x = value

    @property
    def dim_y(self):
        """Get the dim_y.

        Returns
        -------
        Quantity['length']
        """
        return self._dim_y
    
    @dim_y.setter
    @ureg.check(None, '[length]')
    def dim_y(self, value):
        """Set the dim_y.

        Parameters
        ----------
        value : Quantity['length']

        Raises
        ------
        ValueError
            If the dimension is less than 0 inch/mm
        """
        if value < Q_(0,'mm'): raise ValueError("Dimensions must be greater than zero.")
        self._dim_y = value    

    def solve(self):
        """Runs the solver.
        """
        # Determine the load share factor
        for lite in self.buildup:
            r4s = Roarks4side(lite.E, self.dim_x, self.dim_y)
            for ply, h_efs in lite.h_efs.items():
                r4s.t = h_efs
                self.stress[ply] = r4s.stress_max(self.wind_load * self.LSF[lite])
            r4s.t = lite.h_efw
            self.deflection[lite] = r4s.deflection_max(self.wind_load * self.LSF[lite])
