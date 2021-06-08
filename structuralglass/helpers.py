from scipy import interpolate
import numpy as np
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

    def __init__(self, dim_x,dim_y, t, E):
        """
            Args:
                ratio (float): the ratio of the largest dimension to the smallest dimension (rectangular panel)
        """
        
        if dim_x < Q_(0,'mm') or dim_y < Q_(0,'mm'): raise ValueError("Dimensions must be greater than zero.")
        if t < Q_(0,'mm'): raise ValueError("Thickness must be greater than zero.")
        if E < Q_(0,'MPa'): raise ValueError("Elastic modulus must be greater than zero.")

        self._b, self._a = np.sort([dim_x, dim_y])
        self._ratio = self._a/self._b
        self._E = E
        ratios = [1, 1.2, 1.4, 1.6, 1.8, 2, 3, 4, 5, 1e16]
        beta = [0.2874, 0.3762, 0.453, 0.5172, 0.5688, 0.6102, 0.7134, 0.741, 0.7476, 0.75]
        alpha = [0.044, 0.0616, 0.077, 0.0906, 0.1017, 0.111, 0.1335, 0.14, 0.1417, 0.1421]
        gamma = [0.42, 0.455, 0.478, 0.491, 0.499, 0.503, 0.505, 0.502, 0.501, 0.5]

        self.beta = interpolate.interp1d(ratios, beta)
        self.alpha = interpolate.interp1d(ratios, alpha)
        self.gamma = interpolate.interp1d(ratios, gamma)

        @ureg.check(None, '[pressure]')
        def stress_max(self,q):
            return self.beta(self.ratio)*q*self.b**2/self.t**2
        @ureg.check(None, '[pressure]')
        def deflection_max(self,q):
            return -self.alpha(self.ratio)*q*self.b**4/(self.E*self.t**3)
        @ureg.check(None, '[pressure]')
        def reaction_max(self,q):
            return self.gamma(self.ratio)*q*self.b
