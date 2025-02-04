import numpy as np
from Bundle import Bundle
from Bus import Bus
from Geometry import Geometry

class TransmissionLine:

    def __init__(self, name:str, bus1:Bus, bus2:Bus, bundle:Bundle, geometry:Geometry, length:float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length
        self.f = 60  # Going to keep this a constant for now, but it can be change later if needed
        self.series_impedance = self.calculate_impedance()
        self.shunt_admittance = self.calculate_admittance()
        self.admittance_matrix = self.calculate_admittance_matrix()

    def calculate_impedance(self):
        # Using equation w*2*10^-7 * log(DEQ/DSL)
        z_imag = 2*np.pi*self.f * 2e-7 * np.log(self.geometry.calc_deq() / self.bundle.calculate_dsl())
        z_imag_full = 1j * z_imag * self.length
        z_real = self.bundle.conductor.resistance * self.length / self.bundle.num_conductors
        return z_real + z_imag_full

    def calculate_admittance(self):
        # Using equation w * 2pi * e0 / log(DEQ/DSC)
        z_admittance = 2*np.pi*self.f * 2 * np.pi * 8.854e-12 / np.log(self.geometry.calc_deq() / self.bundle.calculate_dsc())
        y_shunt = 1j * z_admittance * self.length
        return y_shunt

    # Placeholders for late
    #def calculate_zpu(self):
    #    return Vbase**2/Sbase

    #def calculate_ypu
    #    return Sbase/Vbase**2

    def calculate_admittance_matrix(self):
        Y11 = self.shunt_admittance / 2 + 1 / self.series_impedance
        Y12 = -1 / self.series_impedance
        Y21 = Y12
        Y22 = Y11
        return [[Y11, Y12], [Y21, Y22]]