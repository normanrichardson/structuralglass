"""
The NCSEA Glass Design Guide presents a common mathematical model for the strength of fabricated glass.
This common model is reflected in the abstract class :class:`~structuralglass.layers.GlassType`.

Much like steel, float glass' strength properties can be manipulated using heat treatments and chemical processes.
Different processes have been quantified and codified.
Glass fabricators can produce glass plys that are either:

 - annealed
 - heat strengthened
 - fully tempered

To facilitate these common designations :class:`~structuralglass.layers.Annealed`, :class:`~structuralglass.layers.HeatStrengthened`, and :class:`~structuralglass.layers.FullyTempered` can be used.

::

    from structuralglass import Q_
    import structuralglass.glass_types as gt
        
    # Allowable stress
    ft = gt.FullyTempered()
    allow_stress = ft.prob_breakage_factor(1/1000) \\
        * ft.load_duration_factor(Q_(3, "sec")) \\
        * ft.surf_treat_factor("None") * ft.stress_edge     #Q(66.448, "MPa")

These classes are derived from :class:`~structuralglass.layers.GlassType`.
Unique formulations of the mechanical behavior can be derived from :class:`~structuralglass.layers.GlassType`.

::

    from structuralglass import Q_
    import structuralglass.glass_types as gt


    class MyFT(gt.GlassType):
    \"\"\"My tempered glass type.
    \"\"\"

    def __init__(self):
        stress_surface =  Q_(93.1, "MPa")
        stress_edge    = Q_(73.0, "MPa")
        duration_factor = 47.5
        coef_variation = 0.2
        surf_factors = {
            "None" : 1,
            "Fritted" : 1,
            "Acid etching" : 0.5,
            "Sandblasting" : 0.5
        }
        super(MyFT, self).__init__(stress_surface, stress_edge, \\
            duration_factor, surf_factors, coef_variation)

    # Allowable stress
    ft = MyFT()
    allow_stress = ft.prob_breakage_factor(1/1000) \\
        * ft.load_duration_factor(Q_(3, "sec")) \\
        * ft.surf_treat_factor("None") * ft.stress_edge     #Q(53.805, "MPa")

"""

from . import ureg, Q_
import abc
import scipy.stats as ss

class GlassType:
    """
    An abstract class to represent the allowable stress of glass.
    Unique formulations of the mechanical behaviour are derived from this class.
    """

    __metaclass__ = abc.ABCMeta
    @ureg.check(None, '[pressure]', '[pressure]', None, None, None)
    def __init__(self, stress_surface, stress_edge, duration_factor, surf_factors, coef_variation = 0.2):
        """Abstract class constructor

        Parameters
        ----------
            stress_surface : Quantity [pressure] i.e. [stress]
                The base allowable surface stress for the glass type.
            stress_edge : Quantity [pressure] i.e. [stress]
                The base allowable edge stress for the glass type.
            duration_factor : float
                The duration factor for the glass type.
            surf_factors : dict(string, float)
                The allowable stress reduction factor for different surface treatments.
                e.g. "Acid etching" can reduce the allowable stress by 0.5 
            coef_variation  : float, optional 
                The coefficient of variation for the glass type. 
                This factor describes the statistical behavior of the failure stress.
                By default 0.2.
        """

        self.stress_surface = stress_surface
        self.stress_edge = stress_edge
        self.duration_factor = duration_factor
        self.coef_variation = coef_variation
        self.surf_factors = surf_factors
    
    @ureg.check(None, '[time]')
    def load_duration_factor(self, time = 3*ureg.sec):
        """Determines the load duration factor for the glass type.

        Parameters
        ----------
        time : Quantity [time], optional
            The load duration, by default 3*ureg.sec
        Returns
        -------
        float
            Load duration factor to apply to the base stress.
        """      

        return 1 / ((time/(3*ureg.sec))**(1/self.duration_factor))

    def design_factor(self, ratio):
        """Determines the design factor for the glass type based on a given failure 
        ratio (e.g. 1/1000). This can be used to convert the average breaking stress
        to the stress corresponding with the failure ratio.

        Parameters
        ----------
        ratio : float
            Failure ratio. E.g. 1/1000, 8/1000

        Returns
        -------
        float
            The design factor for the glass type.
        """

        return 1 / ( 1 - self.coef_variation*ss.norm.ppf(1-ratio) )

    def prob_breakage_factor(self, ratio):
        """Determines the probability of breakage factor for the glass type based 
        on a given failure ratio (e.g. 1/1000).

        Parameters
        ----------
        ratio : float
            Failure ratio. E.g. 1/1000, 8/1000

        Returns
        -------
        float
            Probability of breakage factor to apply to the base stress.
        """

        return self.design_factor(0.008) / self.design_factor(ratio)

    def surf_treat_factor(self, surf_treat):
        """Looks up the reduction associated with a surface treatment

        Parameters
        ----------
        surf_treat : string
            Looks up the factor for the surface treatment.

        Returns
        -------
        float
            Surface treatment factor to apply to the base stress.
        """

        return self.surf_factors[surf_treat]

    @property
    def stress_surface(self):
        """The base allowable surface stress in Quantity [pressure].
        
        Raises
        ------
        ValueError
            When the base allowable surface stress is set to less than 0MPa.
        """

        return self._stress_surface
    
    @stress_surface.setter
    @ureg.check(None, '[pressure]')
    def stress_surface(self, value):
        if value < Q_(0, "MPa"): raise ValueError("The base allowable surface stress cannot be less than zero.")
        self._stress_surface = value

    @property
    def stress_edge(self):
        """The base allowable edge stress as Quantity [pressure].

        Raises
        ------
        ValueError
            When the base allowable edge stress is set to less than 0MPa.
        """

        return self._stress_edge
    
    @stress_edge.setter
    @ureg.check(None, '[pressure]')
    def stress_edge(self, value):
        if value < Q_(0, "MPa"): raise ValueError("The base allowable edge stress cannot be less than zero.")
        self._stress_edge = value

    @property
    def duration_factor(self):
        """The duration factor.

        Raises
        ------
        ValueError
            When the duration factor is set less than 0.
        """

        return self._duration_factor

    @duration_factor.setter
    def duration_factor(self, value):
        if value < 0: raise ValueError("The duration factor cannot be less than 0.")
        self._duration_factor = value
    
    @property
    def coef_variation(self):
        """The coefficient of variation.
        """

        return self._coef_variation

    @coef_variation.setter
    def coef_variation(self, value):
        self._coef_variation = value

    @property
    def surf_factors(self):
        """The allowable stress reduction factor for different surface treatments as a dict(string, float)
        """

        return self._surf_factors

    @surf_factors.setter
    def surf_factors(self, value):
        self._surf_factors = value

class Annealed(GlassType):
    """Annealed glass type.
    """

    def __init__(self):
        stress_surface = 23.3 * ureg.MPa
        stress_edge    = 18.3 * ureg.MPa
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
    """Heat strengthened glass type.
    """

    def __init__(self):
        stress_surface = 46.6 * ureg.MPa
        stress_edge    = 36.5 * ureg.MPa
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
    """Fully tempered glass type.
    """
    
    def __init__(self):
        stress_surface = 93.1 * ureg.MPa
        stress_edge    = 73.0 * ureg.MPa
        duration_factor = 47.5
        coef_variation = 0.1
        surf_factors = {
            "None" : 1,
            "Fritted" : 1,
            "Acid etching" : 0.5,
            "Sandblasting" : 0.5
        }
        super(FullyTempered, self).__init__(stress_surface, stress_edge, duration_factor, surf_factors, coef_variation)
