import numpy as np
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

    # Placeholders for later
    #def calculate_zpu(self):
    #    return series_impedance / (Vbase**2/Sbase)

    #def calculate_ypu
    #    return shunt_admittance / (Sbase/Vbase**2)

    def calculate_admittance_matrix(self):
        Y11 = self.shunt_admittance / 2 + 1 / self.series_impedance
        Y12 = -1 / self.series_impedance
        Y21 = Y12
        Y22 = Y11
        return [[Y11, Y12], [Y21, Y22]]

if __name__ == '__main__':
    # Running a test transmission line
    Bus1 = Bus("Bus1", 20)
    Bus2 = Bus("Bus2", 230)
    cardinal = Conductor("Cardinal", 1.196 / 12, 0.0403, 0.1128, 1010)
    test_bundle = Bundle('test_bundle', 2, 3, cardinal)
    test_geometry = Geometry("test_bundle", 0, 0, 18.5, 0, 37, 0)
    test_line = TransmissionLine('test_line', Bus1, Bus2, test_bundle, test_geometry, 100)
    impedance = test_line.calculate_impedance()
    admittance = test_line.calculate_admittance()
    matrix = test_line.calculate_admittance_matrix()
    print(f'impedance: {impedance:.4f}, admittance: {admittance}, matrix: {matrix}')