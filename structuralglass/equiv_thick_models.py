import abc
import itertools
from . import ureg, Q_
from .layers import GlassPly, InterLayer

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
    def __init__(self, E, ply):
        """
            Args:
                ply (List[GlassPly and InterLayer]): The list of glass layers and interlayers that form a laminate.
        """
        self.h_efw = None
        self.h_efs = None
        self.E = E
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

        # check the elastic modulus of all plys is the same
        set_E = set([ii.E for ii in plys])
        if len(set_E) != 1: raise ValueError("The plys must have the same elastic modulus.")
        E = list(set_E)[0]

        super(MonolithicMethod, self).__init__(E, plys)
        self.calcEquivThickness()

    def calcEquivThickness(self):
        """
            Method that calculates the effective thicknesses.
        """
        self.h_efw = sum((ii.t_min for ii in self.ply))
        self.h_efs = dict(zip(self.ply,itertools.repeat(self.h_efw,len(self.ply))))

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

        # check the elastic modulus of all plys is the same
        set_E = set([ii.E for ii in plys])
        if len(set_E) != 1: raise ValueError("The plys must have the same elastic modulus.")
        E = list(set_E)[0]

        super(NonCompositeMethod, self).__init__(plys)
        self.calcEquivThickness()

    def calcEquivThickness(self):
        """
            Method that calculates the effective thicknesses.
        """
        func = lambda n: sum(ii.t_min**n for ii in self.ply)**(1/n)
        self.h_efs = dict(zip(self.ply, itertools.repeat(func(2),len(self.ply))))
        self.h_efw = func(3)

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

        # check the elastic modulus of all plys is the same
        set_E =set([plys[0].E, plys[2].E])
        if len(set_E) != 1: raise ValueError("The plys must have the same elastic modulus.")
        E = list(set_E)[0]

        super(ShearTransferCoefMethod, self).__init__(E,plys)
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
        self.h_efs = {}
        self.h_efs [self.ply[0]] = (self.h_efw**3/(h_1+2*self.Gamma*h_s2))**(0.5)
        self.h_efs [self.ply[2]] = (self.h_efw**3/(h_2+2*self.Gamma*h_s1))**(0.5)



