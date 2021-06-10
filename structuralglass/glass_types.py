from . import ureg, Q_
import abc
import scipy.stats as ss

class GlassType:
    """
    An abstract class to represent the allowable stress of glass.
    Unique formulations of the mechanical behaviour are derived from this class.

    Attributes
    ----------
    stress_surface: Quantity [pressure] i.e. [stress]
        The base allowable surface stress for the glass type.
    stress_edge : Quantity [pressure] i.e. [stress]
        The base allowable edge stress for the glass type.
    duration_factor : float
        The duration factor for the glass type.
    coef_variation : float
        The coefficient of variation for the glass type. 
        This factor describes the statistical behavior of the failure stress.
    surf_factors : Dict [string, float]
        The allowable stress reduction factor for different surface treatments.
        e.g. "Acid etching" can reduce the allowable stress by 0.5  
    
    Methods
    -------
    load_duration_factor(time = 3*ureg.sec)
        Determines the load duration factor for the glass type.
    design_factor(ratio)
        Determines the design factor for the glass type based on a given failure 
        ratio (e.g. 1/1000). This can be used to convert the average breaking stress
        to the stress corresponding with the failure ratio.
    prob_breakage_factor(ratio)
        Determines the probability of breakage factor for the glass type based 
        on a given failure ratio (e.g. 1/1000).
    surf_treat_factor(surf_treat)
        Looks up the reduction associated with a surface treatment
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
        """Get base allowable surface stress.

        Returns
        -------
        Quantity [pressure]
        """
        return self._stress_surface
    
    @stress_surface.setter
    @ureg.check(None, '[pressure]')
    def stress_surface(self, value):
        """Set base allowable surface stress.

        Parameters
        ----------
        value : Quantity [pressure]

        Raises
        ------
        ValueError
            The base allowable surface stress cannot be less than 0MPa.
        """
        if value < Q_(0, "MPa"): raise ValueError("The base allowable surface stress cannot be less than zero.")
        self._stress_surface = value

    @property
    def stress_edge(self):
        """Get base allowable edge stress.

        Returns
        -------
        Quantity [pressure]
        """
        return self._stress_edge
    
    @stress_edge.setter
    @ureg.check(None, '[pressure]')
    def stress_edge(self, value):
        """Set base allowable edge stress.

        Parameters
        ----------
        value : Quantity [pressure]

        Raises
        ------
        ValueError
            The base allowable edge stress cannot be less than 0MPa.
        """
        if value < Q_(0, "MPa"): raise ValueError("The base allowable edge stress cannot be less than zero.")
        self._stress_edge = value

    @property
    def duration_factor(self):
        """Get the duration factor.

        Returns
        -------
        float
        """
        return self._duration_factor

    @duration_factor.setter
    def duration_factor(self, value):
        """Set the duration factor.

        Parameters
        ----------
        value : float

        Raises
        ------
        ValueError
            The duration factor cannot be less than 0.
        """
        if value < Q_(0, "MPa"): raise ValueError("The base allowable edge stress cannot be less than zero.")
        self._duration_factor = value
    
    @property
    def coef_variation(self):
        """Get the coefficient of variation.

        Returns
        -------
        float
        """
        return self._coef_variation

    @coef_variation.setter
    def coef_variation(self, value):
        """Set the coefficient of variation.

        Parameters
        ----------
        value : float
        """
        self._coef_variation = value

    @property
    def surf_factors(self):
        """Get the allowable stress reduction factor for different surface treatments.

        Returns
        -------
        dict(string, float)
        """
        return self._surf_factors

    @surf_factors.setter
    def surf_factors(self, value):
        """Set the allowable stress reduction factor for different surface treatments.

        Parameters
        ----------
        value : float
        """
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
