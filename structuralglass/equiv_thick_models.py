import abc
import itertools

from numpy.lib.function_base import place
from . import ureg, Q_
from .layers import GlassPly, InterLayer

class GlassLiteEquiv:
    """
    An abstract class to represent the mechanical behavior of a liminate.
    Unique formulations of the mechanical behaviour are derived from this class.

    Attributes
    ----------
    ply: List[GlassPly and InterLayer (optional)]
        The list of glass layers and interlayers that form a laminate.
    h_efw : Quantity [length]
        The equivalent laminate thickness for displacement.
    h_efs : Dict[GlassPly, Quantity [length]]
        The equivalent laminate thickness for the stress in the associated ply.
    E: Quantity [pressure]
        The elastic modulus for the formulation.
    
    Methods
    -------
    _calc_equiv_thickness()
        Abstract method that sets h_efw and h_efs for that formulation.
    _validate(plys)
        Abstract method to validate the plys based on the requirements of the formulation.
    _determine_package_E()
        Abstract method to determine the elastic modulus for the formulation.
    """
    __metaclass__ = abc.ABCMeta
    def __init__(self, ply):
        """[summary]

        Parameters
        ----------
        ply : ply (List[GlassPly and/or InterLayer])
            The list of glass layers and interlayers that form a laminate.
        """
        self._h_efw = None
        self._h_efs = None
        self._E = None
        self.ply = ply

    @abc.abstractmethod
    def _calc_equiv_thickness(self):
        """Abstract method to determine the equivalent thicknesses.
        """
        return

    @abc.abstractmethod
    def _validate(self, plys):
        """Abstract method to valadate the plys.

        Parameters
        ----------
        plys : List[GlassPly and InterLayer (optional)]
        
        Returns
        -------
        Tuple (bool, msg)
            True for a valid formulation. A mesage for an error.
        """
        return 

    @abc.abstractmethod
    def _determine_package_E(self):
        """Abstract method to determine the packages elastic modulus.
        """
        return

    @property
    def h_efw(self):
        """Get the equivalent laminate thickness for displacement.

        Returns
        -------
        Quantity [length]
        """
        return self._h_efw

    @property
    def h_efs(self):
        """Get the equivalent laminate thickness for the stress in the associated ply.

        Returns
        -------
        Dict[GlassPly, Quantity [length]]
        """
        return self._h_efs

    @property
    def ply(self):
        """Get the list of glass layers and interlayers that form a laminate.

        Returns
        -------
        List[GlassPly and/or InterLayer]
        """
        return self._ply

    @property
    def E(self):
        """Get the elastic modulus for the formulation.

        Returns
        -------
        Quantity [pressure]
        """
        return self._E

    @ply.setter
    def ply(self, value):
        """Set the list of glass layers and interlayers that form a laminate.

        Parameters
        ----------
        value : List[GlassPly and InterLayer (optional)]

        Raises
        ------
        ValueError
            If the provided list fails the formulations validation function.
        """
        valid, msg = self._validate(value)
        if not valid: raise ValueError(f"Ply validation failed: {msg}")
        self._ply = value
        self._determine_package_E()
        self._calc_equiv_thickness()

