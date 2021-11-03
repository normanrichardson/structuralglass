"""
The NCSEA Glass Design Guide presents a common mathematical model for the strength of fabricated glass.
This common model is reflected in the class :class:`~structuralglass.glass_types.GlassType`.

Much like steel, float glass's strength properties can be manipulated using heat treatments and chemical processes.
Different processes have been quantified and codified.
Glass fabricators can produce glass plys that are either:

 - annealed
 - heat strengthened
 - fully tempered

To facilitate these common designations a :class:`~structuralglass.glass_types.GlassType` can be created using the :meth:`~structuralglass.glass_types.GlassType.from_name` and :meth:`~structuralglass.glass_types.GlassType.from_abbr` class methods:

::

    from structuralglass import Q_
    import structuralglass.glass_types as gt
        
    # Allowable stress FT
    ft = gt.GlassType.from_name("Fully Tempered")
    allow_stress_ft = ft.prob_breakage_factor(1/1000) \\
        * ft.load_duration_factor(Q_(3, "sec")) \\
        * ft.surf_treat_factor("None") * ft.stress_edge     #Q(66.448, "MPa")
    
    # Allowable stress AN
    an = gt.GlassType.from_abbr("AN")
    allow_stress_an = an.prob_breakage_factor(1/1000) \\
        * ft.load_duration_factor(Q_(3, "sec")) \\
        * ft.surf_treat_factor("None") * ft.stress_edge     #Q(12.464, "MPa")

A background registry holds the glass type parameters.
New glass type parameters can be added via the :func:`~structuralglass.glass_types.register_glass_type` function.

::

    from structuralglass import Q_
    from structuralglass import glass_types as gt

    gt.register_glass_type(
        name="My Fully Tempered", 
        stress_surface = Q_(93.1, "MPa"),
        stress_edge    = Q_(73.0, "MPa"),
        duration_factor = 47.5,
        coef_variation = 0.2,
        surf_factors = {
            "None" : 1,
            "Fritted" : 1,
            "Acid etching" : 0.5,
            "Sandblasting" : 0.5
        },
        abbr="MyFT"
    )

Glass types can be removed via the :func:`~structuralglass.glass_types.deregister_glass_type` function.
The underlying data can be viewed via the :func:`~structuralglass.glass_types.get_glass_types_data` function.
The abbreviation mapping can be viewed via the  :func:`~structuralglass.glass_types.get_abbr_data` function.
"""

from . import ureg, Q_
import scipy.stats as ss
import copy

class GlassType:
    """
    A class that represents the stress factors in glass.
    """

    @ureg.check(None, '[pressure]', '[pressure]', None, None, None)
    def __init__(self, stress_surface, stress_edge, duration_factor, surf_factors, coef_variation = 0.2):
        """Constructor

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
    
    @classmethod
    def from_name(cls, name):
        """Class method to creating a GlassType from a string identifier held in the registry.

        Parameters
        ----------
        name : ``string``
            String identifier.

        Returns
        -------
        GlassType

        Raises
        ------
        ValueError
            When the registry does not contain the string identifier.
        """

        if name in _glass_type_registry:
            return cls(**_glass_type_registry[name])
        else:
            raise ValueError(f"The register does not contain the name key {name}.")

    @classmethod
    def from_abbr(cls, abbr):
        """Class method to creating a GlassType from a string abbreviation held in the registry.

        Parameters
        ----------
        name : ``string``
            String abbreviation.

        Returns
        -------
        GlassType

        Raises
        ------
        ValueError
            When the registry does not contain the string abbreviation.
        """

        if abbr in _glass_type_abbr:
            return cls(**_glass_type_registry[_glass_type_abbr[abbr]])
        else:
            raise ValueError(f"The register does not contain the abbr key {abbr}.")

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

# Glass type registry

_glass_type_registry = {}
_glass_type_abbr = {}

def register_glass_type(name, stress_surface, stress_edge, duration_factor, coef_variation, surf_factors, *, abbr=None):
    """Register a new glass type.

    Parameters
    ----------
    name : string
        Identifier
    stress_surface : Quantity [pressure] i.e. [stress]
        The base allowable surface stress for the glass type.
    stress_edge : Quantity [pressure] i.e. [stress]
        The base allowable edge stress for the glass type.
    duration_factor : float
        The duration factor for the glass type.
    coef_variation  : float, optional 
        The coefficient of variation for the glass type. 
        This factor describes the statistical behavior of the failure stress.
    surf_factors : dict(string, float)
        The allowable stress reduction factor for different surface treatments.
        e.g. "Acid etching" can reduce the allowable stress by 0.5 
    abbr : string, optional
        Abbreviation, by default None

    Raises
    ------
    ValueError
        If the name identifier already in use.
    ValueError
        If the abbreviation identifier already in use.
    """

    if name in _glass_type_registry:
        raise ValueError(f"Name identifier already in use. Deregister `{name}` first.")

    if abbr in _glass_type_abbr:
        raise ValueError(f"Abbreviation identifier already in use. Deregister `{_glass_type_abbr[abbr]}` first.")

    data = {
        "stress_surface": stress_surface,
        "stress_edge" : stress_edge,
        "duration_factor" : duration_factor,
        "coef_variation" : coef_variation,
        "surf_factors" : surf_factors
    }

    _glass_type_registry[name] = data
    if abbr is not None: _glass_type_abbr[abbr] = name

def deregister_glass_type(name):
    """Deregister an existing glass type.

    Parameters
    ----------
    name : ``string``
        String identifier
    """

    key_list = list(_glass_type_abbr.keys())
    val_list = list(_glass_type_abbr.values())
    try:
        position = val_list.index(name)
    except ValueError:
        position = None
    else:
        abbr = key_list[position]
        _glass_type_abbr.pop(abbr, None)

    _glass_type_registry.pop(name, None)
    

def get_glass_types_data():
    """Get a deep copy of the registry.
    
    Returns
    -------
    Dict(string, values)
        A dictionary of all the GlassType parameters, the keys are the string identifiers.
    """

    return copy.deepcopy(_glass_type_registry)

def get_abbr_data():
    """Get a deep copy of the abbreviation map.
    
    Returns
    -------
    Dict(string, string)
        A dictionary of the string identifiers, the keys are the string abbreviation.
    """

    return copy.deepcopy(_glass_type_registry)


# Register common glass types

register_glass_type(
    name = "Annealed", 
    stress_surface = Q_(23.3, "MPa"),
    stress_edge    = Q_(18.3, "MPa"),
    duration_factor = 16,
    coef_variation = 0.22,
    surf_factors = {
        "None" : 1,
        "Fritted" : 1,
        "Acid etching" : 0.5,
        "Sandblasting" : 0.5
    },
    abbr="AN"
)

register_glass_type(
    name = "Heat Strengthened",
    stress_surface = Q_(46.6, "MPa"),
    stress_edge    = Q_(36.5, "MPa"),
    duration_factor = 31.7,
    coef_variation = 0.15,
    surf_factors = {
        "None" : 1,
        "Fritted" : 1,
        "Acid etching" : 0.5,
        "Sandblasting" : 0.5
    },
    abbr="HS"
)

register_glass_type(
    name="Fully Tempered", 
    stress_surface = 93.1 * ureg.MPa,
    stress_edge    = 73.0 * ureg.MPa,
    duration_factor = 47.5,
    coef_variation = 0.1,
    surf_factors = {
        "None" : 1,
        "Fritted" : 1,
        "Acid etching" : 0.5,
        "Sandblasting" : 0.5
    },
    abbr="FT"
)
