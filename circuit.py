import pandas as pd
import numpy as np
from bus import Bus
from conductor import Conductor
from bundle import Bundle
from geometry import Geometry
from transformer_Class import Transformer
from transmissionLine import TransmissionLine
from generator import Generator
from load import Load

class Circuit:
    def __init__(self, name:str, analysis_mode: str = "Power_Flow", fault_type:str = "SYM", base_mva: float = 100):
        self.name = name
        self.base_mva = base_mva
        self.analysis_mode = analysis_mode
        self.fault_type = fault_type
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.generators = {}
        self.loads = {}


    def add_bus(self, name:str, baseKV:float, vpu:float = 1, delta:float = 0, bus_type:str = 'PQ'):
        bus = Bus(name, baseKV, vpu, delta, bus_type)
        self.buses[bus.name] = bus
        return

    def add_transformer(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float,
                 x_over_r_ratio: float, connection: str, ground1:complex, ground2:complex):
        transformer = Transformer(name, bus1, bus2, power_rating, impedance_percent, x_over_r_ratio, self.base_mva, connection, ground1, ground2)
        instance = (transformer.name, transformer.bus1, transformer.bus2)
        self.transformers[instance] = transformer
        return

    def add_transmission_line(self, name:str, bus1:Bus, bus2:Bus, bundle:Bundle, geometry:Geometry, length:float):
        transmission_line = TransmissionLine(name, bus1, bus2, bundle, geometry, length)
        instance = (transmission_line.name, transmission_line.bus1, transmission_line.bus2)
        self.transmission_lines[instance] = transmission_line
        return


    def add_generator(self, name, bus, voltage_setpoint, mw_setpoint, x0, x1, x2, ground_imp, isGrounded):
        real_pu = mw_setpoint / self.base_mva
        generator = Generator(name, bus, voltage_setpoint, real_pu, x0, x1, x2, ground_imp, isGrounded)
        self.generators[name] = generator
        bus.real_power += real_pu

    # subtract because gen is injection

    def add_load(self, name, bus, mw, mvar):
        # Convert to per unit using base_mva
        real_pu = mw / self.base_mva
        reactive_pu = mvar / self.base_mva
        load = Load(name, bus, real_pu, reactive_pu)
        self.loads[name] = load
        bus.real_power += real_pu
        bus.reactive_power += reactive_pu

    # For Creating the big Y Bus, use a for loop for each element, then grab the y primitive, then add it
    # to the y bus matrix, and keep going, use tags to know how to orient the whole thing
    def calc_ybus(self):
        bus_names = list(self.buses.keys())
        y_bus = pd.DataFrame(0, index=bus_names, columns=bus_names, dtype=complex)
        for item in self.transformers:
            prim = self.transformers[item].calc_y_primitive()
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        for item in self.transmission_lines:
            prim = self.transmission_lines[item].calc_y_primitive()
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        # Currently here to make it easier to debug, remove print statement the final implementation
        #print(y_bus)
        return y_bus
    def calc_ybus_sequence(self, sequence: str = "pos"):
        bus_names = list(self.buses.keys())
        y_bus = pd.DataFrame(0, index=bus_names, columns=bus_names, dtype=complex)
        for item in self.transformers:
            prim = self.transformers[item].calc_y_primitive_sequence(sequence)
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        for item in self.transmission_lines:
            prim = self.transmission_lines[item].calc_y_primitive_sequence(sequence)
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        for item in self.generators:
            prim = self.generators[item].calc_y_primitive_sequence(sequence)
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        if sequence != "zero":
            for item in self.loads:
                S = self.loads[item].real_power + 1j * self.loads[item].reactive_power
                I = np.conjugate(S / self.loads[item].bus.vpu)
                y_bus.loc[self.loads[item].bus.name, self.loads[item].bus.name] += 1/(I/self.loads[item].bus.vpu)
        # Currently here to make it easier to debug, remove print statement the final implementation
        #print(y_bus)
        return y_bus

    def calc_zbus_sequence(self, sequence: str = "pos"):
        bus_names = list(self.buses.keys())
        y_bus = pd.DataFrame(0, index=bus_names, columns=bus_names, dtype=complex)
        for item in self.transformers:
            prim = self.transformers[item].calc_y_primitive_sequence(sequence)
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        for item in self.transmission_lines:
            prim = self.transmission_lines[item].calc_y_primitive_sequence(sequence)
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        for item in self.generators:
            prim = self.generators[item].calc_y_primitive_sequence(sequence)
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        if sequence != "zero":
            for item in self.loads:
                S = self.loads[item].real_power + 1j * self.loads[item].reactive_power
                y_bus.loc[self.loads[item].bus.name, self.loads[item].bus.name] += 1/S
        # Currently here to make it easier to debug, remove print statement the final implementation
        #print(y_bus)
        z_bus_values = np.linalg.inv(y_bus.values)
        z_bus = pd.DataFrame(z_bus_values, index=y_bus.index, columns=y_bus.columns, dtype=complex)
        return z_bus

    def compute_power_injection(self, voltageVector):
        V = voltageVector
        ybus = self.calc_ybus()
        I = ybus.values @ V
        S = V * np.conj(I)

       # print("\n--- Power Injection Check ---")
        #for i, bus_name in enumerate(self.buses):
       #     print(
        #        f"{bus_name}: V = {V[i]:.4f}, I = {I[i]:.4f}, S = {S[i]:.4f} -> P = {S[i].real:.4f}, Q = {S[i].imag:.4f}")

        Px = {bus: S[k].real for k, bus in enumerate(self.buses)}
        Qx = {bus: S[k].imag for k, bus in enumerate(self.buses)}
        return [Px, Qx]

    def compute_power_mismatch(self, voltageVector):
        P_inj, Q_inj = self.compute_power_injection(voltageVector)

        deltaP = []  # ∆P for all non-slack buses (PQ + PV)
        deltaQ = []  # ∆Q only for PQ buses

        for name, bus in self.buses.items():
            if bus.type != 'Slack':
                # Start with load demand (which is negative contribution)
                P_spec = -bus.real_power

                # Add generator contribution if this bus has a generator
                for gen in self.generators.values():
                    if gen.bus.name == name:
                        P_spec += 2*gen.mw_setpoint  # this is in pu already

                deltaP.append(P_spec - P_inj[name])
            if bus.type == 'PQ':
                Q_spec = -bus.reactive_power  # only load matters
                deltaQ.append(Q_spec - Q_inj[name])

        return np.array(deltaP + deltaQ)

