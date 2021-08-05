from . import ureg, Q_
from scipy import interpolate
import pint
import numpy as np

# Lookup for nominal thickness to minimal allowable thickness in metric
t_min_lookup_metric = {
            2.0: 1.80,
            2.5: 2.16,
            2.7: 2.59,
            3  : 2.92,
            4  : 3.78,
            5  : 4.57,
            6  : 5.56,
            8  : 7.42,
            10 : 9.02,
            12: 11.91,
            16: 15.09,
            19: 18.26,
            22: 21.44,
            25: 24.61
}

# Lookup for nominal thickness to minimal allowable thickness in imperial
t_min_lookup_imperial = {
            0.09375: 2.16,
            0.125  : 2.92,
            0.15625: 3.78,
            0.1875 : 4.57,
            0.25   : 5.56,
            0.3125 : 7.42,
            0.375  : 9.02,
            0.5    : 11.91,
            0.625  : 15.09,
            0.75   : 18.26,
            0.875  : 21.44,
            1      : 24.61
}

class GlassPly:
    """A class to represent a glass ply, its thinkess (nominal and minimum allowable) and mechanical properties.

    Attributes
    ----------
    E : Quantity [pressure]
        Elastic modulus.
    t_nom : Quantity [length]
        Nominal thickness.
    t_min : Quantity [length]
        Min allowable thickness.
    
    Methods
    -------
    from_nominal_thickness(t_nom):
        Class method to creating a GlassPly with a nominal thickness.
    from_actual_thickness(t_nom):
        Class method to creating a GlassPly with an actual thickness.
    
    Raises
    ------
    pint.DimensionalityError
        If an input argument does not meet the Quantity requirement.
    TypeError
        The provided nominal thickness is not a Quanity['length'] or None.
    ValueError
        Actual thickness/elastic modulus/nominal thickness cannot be less than zero.
    ValueError
        The provided nominal thickness could not be found in the lookup.
    """    
    @ureg.check(None, '[length]', None, '[pressure]')
    def __init__(self, t_min, t_nom = None, E = 71.7 * ureg.GPa):
        """[summary]

        Parameters
        ----------
        t_min : Quantity [length]
            Min allowable thickness.
        t_nom : Quantity [length], optional
            Nominal thickness, by default None (if using actual thickness)
        E : Quantity [pressure], optional
            Elastic modulus, by default 71.7GPa

        Raises
        ------
        pint.DimensionalityError
            If an input argument does not meet the Quantity requirement.
        TypeError
            The provided nominal thickness is not a Quanity['length'] or None.
        ValueError
            Actual thickness/elastic modulus/nominal thickness cannot be less than zero.
        """
        # The check decorator can not be used to check t_nom (as it can be None)
        if t_nom is not None:
            if (isinstance(t_nom,Q_)): 
                if not t_nom.check('[length]'): 
                    dim = t_nom.dimensionality
                    unit = t_nom.units
                    # Is a Quantity but not the corret dim
                    raise pint.DimensionalityError(unit,'inch', dim, '[length]')
            else: raise TypeError("t_nom is not a Quanity['length'] or None.")
            
        if t_min < Q_(0,'inch'): raise ValueError("Actual thickness cannot be less than zero.")

        self.E = 71.7 * ureg.GPa
        self._t_min = t_min
        self._t_nom = t_nom
    
    @classmethod
    @ureg.check(None, '[length]')
    def from_nominal_thickness(cls, t_nom):
        """Class method to creating a GlassPly with a nominal thickness.

        Parameters
        ----------
        t_nom : Quantity [length]
            Nominal thickness.

        Returns
        -------
        GlassPly
        """
        t_min = cls._find_min_from_nom(t_nom)
        return cls(t_min,t_nom)
    
    @classmethod
    @ureg.check(None, '[length]')
    def from_actual_thickness(cls, t_act):
        """Class method to creating a GlassPly with an actual thickness.

        Parameters
        ----------
        t_act : Quantity [length]
            Actual thickness.

        Returns
        -------
        GlassPly
        """
        return cls(t_act)

    @staticmethod
    def _find_min_from_nom(t_nom):
        try:
            t_min = t_min_lookup_metric[t_nom.to(ureg.mm).magnitude] * ureg.mm
        except KeyError:
            try:
                t_min = t_min_lookup_imperial[t_nom.to(ureg.inch).magnitude] * ureg.mm
            except KeyError:
                raise ValueError("Could not find the nominal tickness of {0} in the nominal thickness lookup.".format(t_nom))
        return t_min

    @property
    def E(self):
        """Get the elastic modulus.

        Returns
        -------
        Quantity [pressure]
        """
        return self._E
    
    @E.setter
    @ureg.check(None, '[pressure]')
    def E(self, value):
        """Set the elastic modulus.

        Parameters
        ----------
        value : Quantity [pressure]
            Elastic modulus

        Raises
        ------
        ValueError
            Elastic modulus cannot be less than 0MPa.
        """
        if value < Q_(0,'MPa'): raise ValueError("Elastic modulus cannot be less than zero.")
        self._E = value
    
    @property
    def t_nom(self):
        """Get the nominal thickness.

        Returns
        -------
        Quantity [length]
        """
        return self._t_nom
    
    @t_nom.setter
    @ureg.check(None, '[length]')
    def t_nom(self, value):
        """Set the nominal thickness.

        Parameters
        ----------
        value : Quantity [length]
            Nominal thickness

        Raises
        ------
        ValueError
            Nominal thickness cannot be less than zero.
        """
        if value < Q_(0,'inch'): raise ValueError("Nominal thickness cannot be less than zero.")
        self._t_nom = value
        self._t_min = self._find_min_from_nom(value)

    @property
    def t_min(self):
        """Get the minimum thickness.

        Returns
        -------
        Quantity [length]
        """
        return self._t_min
    
    @t_min.setter
    @ureg.check(None, '[length]')
    def t_min(self, value):
        """Set the minimum thickness.

        Parameters
        ----------
        value : Quantity [length]
            Minimum thickness

        Raises
        ------
        ValueError
            Actual thickness cannot be less than zero.
        """
        if value < Q_(0,'inch'): raise ValueError("Actual thickness cannot be less than zero.")
        self._t_min = value
        self._t_nom = None




