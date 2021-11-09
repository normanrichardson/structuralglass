"""
The NCSEA Glass Design Guide presents a common mathematical model for the
strength of fabricated glass. This common model is reflected in the class
:class:`~GlassType`.

Much like steel, float glass's strength properties can be manipulated using
heat treatments and chemical processes. Different processes have been
quantified and codified. Glass fabricators can produce glass plys that are
either:

 - annealed
 - heat strengthened
 - fully tempered

To facilitate these common designations a :class:`~GlassType` can be created
using the :meth:`~structuralglass.glass_types.GlassType.from_name` and
:meth:`~GlassType.from_abbr` class methods:

::

    from structuralglass import Q_
    import structuralglass.glass_types as gt

    # Allowable stress FT
    ft = gt.GlassType.from_name("Fully Tempered")
    allow_stress_ft = ft.prob_breakage_factor(1/1000) \\
        * ft.load_duration_factor(Q_(3, "sec")) \\
        * ft.surf_treat_factor("None") * ft.stress_edge     # Q_(66.448, "MPa")

    # Allowable stress AN
    an = gt.GlassType.from_abbr("AN")
    allow_stress_an = an.prob_breakage_factor(1/1000) \\
        * ft.load_duration_factor(Q_(3, "sec")) \\
        * ft.surf_treat_factor("None") * ft.stress_edge     # Q_(12.464, "MPa")

A background registry holds the glass type parameters.
New glass type parameters can be added via the :func:`~register_glass_type`
function.

::

    from structuralglass import Q_
    from structuralglass import glass_types as gt

    gt.register_glass_type(
        name="My Fully Tempered",
        stress_surface=Q_(93.1, "MPa"),
        stress_edge=Q_(73.0, "MPa"),
        duration_factor=47.5,
        coef_variation=0.2,
        surf_factors={
            "None": 1,
            "Fritted": 1,
            "Acid etching": 0.5,
            "Sandblasting": 0.5
        },
        abbr="MyFT"
    )

Glass types can be removed via the :func:`~deregister_glass_type` function.
The underlying data can be viewed via the :func:`~get_glass_types_data`
function. The abbreviation mapping can be viewed via the
:func:`~get_abbr_data` function.
"""

import copy

import scipy.stats as ss

from . import Q_, ureg


