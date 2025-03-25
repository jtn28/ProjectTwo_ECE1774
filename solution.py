import numpy as np
from bus import Bus
from settings import Settings

class Solution:
    # implementing Power Injection


    def __init__(self, ybus, voltages, buses):
        """
        Initializes the solution verification with system data.

        Parameters:
        ybus (ndarray): System admittance matrix (NxN complex array).
        voltages (ndarray): Voltage magnitudes and angles in complex form (Nx1 array).
        buses (list): List of Bus objects.
        """
        self.ybus = ybus
        self.voltages = voltages
        self.buses = buses  # Ensure buses are indexed correctly