class InterLayer:
    """
    A class to represent a glass interlayer(e.g. PVB or SG), and its mechanical properties. 
    Rate dependent properties can be considered via the use of a product table or registered product name

    ...

    Attributes
    ----------
    t : Quantity [length]
        thickness
    G : Quantity [pressure]
        Shear modulus
    temperature: Quantity [temperature]
        The load case temperature, if a product table is used.
    duration:
        The load case duration, if a product table is used.

    Methods
    -------
    from_product_table(t, product_name):
        Class method to creating a interlayer with a registered product name
    from_static(t, G):
        Class method to creating a interlayer with a static shear modulus value
    """
    def __init__(self, t, **kwargs):
        """[summary]

        Parameters
        ----------
        t : [type]
            [description]
        G : Quantity [pressure]
            Shear modulus for the case of a static layer, do not provide a G_table.
        G_table: Dict[(Quantity [temperature],Quantity [time]), Quantity [pressure]]
            Shear modulus table for the case of using an interlayer product table.
            The dictionary keys are (temperature, duration) and associated shear modulus.
            Do not provide a G value.

        Raises
        ------
        ValueError
            If neither G nor G_table are provided.
        ValueError
            If both G and G_table are provided.
        """        
        self.t = t
        G_tmp = kwargs.get('G',None)
        G_table_tmp = kwargs.get('G_table',None)
        if G_tmp is None and G_table_tmp is None:
            raise ValueError("Either G or G_table must be provided.")
        elif  G_tmp is not None and G_table_tmp is not None:
            raise ValueError("Only one of G or G_table must be provided.")
        self._G = G_tmp
        self.G_table = G_table_tmp
        if self.G_table is not None:
            self._temperature = None
            self._duration = None
            # Create a function that does the interpolation for the product table
            # Get the unique values for tempereture in the table in degC
            G_table_x = np.sort(np.array(list(set([ii[0].to("degC").magnitude for ii in self.G_table.keys()]))))
            # Get the unique values for duration in the table in sec
            G_table_y = np.sort(np.array(list(set([ii[1].to("sec").magnitude for ii in self.G_table.keys()]))))
            # Create a meshgrid for the interpolation process
            x, y = np.meshgrid(G_table_x, G_table_y)
            # vectorize the look up for the tables (this is done as the entries in the table may not be in order)
            vlookup = np.vectorize(lambda x,y: self.G_table[Q_(x,"degC"),Q_(y,"sec")].to("MPa").magnitude)
            # Exicute the vectorized lookup
            G_table_z = vlookup(x,y)
            # create the interploation function
            G_interp = interpolate.interp2d(G_table_x, G_table_y, G_table_z, kind='linear')
            # use a decorator to add dimentions to the interpolation function
            self.G_interp_dim = ureg.wraps(ureg.MPa, (ureg.degC,ureg.second))(lambda x,y: G_interp(x,y))

    @classmethod
    @ureg.check(None,"[length]",None)
    def from_product_table(cls, t, product_name):
        """Class method for an interlayer with a product table.

        Parameters
        ----------
        t : Quantity [length]
            The thickness of the interlayer.
        product_name : sting
            The registred name of the product.

        Returns
        -------
        Interlayer
        """
        if not(t > Q_(0, "mm")): raise ValueError("The thickness must be greater than zero [lengh].")
        table = _interLayer_registry.get(product_name, None)
        if table is None:
            raise ValueError("The product is not registered in the product registry.")
        return cls(t,G_table = table)
    
    @classmethod
    @ureg.check(None,"[length]","[pressure]")
    def from_static(cls, t, G):
        """Class method for an interlayer with a static shear modulus.

        Parameters
        ----------
        t : Quantity [length]
            The thickness of the interlayer.
        G : Quantity [pressure]
            The shear modulus.

        Returns
        -------
        Interlayer
        """
        if not(t > Q_(0, "mm")): raise ValueError("The thickness must be greater than zero [lengh].")
        if not(G > Q_(0, "MPa")): raise ValueError("The shear modulus must be greater than zero [pressure].")
        return cls(t,G=G)

    @property
    def temperature(self):
        """Get the temperature

        Returns
        -------
        Quantity [temperature]

        Raises
        ------
        ValueError
            If no product table is provided.
        """
        if self.G_table is None: raise ValueError("No product table provided. Static case being used.")
        return self._temperature

    @temperature.setter
    @ureg.check(None,'[temperature]')
    def temperature(self,value):
        """Set the temperature

        Parameters
        ----------
        value : Quantity [temperature]
            New temperature value

        Raises
        ------
        ValueError
            If no product table is provided.
        """
        if self.G_table is None: raise ValueError("No product table provided. Static case being used.")
        self._temperature = value

    @property
    def duration(self):
        """Get the duration

        Returns
        -------
        Quantity [time]

        Raises
        ------
        ValueError
            If no product table is provided.
        """
        if self.G_table is None: raise ValueError("No product table provided. Static case being used.")
        return self._duration

    @duration.setter
    @ureg.check(None,'[time]') 
    def duration(self,value):
        """Set the duration

        Parameters
        ----------
        value : Quantity [time]
            New duration value

        Raises
        ------
        ValueError
            If no product table is provided.
        """
        if self.G_table is None: raise ValueError("No product table provided. Static case being used.")
        self._duration = value
        
    @property
    def G(self):
        """Get the shear modulus. Interpolates linearly within the domain of the provided table.

        Returns
        -------
        Quantity [pressure]
            The shear modulus

        Raises
        ------
        ValueError
            If a product table is being used and the reference temperature and/or duration are not set.
        """        
        if self._G is not None:
            return self._G
        else:
            try:
                return self.G_table[self.temperature, self.duration]
            except KeyError:
                if self.temperature is None or self.duration is None: raise ValueError("Reference temperature and/or duration not test.")
                return self.G_interp_dim(self.temperature, self.duration)[0]

