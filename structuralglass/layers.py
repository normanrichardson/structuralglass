from . import ureg, Q_

# Lookup for nominal thickness to minimal allowable thickness in metric
t_min_lookup_metric = {
            2.5: 2.16,
            3  : 2.92,
            4  : 3.78,
            5  : 4.57,
            6  : 5.56,
            8  : 7.42,
            10 : 9.02,
            12: 11.91,
            16: 15.09,
            19: 18.26,
            22: 21.44
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
            0.875  : 21.44
}

class GlassPly:
    """
        A class to represent a glass ply, its thinkess (nominal and minimum allowable) and mechanical properties.

        ...

        Attributes
        ----------
        E : Quantity [pressure]
            Elastic modulus
        t_nom : Quantity [length]
            nominal thickness
        t_min : Quantity [length]
            min allowable thickness
        glassType : str
            Glass type [AN, HS, FT]
        Methods
        -------
        __init__(t_nom, glassType):
            Constructor for a ply with nominal thickness
    """
    def __init__(self, t_min, glassType, t_nom=None):
        """
            Args:
                t_nom (Quantity [length]): nominal thickness
                glassType (str): Glass type [AN, HS, FT]
        """
        self.E = 71.7 * ureg.GPa
        self.t_min = t_min
        self.t_nom = t_nom
        self.glassType = glassType
    
    @classmethod
    @ureg.check(None, '[length]', None)
    def from_nominal_thickness(cls, t_nom, glassType):
        try:
            t_min = t_min_lookup_metric[t_nom.to(ureg.mm).magnitude] * ureg.mm
        except KeyError:
            try:
                t_min = t_min_lookup_imperial[t_nom.to(ureg.inch).magnitude] * ureg.mm
            except KeyError:
                raise ValueError("Could not find the nominal tickness of {0} in the nominal thickness lookup.".format(t_nom))
        return cls(t_min,glassType,t_nom)
    
    @classmethod
    def from_actual_thickness(cls, t_act, glassType):
        return cls(t_act, glassType)

class InterLayer:
    """
        A class to represent a glass interlayer(e.g. PVB or SG), and its mechanical properties. 
        Rate dependent properties are not considered here.

        ...

        Attributes
        ----------
        t : Quantity [length]
            thickness
        G : Quantity [pressure]
            Shear modulus
        Methods
        -------
        __init__(t, G):
            Constructor for an interlayer.
    """
    def __init__(self, t, G):
        """
            Args:
                t (Quantity [length]): thickness
                G (Quantity [pressure]): Shear modulus
        """
        self.t = t
        self.G = G