class MonolithicMethod(GlassLiteEquiv):
    """
    A basic/naive mechanical behavior that assumes the laminates effective thickness is the sum of the plys minimum thicknesses.
    This assumption applies to both stress and deflection effective thickness.
    This models validity decreases with load duration.

    Attributes
    ----------
    ply: List[GlassPly]
        The list of glass layers that form a laminate.
    h_efw : Quantity [length]
        The equivlant laminate thickness for displacement.
    h_efs : Dict[GlassPly, Quantity [length]]
        The equivlant laminate thickness for the stress in the associated ply.
    E: Quantity [pressure]
        The elastic modulus for the formulation.
    """
    def __init__(self, plys):
        """Constructor for a liminate's behaviour.

        Parameters
        ----------
        plys : List[GlassPly]
            The list of glass layers that form a laminate.
        """
        super(MonolithicMethod, self).__init__(plys)

    def _calc_equiv_thickness(self):
        """Method that calculates the effective thicknesses.
        The sum of the plys minimum thicknesses is used.
        """
        self._h_efw = sum((ii.t_min for ii in self._ply))
        self._h_efs = dict(zip(self._ply,itertools.repeat(self.h_efw,len(self._ply))))

    def _determine_package_E(self):
        """Method to determine the elastic modulus for the formulation. 
        As the validation function is already checks the elastic modulus 
        of all GlassPly are the same, take the 1st plys elastic modulus.
        """
        self._E = self.ply[0].E

    def _validate(self, plys):
        """Method that validates the data in the plys.

        1. Checks the list is only contains type GlassPly
        2. Checks the elastic modulus of all GlassPly are the same.

        Parameters
        ----------
        plys : List

        Returns
        -------
        Tuple (bool, str)
            True for a valid formulation. A mesage for an error.
        """
        msg = ""
        valid = all((isinstance(ii,GlassPly) for ii in plys))
        if valid:
            set_E = set([ii.E for ii in plys])
            valid = len(set_E) == 1
            if not valid:
                msg = "The plys must have the same elastic modulus." if not valid else ""
        else:
            msg = "Method is only formulated for a list of GlassPly."        
        return valid, msg

class NonCompositeMethod(GlassLiteEquiv):
    """
    A simple mechanical behavior that assumes the laminates effective thickness is:
        * for deflection: the square root of the minimum thicknesses squared
        * for stress: the cubed root of the minimum thicknesses cubed
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
    E: Quantity [pressure]
        The elastic modulus for the formulation.

    Methods
    -------
    __init__(plys):
        Constructor for a liminate's behaviour.
    calcEquivThickness()
        Method that sets h_efw and h_efs for this formulation.
    """
    def __init__(self, plys):
        """Constructor for a liminate's behaviour.

        Parameters
        ----------
        plys : List[GlassPly]
            The list of glass layers that form a laminate.
        """
        super(NonCompositeMethod, self).__init__(plys)

    def _calc_equiv_thickness(self):
        """Method that calculates the effective thicknesses. 
        The laminates effective thickness is:
            * for deflection: the square root of the minimum thicknesses squared
            * for stress: the cubed root of the minimum thicknesses cubed
        """
        func = lambda n: sum(ii.t_min**n for ii in self.ply)**(1/n)
        self._h_efs = dict(zip(self.ply, itertools.repeat(func(2),len(self.ply))))
        self._h_efw = func(3)

    def _determine_package_E(self):
        """Method to determine the elastic modulus for the formulation. 
        As the validation function is already checks the elastic modulus 
        of all GlassPly are the same, take the 1st plys elastic modulus.
        """
        self._E = self.ply[0].E

    def _validate(self, plys):
        """Method that validates the data in the plys.

        1. Checks the list is only contains type GlassPly
        2. Checks the elastic modulus of all GlassPly are the same.

        Parameters
        ----------
        plys : List

        Returns
        -------
        Tuple (bool, str)
            True for a valid formulation. A mesage for an error.
        """
        msg = ""
        valid = all((isinstance(ii,GlassPly) for ii in plys))
        if valid:
            set_E = set([ii.E for ii in plys])
            valid = len(set_E) == 1
            if not valid:
                msg = "The plys must have the same elastic modulus." if not valid else ""
        else:
            msg = "Method is only formulated for a list of GlassPly."        
        return valid, msg
        