_interLayer_registry = {}
def register_interlayer_product(product_name, data):
    """Register new interlayer product table.

    Parameters
    ----------
    product_name : str
        String identifier
    data : Dict( Tuple(Quanity['temperature'], Quanity['time']), Quanity['pressure'])
        The tabulated data of the shear modulus that depends on temperature and load duration.

    Raises
    ------
    ValueError
        If the provided data table is not rectangular. E.g. if shear modulus values are given for 
        (20degC, 3s) and (30degC, 10min), then values for (30degC, 3s) and (20degC, 10min) must also 
        be provided.
    """
    G_table_tmp = set([ii[0].to("degC").magnitude for ii in data.keys()])
    G_table_dur = set([ii[1].to("sec").magnitude for ii in data.keys()])
    G_table_val = list(data.values())
    # check that the provided data is "rectangular"
    if len(G_table_tmp) * len(G_table_dur) != len(G_table_val):
        raise ValueError("The provided data is not rectangular.")
    _interLayer_registry[product_name] = data 

__name_II = "Ionoplast Interlayer NCSEA"
__data_II = {
    (Q_(10,"degC"), Q_(1,'sec')) : Q_(240, "MPa"),
    (Q_(20,"degC"), Q_(1,'sec')) : Q_(217, "MPa"),
    (Q_(24,"degC"), Q_(1,'sec')) : Q_(200, "MPa"),
    (Q_(30,"degC"), Q_(1,'sec')) : Q_(151, "MPa"),
    (Q_(40,"degC"), Q_(1,'sec')) : Q_(77.0, "MPa"),
    (Q_(50,"degC"), Q_(1,'sec')) : Q_(36.2, "MPa"),
    (Q_(60,"degC"), Q_(1,'sec')) : Q_(11.8, "MPa"),
    (Q_(70,"degC"), Q_(1,'sec')) : Q_(3.77, "MPa"),
    (Q_(80,"degC"), Q_(1,'sec')) : Q_(1.55, "MPa"),

    (Q_(10,"degC"), Q_(3,'sec')) : Q_(236, "MPa"),
    (Q_(20,"degC"), Q_(3,'sec')) : Q_(211, "MPa"),
    (Q_(24,"degC"), Q_(3,'sec')) : Q_(193, "MPa"),
    (Q_(30,"degC"), Q_(3,'sec')) : Q_(141, "MPa"),
    (Q_(40,"degC"), Q_(3,'sec')) : Q_(63.0, "MPa"),
    (Q_(50,"degC"), Q_(3,'sec')) : Q_(26.4, "MPa"),
    (Q_(60,"degC"), Q_(3,'sec')) : Q_(8.18, "MPa"),
    (Q_(70,"degC"), Q_(3,'sec')) : Q_(2.93, "MPa"),
    (Q_(80,"degC"), Q_(3,'sec')) : Q_(1.32, "MPa"),

    (Q_(10,"degC"), Q_(1,'min')) : Q_(225, "MPa"),
    (Q_(20,"degC"), Q_(1,'min')) : Q_(195, "MPa"),
    (Q_(24,"degC"), Q_(1,'min')) : Q_(173, "MPa"),
    (Q_(30,"degC"), Q_(1,'min')) : Q_(110, "MPa"),
    (Q_(40,"degC"), Q_(1,'min')) : Q_(30.7, "MPa"),
    (Q_(50,"degC"), Q_(1,'min')) : Q_(11.3, "MPa"),
    (Q_(60,"degC"), Q_(1,'min')) : Q_(3.64, "MPa"),
    (Q_(70,"degC"), Q_(1,'min')) : Q_(1.88, "MPa"),
    (Q_(80,"degC"), Q_(1,'min')) : Q_(0.83, "MPa"),

    (Q_(10,"degC"), Q_(1,'hour')) : Q_(206, "MPa"),
    (Q_(20,"degC"), Q_(1,'hour')) : Q_(169, "MPa"),
    (Q_(24,"degC"), Q_(1,'hour')) : Q_(142, "MPa"),
    (Q_(30,"degC"), Q_(1,'hour')) : Q_(59.9, "MPa"),
    (Q_(40,"degC"), Q_(1,'hour')) : Q_(9.28, "MPa"),
    (Q_(50,"degC"), Q_(1,'hour')) : Q_(4.20, "MPa"),
    (Q_(60,"degC"), Q_(1,'hour')) : Q_(1.70, "MPa"),
    (Q_(70,"degC"), Q_(1,'hour')) : Q_(0.84, "MPa"),
    (Q_(80,"degC"), Q_(1,'hour')) : Q_(0.32, "MPa"),

    (Q_(10,"degC"), Q_(1,'day')) : Q_(190, "MPa"),
    (Q_(20,"degC"), Q_(1,'day')) : Q_(146, "MPa"),
    (Q_(24,"degC"), Q_(1,'day')) : Q_(111, "MPa"),
    (Q_(30,"degC"), Q_(1,'day')) : Q_(49.7, "MPa"),
    (Q_(40,"degC"), Q_(1,'day')) : Q_(4.54, "MPa"),
    (Q_(50,"degC"), Q_(1,'day')) : Q_(2.82, "MPa"),
    (Q_(60,"degC"), Q_(1,'day')) : Q_(1.29, "MPa"),
    (Q_(70,"degC"), Q_(1,'day')) : Q_(0.59, "MPa"),
    (Q_(80,"degC"), Q_(1,'day')) : Q_(0.25, "MPa"),

    (Q_(10,"degC"), Q_(1,'month')) : Q_(171, "MPa"),
    (Q_(20,"degC"), Q_(1,'month')) : Q_(112, "MPa"),
    (Q_(24,"degC"), Q_(1,'month')) : Q_(73.2, "MPa"),
    (Q_(30,"degC"), Q_(1,'month')) : Q_(11.6, "MPa"),
    (Q_(40,"degC"), Q_(1,'month')) : Q_(3.29, "MPa"),
    (Q_(50,"degC"), Q_(1,'month')) : Q_(2.18, "MPa"),
    (Q_(60,"degC"), Q_(1,'month')) : Q_(1.08, "MPa"),
    (Q_(70,"degC"), Q_(1,'month')) : Q_(0.48, "MPa"),
    (Q_(80,"degC"), Q_(1,'month')) : Q_(0.21, "MPa"),

    (Q_(10,"degC"), Q_(10,'year')) : Q_(153, "MPa"),
    (Q_(20,"degC"), Q_(10,'year')) : Q_(86.6, "MPa"),
    (Q_(24,"degC"), Q_(10,'year')) : Q_(26.0, "MPa"),
    (Q_(30,"degC"), Q_(10,'year')) : Q_(5.31, "MPa"),
    (Q_(40,"degC"), Q_(10,'year')) : Q_(2.95, "MPa"),
    (Q_(50,"degC"), Q_(10,'year')) : Q_(2.00, "MPa"),
    (Q_(60,"degC"), Q_(10,'year')) : Q_(0.97, "MPa"),
    (Q_(70,"degC"), Q_(10,'year')) : Q_(0.45, "MPa"),
    (Q_(80,"degC"), Q_(10,'year')) : Q_(0.18, "MPa")
}

