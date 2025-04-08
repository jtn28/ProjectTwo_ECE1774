import numpy as np

class Settings:
    frequency = 60
    base_power = 100e6
    Sbase = 100
    def __init__(self, frequency:float = 60, base_power:float = 100e6, sbase:float = 100):
        """
        Defines global values for use in other locations of the code
        Parameters:
            frequency(float): Defines the frequency at which the code is based
            base_power(float): Defines the power at which the code is based in watts
            sbase(float): Defines the base power at which the code is based in megawatts
        """
        Settings.frequency = frequency
        Settings.base_power = base_power
        Settings.Sbase = sbase
