import abc
import pint

# Create the default pint unit registary
ureg = pint.UnitRegistry()
# Add custom units here for this project
# Add psf
ureg.define('pound_force_per_square_foot = pound * gravity / foot ** 2 = psf')

# Lookup for nominal thickness to minimal allowable thickness
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
    def from_nominal_thickness(cls, t_nom, glassType):
        try:
            t_min = t_min_lookup_metric[t_nom.to(ureg.mm).magnitude] * ureg.mm
        except KeyError:
            try:
                t_min = t_min_lookup_imperial[t_nom.to(ureg.in).magnitude] * ureg.mm
            except KeyError:
                raise ValueError("Could not find the nominal tickness of {0} in the nominal thickness lookup.".format(t_nom))
        except AttributeError:
            raise ValueError("The nominal thickness must be defined in pint length units. {0} provided.".format(type(t_nom)))
        except pint.DimensionalityError:
            raise ValueError("The nominal thickness must be defined in pint length units. {0} provided.".format(t_nom.dimensionality))
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

class GlassLiteEquiv:
    """
        An abstract class to represent the mechanical behavior of a liminate.
        Unique formulations of the mechanical behaviour are derived from this class.

        ...

        Attributes
        ----------
        ply: List[GlassPly and InterLayer (optional)]
            The list of glass layers and interlayers that form a laminate.
        h_efw : Quantity [length]
            The equivlant laminate thickness for displacement.
        h_efs : Dict[GlassPly, Quantity [length]]
            The equivlant laminate thickness for the stress in the associated ply.
        Methods
        -------
        __init__(plys):
            Constructor for a liminate's behaviour.
        calcEquivThickness()
            Abstract method that sets h_efw and h_efs for that formulation.
    """
    __metaclass__ = abc.ABCMeta
    def __init__(self, ply):
        """
            Args:
                ply (List[GlassPly and InterLayer]): The list of glass layers and interlayers that form a laminate.
        """
        self.h_efw = 0.0 * ureg.mm
        self.h_efs = {}
        self.ply = ply

    @abc.abstractmethod
    def calcEquivThickness(self):
        """
            Abstract method to determine the equivalent thicknesses
        """
        return

class MonolithicMethod(GlassLiteEquiv):
    """
        A basic/naive mechanical behavior that assumes the laminates effective thickness is the sum of the nominal ply thicknesses.
        This assumption applies to both stress and deflection effective thickness.
        This models validity decreases with load duration.

        ...

        Attributes
        ----------
        ply: List[GlassPly]
            The list of glass layers that form a laminate.
        h_efw : Quantity [length]
            The equivlant laminate thickness for displacement.
        h_efs : Dict[GlassPly, Quantity [length]]
            The equivlant laminate thickness for the stress in the associated ply.
        Methods
        -------
        __init__(plys):
            Constructor for a liminate's behaviour.
        calcEquivThickness()
            Method that sets h_efw and h_efs for this formulation.
    """
    def __init__(self, plys):
        """
            Constructor for a liminate's behaviour.

            Args:
                plys (List[GlassPly]): The list of glass layers that form a laminate.
        """
        super(MonolithicMethod, self).__init__(plys)
        self.calcEquivThickness()

    def calcEquivThickness(self):
        """
            Method that calculates the effective thicknesses.
        """
        tmp = sum((ii.t_min for ii in self.ply))
        self.h_efw = tmp
        for ii in self.ply:
            self.h_efs[ii] = tmp

class NonCompositeMethod(GlassLiteEquiv):
    """
        A simple mechanical behavior that assumes the laminates effective thickness is:
            * for deflection: the square root of the nominal thicknesses squared
            * for stress: the cubed root of the nominal thicknesses cubed
        This models assumes a non-composite behavior.

        ...

        Attributes
        ----------
        ply: List[GlassPly]
            The list of glass layers that form a laminate.
        h_efw : Quantity [length]
            The equivlant laminate thickness for displacement.
        h_efs : Dict[GlassPly, Quantity [length]]
            The equivlant laminate thickness for the stress in the associated ply.
        Methods
        -------
        __init__(plys):
            Constructor for a liminate's behaviour.
        calcEquivThickness()
            Method that sets h_efw and h_efs for this formulation.
    """
    def __init__(self, plys):
        """
            Constructor for a liminate's behaviour.

            Args:
                plys (List[GlassPly]): The list of glass layers that form a laminate.
        """
        super(NonCompositeMethod, self).__init__(plys)
        self.calcEquivThickness()

    def calcEquivThickness(self):
        """
            Method that calculates the effective thicknesses.
        """
        tmp1 = 0.0 * (ureg.mm)**2
        tmp2 = 0.0 * (ureg.mm)**3
        for ii in self.ply:
            tmp1 += (ii.t_min)**2
            tmp2 += (ii.t_min)**3
        tmp3 = tmp1**(0.5)
        for ii in self.ply:
            self.h_efs[ii] = tmp3
        self.h_efw = tmp2**(1/3.0)