register_interlayer_product(__name_II, __data_II)

__name_PVB = "PVB NCSEA"
__data_PVB = {
    (Q_(20,"degC"), Q_(3,'sec')) : Q_(8.060, "MPa"),
    (Q_(30,"degC"), Q_(3,'sec')) : Q_(0.971, "MPa"),
    (Q_(40,"degC"), Q_(3,'sec')) : Q_(0.610, "MPa"),
    (Q_(50,"degC"), Q_(3,'sec')) : Q_(0.440, "MPa"),

    (Q_(20,"degC"), Q_(1,'min')) : Q_(1.640, "MPa"),
    (Q_(30,"degC"), Q_(1,'min')) : Q_(0.753, "MPa"),
    (Q_(40,"degC"), Q_(1,'min')) : Q_(0.455, "MPa"),
    (Q_(50,"degC"), Q_(1,'min')) : Q_(0.290, "MPa"),

    (Q_(20,"degC"), Q_(1,'hour')) : Q_(0.840, "MPa"),
    (Q_(30,"degC"), Q_(1,'hour')) : Q_(0.441, "MPa"),
    (Q_(40,"degC"), Q_(1,'hour')) : Q_(0.234, "MPa"),
    (Q_(50,"degC"), Q_(1,'hour')) : Q_(0.052, "MPa"),

    (Q_(20,"degC"), Q_(1,'day')) : Q_(0.508, "MPa"),
    (Q_(30,"degC"), Q_(1,'day')) : Q_(0.281, "MPa"),
    (Q_(40,"degC"), Q_(1,'day')) : Q_(0.234, "MPa"),
    (Q_(50,"degC"), Q_(1,'day')) : Q_(0.052, "MPa"),

    (Q_(20,"degC"), Q_(1,'month')) : Q_(0.372, "MPa"),
    (Q_(30,"degC"), Q_(1,'month')) : Q_(0.069, "MPa"),
    (Q_(40,"degC"), Q_(1,'month')) : Q_(0.052, "MPa"),
    (Q_(50,"degC"), Q_(1,'month')) : Q_(0.052, "MPa"),

    (Q_(20,"degC"), Q_(1,'year')) : Q_(0.266, "MPa"),
    (Q_(30,"degC"), Q_(1,'year')) : Q_(0.052, "MPa"),
    (Q_(40,"degC"), Q_(1,'year')) : Q_(0.052, "MPa"),
    (Q_(50,"degC"), Q_(1,'year')) : Q_(0.052, "MPa")
}

register_interlayer_product(__name_PVB, __data_PVB)