class GlassType:
    """
    A class that represents the stress factors in glass.
    """

    @ureg.check(None, "[pressure]", "[pressure]", None, None, None)
    def __init__(
        self,
        stress_surface,
        stress_edge,
        duration_factor,
        surf_factors,
        coef_variation=0.2,
    ):
        """
        Constructor.

        Parameters
        ----------
            stress_surface : :class:`~pint.Quantity` [pressure] i.e. [stress]
                The base allowable surface stress for the glass type.
            stress_edge : :class:`~pint.Quantity` [pressure] i.e. [stress]
                The base allowable edge stress for the glass type.
            duration_factor : :class:`float`
                The duration factor for the glass type.
            surf_factors : :class:`dict` (:class:`str`, :class:`float`)
                The allowable stress reduction factor for different surface
                treatments. e.g. "Acid etching" can reduce the allowable
                stress by 0.5.
            coef_variation  : :class:`float`, optional
                The coefficient of variation for the glass type.
                This factor describes the statistical behavior of the failure
                stress. By default 0.2.
        """

        self.stress_surface = stress_surface
        self.stress_edge = stress_edge
        self.duration_factor = duration_factor
        self.coef_variation = coef_variation
        self.surf_factors = surf_factors

    @classmethod
    def from_name(cls, name):
        """
        Class method to creating a GlassType from an identifier held in the
        registry.

        Parameters
        ----------
        name : :class:`str`
            Identifier.

        Returns
        -------
        :class:`GlassType`

        Raises
        ------
        ValueError
            When the registry does not contain the identifier.
        """

        if name in _glass_type_registry:
            return cls(**_glass_type_registry[name])
        else:
            raise ValueError(
                "The register does not contain the name" / f"key {name}."
            )

    @classmethod
    def from_abbr(cls, abbr):
        """
        Class method to creating a GlassType from an abbreviation held in the
        registry.

        Parameters
        ----------
        name : :class:`str`
            Abbreviation.

        Returns
        -------
        :class:`GlassType`

        Raises
        ------
        ValueError
            When the registry does not contain the abbreviation.
        """

        if abbr in _glass_type_abbr:
            return cls(**_glass_type_registry[_glass_type_abbr[abbr]])
        else:
            raise ValueError(
                "The register does not contain the abbr key " f"{abbr}."
            )

    @ureg.check(None, "[time]")
    def load_duration_factor(self, time=Q_(3, "sec")):
        """
        Determines the load duration factor for the glass type.

        Parameters
        ----------
        time : :class:`~pint.Quantity` [time], optional
            The load duration, by default 3*ureg.sec
        Returns
        -------
        :class:`float`
            Load duration factor to apply to the base stress.
        """

        return 1 / ((time / (3 * ureg.sec)) ** (1 / self.duration_factor))

    def design_factor(self, ratio):
        """
        Determines the design factor for the glass type based on a given
        failure ratio (e.g. 1/1000). This can be used to convert the average
        breaking stress to the stress corresponding with the failure ratio.

        Parameters
        ----------
        ratio : :class:`float`
            Failure ratio. E.g. 1/1000, 8/1000

        Returns
        -------
        :class:`float`
            The design factor for the glass type.
        """

        return 1 / (1 - self.coef_variation * ss.norm.ppf(1 - ratio))

    def prob_breakage_factor(self, ratio):
        """
        Determines the probability of breakage factor for the glass type based
        on a given failure ratio (e.g. 1/1000).

        Parameters
        ----------
        ratio : :class:`float`
            Failure ratio. E.g. 1/1000, 8/1000

        Returns
        -------
        :class:`float`
            Probability of breakage factor to apply to the base stress.
        """

        return self.design_factor(0.008) / self.design_factor(ratio)

    def surf_treat_factor(self, surf_treat):
        """
        Looks up the reduction associated with a surface treatment

        Parameters
        ----------
        surf_treat : :class:`str`
            Looks up the factor for the surface treatment.

        Returns
        -------
        :class:`float`
            Surface treatment factor to apply to the base stress.
        """

        return self.surf_factors[surf_treat]

    @property
    def stress_surface(self):
        """
        The base allowable surface stress in
        :class:`~pint.Quantity` [pressure].

        Raises
        ------
        ValueError
            When the base allowable surface stress is set to less than 0MPa.
        """

        return self._stress_surface

    @stress_surface.setter
    @ureg.check(None, "[pressure]")
    def stress_surface(self, value):
        if value < Q_(0, "MPa"):
            raise ValueError(
                "The base allowable surface stress cannot be less" "than zero."
            )
        self._stress_surface = value

    @property
    def stress_edge(self):
        """
        The base allowable edge stress as :class:`~pint.Quantity` [pressure].

        Raises
        ------
        ValueError
            When the base allowable edge stress is set to less than 0MPa.
        """

        return self._stress_edge

    @stress_edge.setter
    @ureg.check(None, "[pressure]")
    def stress_edge(self, value):
        if value < Q_(0, "MPa"):
            raise ValueError(
                "The base allowable edge stress cannot be less " "than zero."
            )
        self._stress_edge = value

    @property
    def duration_factor(self):
        """
        The duration factor.

        Raises
        ------
        ValueError
            When the duration factor is set less than 0.
        """

        return self._duration_factor

    @duration_factor.setter
    def duration_factor(self, value):
        if value < 0:
            raise ValueError("The duration factor cannot be less than 0.")
        self._duration_factor = value

    @property
    def coef_variation(self):
        """
        The coefficient of variation.
        """

        return self._coef_variation

    @coef_variation.setter
    def coef_variation(self, value):
        self._coef_variation = value

    @property
    def surf_factors(self):
        """
        The allowable stress reduction factor for different surface
        treatments as a :class:`dict` of {:class:`str`: :class:`float`}
        """

        return self._surf_factors

    @surf_factors.setter
    def surf_factors(self, value):
        self._surf_factors = value


