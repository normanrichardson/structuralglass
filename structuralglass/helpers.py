from scipy import interpolate
from . import ureg, Q_

class Roarks4side:
    """
        Roarks four sided simply supported plate calculations.

        ...

        Attributes
        ----------
        beta : float
            The beta factor interpolated in the tables.
        alpha : float
            The alpha factor interpolated in the tables.
        gamma : float
            The gamma factor interpolated in the tables.

        Methods
        -------
        __init__(ratio):
            Constructor for a panels aspect ratio.
    """
    @ureg.check(None, '[length]','[length]','[length]','[pressure]')
    def __init__(self, dim_x, dim_y, t, E):
        """
            Args:
                ratio (float): the ratio of the largest dimension to the smallest dimension (rectangular panel)
        """
        self._ratio = None
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.t = t
        self.E = E
        self._reset_ratio()
        
        ratios = [1, 1.2, 1.4, 1.6, 1.8, 2, 3, 4, 5, 1e16]
        beta = [0.2874, 0.3762, 0.453, 0.5172, 0.5688, 0.6102, 0.7134, 0.741, 0.7476, 0.75]
        alpha = [0.044, 0.0616, 0.077, 0.0906, 0.1017, 0.111, 0.1335, 0.14, 0.1417, 0.1421]
        gamma = [0.42, 0.455, 0.478, 0.491, 0.499, 0.503, 0.505, 0.502, 0.501, 0.5]

        self.beta = interpolate.interp1d(ratios, beta)
        self.alpha = interpolate.interp1d(ratios, alpha)
        self.gamma = interpolate.interp1d(ratios, gamma)

    @ureg.check(None, '[pressure]')
    def stress_max(self,q):
        value = self.beta(self._ratio)*q*(self._b/self.t)**2
        return value.to_reduced_units()
    @ureg.check(None, '[pressure]')
    def deflection_max(self,q):
        value = -self.alpha(self._ratio)*q*self._b**4/(self.E*self.t**3)
        return value.to_reduced_units()
    @ureg.check(None, '[pressure]')
    def reaction_max(self,q):
        value = self.gamma(self._ratio)*q*self._b
        return value.to_reduced_units()

    def _reset_ratio(self):
        self._a, self._b = (self.dim_x > self.dim_y) if self.dim_x > self.dim_y else (self.dim_y, self.dim_x)
        self._ratio = float(self._a/self._b)

    @property
    def dim_x(self):
        return self._dim_x
    
    @dim_x.setter
    @ureg.check(None, "[length]")
    def dim_x(self, value):
        if value < Q_(0,'mm'): raise ValueError("Dimensions must be greater than zero.")
        self._dim_x = value
        if self._ratio is not None:
            self._reset_ratio()
    
    @property
    def dim_y(self):
        return self._dim_y
    
    @dim_y.setter
    @ureg.check(None, "[length]")
    def dim_y(self,value):
        if value < Q_(0,'mm'): raise ValueError("Dimensions must be greater than zero.")
        self._dim_y = value
        if self._ratio is not None:
            self._reset_ratio()
    
    @property
    def t(self):
        return self._t

    @t.setter
    @ureg.check(None, '[length]')
    def t(self, value):
        if value < Q_(0,'mm'): raise ValueError("Thickness must be greater than zero.")
        self._t = value

    @property
    def E(self):
        return self._E

    @E.setter
    @ureg.check(None, '[pressure]')
    def E(self, value):
        if value < Q_(0,'MPa'): raise ValueError("Elastic modulus must be greater than zero.")
        self._E = value