class ShearTransferCoefMethod(GlassLiteEquiv):
    """
        A mechanical behavior that takes the shear modulus of the laminate into consideration.
        This method was originally proposed by Bennison-Wolfel and referenced in ASTM E1300.
        It is only valid for a two glass ply laminate.
        Ref literature for limitations.

        ...

        Attributes
        ----------
        ply: List[GlassPly and InterLayer]
            The list of glass layers and InterLayers that form a laminate.
        h_efw : Quantity [length]
            The equivlant laminate thickness for displacement.
        h_efs : Dict[GlassPly, Quantity [length]]
            The equivlant laminate thickness for the stress in the associated ply.
        Methods
        -------
        __init__(plys):
            Constructor for a liminate's behaviour.
        calcEquivThickness():
            Method that sets h_efw and h_efs for this formulation.
        validlite(plys):
            Method that validates that the laminate does not violate the models limitations (in terms of number of layers and layer types).
    """
    beta = 9.6
    def __init__(self, plys, a):
        """
            Constructor for a liminate's behaviour.

            Args:
                plys (List[GlassPly and InterLayer]): The list of glass layers and InterLayers that form a laminate.
                a (Quantity [length]): Minimum dimension of the rectangular panel
        """
        assert self.validlite(plys), "Method is only valid for 2 ply glass laminates"
        super(ShearTransferCoefMethod, self).__init__(plys)
        self.panelMinLen = a
        self.calcEquivThickness()

    def validlite(self, plys):
        if len(plys)==3:
            if isinstance(plys[0],GlassPly):
                if isinstance(plys[2],GlassPly):
                    if isinstance(plys[1],InterLayer):
                        return True
        return False

    def calcEquivThickness(self):
        """
            Method that calculates the effective thicknesses.
        """
        h_1 = self.ply[0].t_min
        h_2 = self.ply[2].t_min
        h_v = self.ply[1].t
        G_interlayer = self.ply[1].G
        E_glass = self.ply[0].E
        h_s = 0.5*(h_1 + h_2)+h_v
        h_s1 = h_s*h_1/(h_1+h_2)
        h_s2 = h_s*h_2/(h_1+h_2)
        I_s = h_1*h_s2**2 + h_2*h_s1**2
        self.Gamma = 1.0 / (1.0 + self.beta*E_glass*I_s*h_v / (G_interlayer * h_s**2 * self.panelMinLen**2))
        self.h_efw = (h_1**3 + h_2**3 + 12*self.Gamma*I_s)**(1/3.0)
        self.h_efs [self.ply[0]] = (self.h_efw**3/(h_1+2*self.Gamma*h_s2))**(0.5)
        self.h_efs [self.ply[2]] = (self.h_efw**3/(h_2+2*self.Gamma*h_s1))**(0.5)

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
    def __init__(self, ratio):
        """
            Args:
                ratio (float): the ratio of the largest dimension to the smallest dimension (rectangular panel)
        """
        r = [1, 1.2, 1.4, 1.6, 1.8, 2, 3, 4, 5]
        beta = [0.2874, 0.3762, 0.453, 0.5172, 0.5688, 0.6102, 0.7134, 0.741, 0.7476, 0.75]
        alpha = [0.044, 0.0616, 0.077, 0.0906, 0.1017, 0.111, 0.1335, 0.14, 0.1417, 0.1421]
        gamma = [0.42, 0.455, 0.478, 0.491, 0.499, 0.503, 0.505, 0.502, 0.501, 0.5]
        if ratio>5:
            self.beta = beta[-1]
            self.alpha = alpha[-1]
            self.gamma = gamma[-1]
        else:
            a = list(filter(lambda x: x <= ratio, r))[-1]
            index_a = r.index(a)
            b = list(filter(lambda x: x >= ratio, r))[0]
            index_b = r.index(b)
            t = (ratio-a)/(b-a) if a!=b else 0
            self.beta = beta[index_a]+t*(beta[index_b]-beta[index_a])
            self.alpha = alpha[index_a]+t*(alpha[index_b]-alpha[index_a])
            self.gamma = gamma[index_a]+t*(gamma[index_b]-gamma[index_a])

class GlassPanel:
    """
        A class to represent a glass panel, its dimensions, buildup and windload.

        ...

        Attributes
        ----------
        windLoad : Quantity [pressure]
            The wind load on the panel.
        buildup : List[GlassLiteEquiv]
            The buildup
        a : Quantity [length]
            The larger dimention.
        b : Quantity [length]
            The smaller dimention.
        LSF : Quantity [dimensionless]
            The load share factor for each package.
        stress : Dict[GlassPly, Quantity [pressure]]
            The stress in each ply.
        deflection : Dict[GlassLiteEquiv, Quantity [pressure]]
            The deflection of each package.

        Methods
        -------
        __init__(width, height, buildup, windLoad):
            Constructor for a panels aspect ratio.
    """
    def __init__(self, width, height, buildup, windLoad):
        # Check that the list unique instances and that only a single type of effective thickness model is used.
        assert len(buildup) == len(set(buildup)), "The buildup must contain unique objects, use deep copy."
        assert len(set(map(lambda x: type(x), buildup)))==1, "Mixing of effective thickness models. Only one model should be used."
        self.windLoad = windLoad
        self.buildup = buildup
        if width<height:
            self.a, self.b = height, width
        else:
            self.b, self.a = height, width

        E_glass = 72 * ureg.GPa
        r4s = Roarks4side((self.a/self.b).magnitude)

        # Determine the load share factor
        s = map(lambda x: (x.h_efw)**3 , self.buildup)
        s = sum(s)
        self.LSF = dict(zip(self.buildup,map(lambda x: x.h_efw**3/s , self.buildup)))

        self.stress = {}
        self.deflection = {}
        for lite in self.buildup:
            for ply, h_efs in lite.h_efs.items():
                self.stress[ply] = (r4s.beta * self.windLoad * self.LSF[lite] * self.b**2 / (h_efs**2)).to('MPa')

            self.deflection[lite] =(r4s.alpha * self.windLoad * self.LSF[lite] * self.b**4 / (E_glass * lite.h_efw**3)).to('mm') 