# Glass type registry
_glass_type_registry = {}
_glass_type_abbr = {}


def register_glass_type(
    name,
    stress_surface,
    stress_edge,
    duration_factor,
    coef_variation,
    surf_factors,
    *,
    abbr=None,
):
    """
    Register a new glass type.

    Parameters
    ----------
    name : :class:`str`
        Identifier
    stress_surface : :class:`~pint.Quantity` [pressure] i.e. [stress]
        The base allowable surface stress for the glass type.
    stress_edge : :class:`~pint.Quantity` [pressure] i.e. [stress]
        The base allowable edge stress for the glass type.
    duration_factor : :class:`float`
        The duration factor for the glass type.
    coef_variation  : :class:`float`, optional
        The coefficient of variation for the glass type. This factor describes
        the statistical behavior of the failure stress.
    surf_factors : :class:`dict` (:class:`str`, :class:`float`)
        The allowable stress reduction factor for different surface treatments.
        e.g. "Acid etching" can reduce the allowable stress by 0.5
    abbr : :class:`str`, optional
        Abbreviation, by default None

    Raises
    ------
    ValueError
        If the name identifier already in use.
    ValueError
        If the abbreviation identifier already in use.
    """

    if name in _glass_type_registry:
        raise ValueError(
            "Name identifier already in use. " f"Deregister `{name}` first."
        )

    if abbr in _glass_type_abbr:
        raise ValueError(
            "Abbreviation identifier already in use. "
            f"Deregister `{_glass_type_abbr[abbr]}` first."
        )

    data = {
        "stress_surface": stress_surface,
        "stress_edge": stress_edge,
        "duration_factor": duration_factor,
        "coef_variation": coef_variation,
        "surf_factors": surf_factors,
    }

    _glass_type_registry[name] = data
    if abbr is not None:
        _glass_type_abbr[abbr] = name


def deregister_glass_type(name):
    """
    Deregister an existing glass type.

    Parameters
    ----------
    name : :class:`str`
        Identifier
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
    """
    Get a deep copy of the registry.

    Returns
    -------
    :class:`dict` (:class:`str`, :class:`dict`)
        A dictionary of all the GlassType parameters (as :class:`dict`), the
        keys are the identifiers.
    """

    return copy.deepcopy(_glass_type_registry)


def get_abbr_data():
    """
    Get a deep copy of the abbreviation map.

    Returns
    -------
    :class:`dict` (:class:`str`, :class:`str`)
        A dictionary of the identifiers, the keys are the abbreviation.
    """

    return copy.deepcopy(_glass_type_registry)


# Register common glass types

register_glass_type(
    name="Annealed",
    stress_surface=Q_(23.3, "MPa"),
    stress_edge=Q_(18.3, "MPa"),
    duration_factor=16,
    coef_variation=0.22,
    surf_factors={
        "None": 1,
        "Fritted": 1,
        "Acid etching": 0.5,
        "Sandblasting": 0.5,
    },
    abbr="AN",
)

register_glass_type(
    name="Heat Strengthened",
    stress_surface=Q_(46.6, "MPa"),
    stress_edge=Q_(36.5, "MPa"),
    duration_factor=31.7,
    coef_variation=0.15,
    surf_factors={
        "None": 1,
        "Fritted": 1,
        "Acid etching": 0.5,
        "Sandblasting": 0.5,
    },
    abbr="HS",
)

register_glass_type(
    name="Fully Tempered",
    stress_surface=Q_(93.1, "MPa"),
    stress_edge=Q_(73.0, "MPa"),
    duration_factor=47.5,
    coef_variation=0.1,
    surf_factors={
        "None": 1,
        "Fritted": 1,
        "Acid etching": 0.5,
        "Sandblasting": 0.5,
    },
    abbr="FT",
)