# Jacobian - Milestone 7 -JN
class Jacobian:
    def __init__(self, buses: dict, ybus, voltages):
        self.buses = list(buses.values())
        self.ybus = ybus
        self.V = np.abs(voltages)
        self.delta = np.angle(voltages)
        self.bus_index = {bus.name: i for i, bus in enumerate(self.buses)}

        self.pq_buses = [bus for bus in self.buses if bus.type == 'PQ']
        self.pv_buses = [bus for bus in self.buses if bus.type == 'PV']
        self.non_slack_buses = [bus for bus in self.buses if bus.type != 'Slack']

    def calc_jacobian(self):
        J1 = self.calc_J1()
        J2 = self.calc_J2()
        J3 = self.calc_J3()
        J4 = self.calc_J4()

        top = np.hstack((J1, J2))
        bottom = np.hstack((J3, J4))
        return np.vstack((top, bottom))

    def calc_J1(self):
        # ∂P/∂δ
        n = len(self.non_slack_buses)
        J1 = np.zeros((n, n))

        for i, bus_i in enumerate(self.non_slack_buses):
            ki = self.bus_index[bus_i.name]
            for j, bus_j in enumerate(self.non_slack_buses):
                kj = self.bus_index[bus_j.name]
                if ki == kj:
                    for m, bus_m in enumerate(self.buses):
                        if bus_m.name != bus_i.name:
                            km = self.bus_index[bus_m.name]
                            Y_km = self.ybus.iloc[ki, km]
                            G = Y_km.real
                            B = Y_km.imag
                            angle = self.delta[ki] - self.delta[km]
                            J1[i, j] += self.V[ki] * self.V[km] * (G * np.sin(angle) - B * np.cos(angle))
                    J1[i, j] *= -1
                else:
                    Y_kj = self.ybus.iloc[ki, kj]
                    G = Y_kj.real
                    B = Y_kj.imag
                    angle = self.delta[ki] - self.delta[kj]
                    J1[i, j] = self.V[ki] * self.V[kj] * (G * np.sin(angle) - B * np.cos(angle))
        return J1

    def calc_J2(self):
        # ∂P/∂V for non-slack (rows) vs PQ (columns)
        rows = len(self.non_slack_buses)
        cols = len(self.pq_buses)
        J2 = np.zeros((rows, cols))

        for i, bus_i in enumerate(self.non_slack_buses):
            ki = self.bus_index[bus_i.name]
            for j, bus_j in enumerate(self.pq_buses):
                kj = self.bus_index[bus_j.name]
                Y_kj = self.ybus.iloc[ki, kj]
                G = Y_kj.real
                B = Y_kj.imag
                angle = self.delta[ki] - self.delta[kj]

                if ki == kj:
                    sum_term = 0
                    for m, bus_m in enumerate(self.buses):
                        km = self.bus_index[bus_m.name]
                        if km == ki:
                            continue
                        Y_km = self.ybus.iloc[ki, km]
                        Gm = Y_km.real
                        Bm = Y_km.imag
                        angle_m = self.delta[ki] - self.delta[km]
                        sum_term += self.V[km] * (Gm * np.cos(angle_m) + Bm * np.sin(angle_m))
                        # Quite note, ran tests, sum_term always equals 0 here, not sure why, maybe not intential?
                    J2[i, j] = -sum_term
                else:
                    J2[i, j] = self.V[ki] * (G * np.cos(angle) + B * np.sin(angle))
        return J2

    def calc_J3(self):
        # ∂Q/∂δ for PQ buses only
        rows = len(self.pq_buses)
        cols = len(self.non_slack_buses)
        J3 = np.zeros((rows, cols))

        for i, bus_i in enumerate(self.pq_buses):
            ki = self.bus_index[bus_i.name]
            for j, bus_j in enumerate(self.non_slack_buses):
                kj = self.bus_index[bus_j.name]
                angle = self.delta[ki] - self.delta[kj]

                if ki == kj:
                    # Diagonal element
                    sum_term = 0
                    for m, bus_m in enumerate(self.buses):
                        km = self.bus_index[bus_m.name]
                        if km == ki:
                            continue
                        Y_km = self.ybus.iloc[ki, km]
                        G = Y_km.real
                        B = Y_km.imag
                        angle_m = self.delta[ki] - self.delta[km]
                        sum_term += self.V[km] * (G * np.cos(angle_m) + B * np.sin(angle_m))
                    J3[i, j] = self.V[ki] * sum_term  # POSITIVE — NOT NEGATIVE
                else:
                    # Off-diagonal
                    Y_kj = self.ybus.iloc[ki, kj]
                    G = Y_kj.real
                    B = Y_kj.imag
                    J3[i, j] = -self.V[ki] * self.V[kj] * (G * np.cos(angle) + B * np.sin(angle))

        return J3

    def calc_J4(self):
        # ∂Q/∂V for PQ (rows) vs PQ (columns)
        size = len(self.pq_buses)
        J4 = np.zeros((size, size))

        for i, bus_i in enumerate(self.pq_buses):
            ki = self.bus_index[bus_i.name]
            for j, bus_j in enumerate(self.pq_buses):
                kj = self.bus_index[bus_j.name]
                angle = self.delta[ki] - self.delta[kj]
                Y_kj = self.ybus.iloc[ki, kj]
                G = Y_kj.real
                B = Y_kj.imag

                if ki == kj:
                    sum_term = 0
                    for m, bus_m in enumerate(self.buses):  # all buses
                        km = self.bus_index[bus_m.name]
                        if km == ki:
                            continue
                        Y_km = self.ybus.iloc[ki, km]
                        Gm = Y_km.real
                        Bm = Y_km.imag
                        angle_m = self.delta[ki] - self.delta[km]
                        sum_term += self.V[km] * (Gm * np.sin(angle_m) - Bm * np.cos(angle_m))
                    Bii = self.ybus.iloc[ki, ki].imag
                    J4[i, j] = -2 * self.V[ki] * Bii + sum_term   # FULL correct formula
                else:
                    J4[i, j] = self.V[ki] * (G * np.sin(angle) - B * np.cos(angle))

        return J4

    def get_jacobian_dataframe(self, round_decimals=5):
        """
        Returns the Jacobian matrix as a clean, labeled pandas DataFrame.

        Parameters:
        round_decimals (int): Number of decimal places to round for display.

        Returns:
        pd.DataFrame: Labeled and rounded Jacobian matrix.
        """
        J = self.calc_jacobian()

        # Create labels: δ_BusName for angle entries, V_BusName for voltage magnitude entries
        delta_labels = [f"δ_{bus.name}" for bus in self.non_slack_buses]
        v_labels = [f"V_{bus.name}" for bus in self.pq_buses]
        labels = delta_labels + v_labels

        df = pd.DataFrame(J, index=labels, columns=labels)
        return df.round(round_decimals)

