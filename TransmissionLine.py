import numpy as np
import pandas as pd
from Bundle import Bundle
from Bus import Bus
from Geometry import Geometry
from Conductor import Conductor # Seems to be needed even though reference in Bundle

class TransmissionLine:

    def __init__(self, name:str, bus1:Bus, bus2:Bus, bundle:Bundle, geometry:Geometry, length:float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length
        self.f = 60  # Going to keep this a constant for now, but it can be change later if needed
        self.Vbase = bus1.baseKV * 1000
        self.Sbase = 100e6 # Temporarily, will update for milestone 5
        self.series_impedance = self.calculate_impedance()
        self.shunt_admittance = self.calculate_admittance()
        self.admittance_matrix = self.calculate_admittance_matrix()

    def calculate_impedance(self):
        # Using equation w*2*10^-7 * log(DEQ/DSL)
        z_imag = 2*np.pi*self.f * 2e-7 * np.log(self.geometry.calc_deq() / self.bundle.calculate_dsl())
        z_imag_full = 1j * z_imag * self.length * 1609
        z_real = self.bundle.conductor.resistance * self.length / self.bundle.num_conductors
        return z_real + z_imag_full

    def calculate_admittance(self):
        # Using equation w * 2pi * e0 / log(DEQ/DSC)
        # NEED TO CHECK, WAS GETTING DIFFERENCE FROM PAULO
        b_admittance = 2*np.pi*self.f * 2 * np.pi * 8.854e-12 / np.log(self.geometry.calc_deq() / self.bundle.calculate_dsc())
        y_shunt = 1j * b_admittance * self.length * 1609
        return y_shunt

    #Placeholders for later
    def calculate_zpu(self):
        return self.series_impedance / (self.Vbase**2/self.Sbase)

    def calculate_ypu(self):
        return self.shunt_admittance / (self.Sbase/self.Vbase**2)

    def calculate_admittance_matrix(self):
        Y11 = self.shunt_admittance / 2 + 1 / self.series_impedance
        Y12 = -1 / self.series_impedance
        Y21 = Y12
        Y22 = Y11
        return pd.DataFrame({"Bus1": [Y11, Y12], "Bus2":[Y21, Y22]})

    def calculate_y_prim(self):
        z_pu = self.calculate_zpu()
        y_pu = self.calculate_ypu()

        Y11 = y_pu / 2 + 1 / z_pu
        Y12 = -1 / z_pu
        Y21 = Y12
        Y22 = Y11
        return pd.DataFrame({"Bus1": [Y11, Y12], "Bus2": [Y21, Y22]})

    def __repr__(self):
        return f"TransmissionLine(name={self.name}, Bus1={self.bus1}, Bus2={self.bus2})"

if __name__ == '__main__':
    # Running a test transmission line
    Bus1 = Bus("Bus1", 230)
    Bus2 = Bus("Bus2", 230)
    cardinal = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    test_bundle = Bundle('test_bundle', 2, 1.5, cardinal)
    test_geometry = Geometry("test_bundle", 0, 0, 18.5, 0, 37, 0)
    test_line = TransmissionLine('test_line', Bus1, Bus2, test_bundle, test_geometry, 10)
    impedance = test_line.calculate_impedance()
    admittance = test_line.calculate_admittance()
    matrix = test_line.calculate_admittance_matrix()
    matrix2 = test_line.calculate_y_prim()
    print(f'impedance: {impedance:.4f}, admittance: {admittance}, matrix: \n{matrix2}')