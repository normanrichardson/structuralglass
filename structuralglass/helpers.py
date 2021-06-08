from scipy import interpolate


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
        r = [1, 1.2, 1.4, 1.6, 1.8, 2, 3, 4, 5, 1e16]
        beta = [0.2874, 0.3762, 0.453, 0.5172, 0.5688, 0.6102, 0.7134, 0.741, 0.7476, 0.75]
        alpha = [0.044, 0.0616, 0.077, 0.0906, 0.1017, 0.111, 0.1335, 0.14, 0.1417, 0.1421]
        gamma = [0.42, 0.455, 0.478, 0.491, 0.499, 0.503, 0.505, 0.502, 0.501, 0.5]


        f_beta = interpolate.interp1d(r, beta)
        f_alpha = interpolate.interp1d(r, alpha)
        f_gamma = interpolate.interp1d(r, gamma)

        
        self.beta = f_beta(ratio)
        self.alpha = f_alpha(ratio)
        self.gamma = f_gamma(ratio)