class ShearTransferCoefMethod(GlassLiteEquiv):
    """
    A mechanical behavior that takes the shear modulus of the laminate into consideration.
    This method was originally proposed by Bennison-Wolfel and referenced in ASTM E1300.
    It is only valid for a two glass ply laminate.
    Ref literature for limitations.

    Attributes
    ----------
    ply: List[GlassPly and InterLayer]
        The list of glass layers and InterLayers that form a laminate.
    h_efw : Quantity [length]
        The equivlant laminate thickness for displacement.
    h_efs : Dict[GlassPly, Quantity [length]]
        The equivlant laminate thickness for the stress in the associated ply.
    beta: float
        A coefficient  dependent  on  the  boundary  and  loading  conditions. 
    panel_min_dim: Quantity [length]
        Minimum dimension of the rectangular panel
    
    Methods
    -------
    calcEquivThickness():
        Method that sets h_efw and h_efs for this formulation.
    validlite(plys):
        Method that validates that the laminate does not violate the models limitations (in terms of number of layers and layer types).
    """
    def __init__(self, plys, panel_min_dim):
        """Constructor for a liminate's behaviour.

        Parameters
        ----------
        plys : List[GlassPly and InterLayer]
            The list of glass layers and InterLayers that form a laminate.
        panel_min_dim : Quantity [length]
            Minimum dimension of the rectangular panel
        """        
        self.panel_min_dim = panel_min_dim
        self.beta = 9.6
        super(ShearTransferCoefMethod, self).__init__(plys)

    def _validate(self, plys):
        """Method that validates the data in the plys.
        
        1. This formulation is only valid for plys with that are 
        [GlassPly, Interlayer, GlassPly].
        2: The GlassPly's must have the same elastic modulus.

        

        Parameters
        ----------
        plys : List
            The list to be validated.

        Returns
        -------
        Tuple (bool, str)
            True for a valid formulation. A mesage for an error.
        """
        valid, msg = False, ""
        if len(plys)==3:
            if isinstance(plys[0],GlassPly):
                if isinstance(plys[2],GlassPly):
                    if isinstance(plys[1],InterLayer):
                        valid = True
        if valid:
            set_E =set([plys[0].E, plys[2].E])
            if len(set_E) != 1:
                msg = "The plys must have the same elastic modulus."
        else:
            msg = "Method is only valid a list of [GlassPly, Interlayer, GlassPly]."
        return valid, msg

    def _calc_equiv_thickness(self):
        """Method that calculates the effective thicknesses.
        This method was originally proposed by Bennison-Wolfel and referenced in ASTM E1300.
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
        self.Gamma = 1.0 / (1.0 + self.beta*E_glass*I_s*h_v / (G_interlayer * h_s**2 * self.panel_min_dim**2))
        self._h_efw = (h_1**3 + h_2**3 + 12*self.Gamma*I_s)**(1/3.0)
        self._h_efs = {}
        self._h_efs [self.ply[0]] = (self.h_efw**3/(h_1+2*self.Gamma*h_s2))**(0.5)
        self._h_efs [self.ply[2]] = (self.h_efw**3/(h_2+2*self.Gamma*h_s1))**(0.5)
    
    def _determine_package_E(self):      
        """Method to determine the elastic modulus for the formulation. 
        As the validation function is already checks the elastic modulus 
        of all GlassPly are the same, take the 1st plys elastic modulus.
        """
        self._E = self.ply[0].E

    @property
    def beta(self):
        """Get the beta value of the formulation. 
        A coefficient  dependent  on  the  boundary  and  loading  conditions. 

        Returns
        -------
        float
        """
        return self._beta

    @beta.setter
    def beta(self,value):
        """Set the beta value of the formulation. 
        A coefficient  dependent  on  the  boundary  and  loading  conditions. 

        Parameters
        ----------
        value : float
        """
        self._beta = value

    @property
    def panel_min_dim(self):
        """Get the minimum dimension of the rectangular panel.

        Returns
        -------
        Quantity [length]
        """
        return self._panel_min_dim
    
    @panel_min_dim.setter
    @ureg.check(None,'[length]')
    def panel_min_dim(self,value):
        """Set the minimum dimension of the rectangular panel.

        Parameters
        ----------
        value : Quantity [length]

        Raises
        ------
        ValueError
            If the minimum panel dimension is less than 0ft.
        """
        if value < Q_(0,"ft"): raise ValueError("The minimum panel dimension must be greater than 0ft")
        self._panel_min_dim = value 
        self._calc_equiv_thickness()
        
