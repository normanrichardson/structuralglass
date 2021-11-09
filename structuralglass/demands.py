"""
When determining demands - depending on project specifics, the maturity of the
project, etc - it is often useful to have simple demand calculations.
In general, more sophisticated models are required.

::

    from structuralglass import Q_
    import structuralglass.layers as lay
    import structuralglass.equiv_thick_models as et
    import structuralglass.demands as dem

    # Plate dimensions
    a = Q_(5, "ft")
    b = Q_(8, "ft")
    t1nom = Q_(8, "mm")
    t2nom = Q_(8, "mm")

    # Panel force
    wind_load = Q_(30, "psf")

    # Plys
    ply1 = lay.GlassPly.from_nominal_thickness(t1nom)
    ply2 = lay.GlassPly.from_nominal_thickness(t2nom)

    # Package specifying the model type
    package1 = et.MonolithicMethod([ply1])
    package2 = et.MonolithicMethod([ply2])
    buildup = [package1, package2]

    # Panel
    panel = dem.IGUWindDemands(buildup, wind_load, dim_x=a, dim_y=b)
    panel.solve()

    panel.deflection[package1]      # Q_(-0.47, "in")

"""

from . import Q_, ureg
from .helpers import Roarks4side


class IGUWindDemands:
    """
    A simplified method for IGU under wind load (short duration). The method
    uses stiffness based load sharing to distribute the wind load and
    equivalent thickness to determine stress and deflections.
    """

    def __init__(self, buildup, wind_load, dim_x, dim_y):
        """
        Constructor.

        Parameters
        ----------
        buildup : :class:`list` (:class:`~structuralglass.equiv_thick_models.GlassLiteEquiv`)
            The buildup.
        wind_load : :class:`~pint.Quantity` [pressure]
            The wind load on the IGU.
        dim_x : :class:`~pint.Quantity` [length]
            The x-dimensions of the plate.
        dim_y : :class:`~pint.Quantity` [length]
            The y-dimensions of the plate.

        Raises
        ------
        ValueError
            If buildup contains duplicate objects, to avoid this use deep copy.
        ValueError
            If a mixture of effective thickness models is used. Only one model
            type should be used.
        """

        # Check that the list unique instances and that only a single type of
        # effective thickness model is used.
        if len(buildup) != len(set(buildup)):
            raise ValueError(
                "The buildup must contain unique objects, use deep copy."
            )

        self.wind_load = wind_load
        self.buildup = buildup
        self._stress = {}
        self._deflection = {}
        self.dim_x = dim_x
        self.dim_y = dim_y

    @property
    def wind_load(self):
        """
        The wind load in :class:`~pint.Quantity` [pressure].
        """

        return self._wind_load

    @wind_load.setter
    @ureg.check(None, "[pressure]")
    def wind_load(self, value):
        self._wind_load = value

    @property
    def buildup(self):
        """
        The buildup as a :class:`list`
        (:class:`~structuralglass.equiv_thick_models.GlassLiteEquiv`).
        """

        return self._buildup

    @buildup.setter
    def buildup(self, value):
        self._buildup = value
        denom = sum(map(lambda x: x.E * (x.h_efw) ** 3, self.buildup))
        self._LSF = dict(
            zip(
                self.buildup,
                map(lambda x: x.E * (x.h_efw) ** 3 / denom, self.buildup),
            )
        )

    @property
    def stress(self):
        """
        The stress as a :class:`dict`
        (:class:`~structuralglass.layers.GlassPly`,
        :class:`~pint.Quantity` [pressure])
        """

        return self._stress

    @property
    def deflection(self):
        """
        The deflection as a :class:`dict`
        (:class:`~structuralglass.equiv_thick_models.GlassLiteEquiv`,
        :class:`~pint.Quantity` [pressure])
        """

        return self._deflection

    @property
    def LSF(self):
        """
        The load share factor for each package as a :class:`dict`
        (:class:`~structuralglass.equiv_thick_models.GlassLiteEquiv`,
        :class:`float`)
        """

        return self._LSF

    @property
    def dim_x(self):
        """
        The dim_x as a :class:`~pint.Quantity` ['length'].

        Raises
        ------
        ValueError
            If the dimension is less than 0 inch/mm
        """

        return self._dim_x

    @dim_x.setter
    @ureg.check(None, "[length]")
    def dim_x(self, value):
        if value < Q_(0, "mm"):
            raise ValueError("Dimensions must be greater than zero.")
        self._dim_x = value

    @property
    def dim_y(self):
        """
        The dim_y as a :class:`~pint.Quantity` ['length']

        Raises
        ------
        ValueError
            If the dimension is less than 0 inch/mm
        """

        return self._dim_y

    @dim_y.setter
    @ureg.check(None, "[length]")
    def dim_y(self, value):
        if value < Q_(0, "mm"):
            raise ValueError("Dimensions must be greater than zero.")
        self._dim_y = value

    def solve(self):
        """
        Runs the solver.
        """

        for lite in self.buildup:
            r4s = Roarks4side(lite.E, self.dim_x, self.dim_y)
            lite_load = self.wind_load * self.LSF[lite]
            for ply, h_efs in lite.h_efs.items():
                r4s.t = h_efs
                self._stress[ply] = r4s.stress_max(lite_load)
            r4s.t = lite.h_efw
            self._deflection[lite] = r4s.deflection_max(lite_load)