if __name__ == '__main__':
    test_circuit = Circuit('Test Circuit')
    # Checking attribute initialization
    print(test_circuit.name)
    print(type(test_circuit.name))
    print(test_circuit.buses)
    print(type(test_circuit.buses))
    print(test_circuit.transformers)
    print(type(test_circuit.transformers))
    print(test_circuit.transmission_lines)
    print(type(test_circuit.transmission_lines))
    # Initializing different class types are adding them
    test_circuit.add_bus('Bus1', 20)
    test_circuit.add_bus('Bus2', 130)
    test_circuit.add_bus('Bus3', 230)
    print(type(test_circuit.buses["Bus1"]))
    print(test_circuit.buses["Bus1"].name, test_circuit.buses["Bus1"].baseKV)
    print(test_circuit.buses["Bus2"].name, test_circuit.buses["Bus2"].baseKV)
    print(test_circuit.buses["Bus3"].name, test_circuit.buses["Bus3"].baseKV)
    # Creating a transformer
    test_circuit.add_transformer('T1', test_circuit.buses.get("Bus1"), test_circuit.buses.get("Bus2"),
                                 130, 50, 11)
    T1_key = ('T1', test_circuit.buses.get("Bus1"), test_circuit.buses.get("Bus2"))
    print(type(test_circuit.transformers[T1_key]))
    print(test_circuit.transformers[T1_key].name, test_circuit.transformers[T1_key].bus1, test_circuit.transformers[T1_key].bus2,
          test_circuit.transformers[T1_key].power_rating, test_circuit.transformers[T1_key].impedance_percent,
          test_circuit.transformers[T1_key].x_over_r_ratio)
    # Creating a Transmission Line
    # Creating these out, since they would be defined in a parameters file or similar
    cardinal = Conductor("Cardinal", 1.196 / 12, 0.0403, 0.1128, 1010)
    test_bundle = Bundle('test_bundle', 2, 3, cardinal)
    test_geometry = Geometry("test_bundle", 0, 0, 18.5, 0, 37, 0)
    #
    test_circuit.add_transmission_line("Tline1", test_circuit.buses.get("Bus2"), test_circuit.buses.get("Bus3"),
                                       test_bundle, test_geometry, 100)
    Tline_key = ('Tline1', test_circuit.buses.get("Bus2"), test_circuit.buses.get("Bus3"))
    print(type(test_circuit.transmission_lines[Tline_key]))
    print(test_circuit.transmission_lines[Tline_key].name, test_circuit.transmission_lines[Tline_key].bus1,
          test_circuit.transmission_lines[Tline_key].bus2,
          test_circuit.transmission_lines[Tline_key].bundle, test_circuit.transmission_lines[Tline_key].geometry,
          test_circuit.transmission_lines[Tline_key].length)

    test_circuit.calc_ybus()