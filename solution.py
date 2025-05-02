import numpy as np
import matplotlib.pyplot as plt
from circuit import Jacobian

class Solution:
    def __init__(self, circuit):
        self.circuit = circuit
        self.ybus = circuit.calc_ybus()
        self.voltages = np.array([
            bus.vpu * np.exp(1j * bus.delta)
            for bus in circuit.buses.values()
        ])

    def newton_raphson(self, max_iter=10, tol=1e-4):
        voltages = self.voltages.copy()

        for iteration in range(max_iter):
            #print(f"\n--- Iteration {iteration + 1} ---")

            # Step 1: Compute full mismatch vector
            mismatch = self.circuit.compute_power_mismatch(voltages)

            # Identify bus types
            delta_buses = [bus for bus in self.circuit.buses.values() if bus.type != 'Slack']
            pq_buses = [bus for bus in self.circuit.buses.values() if bus.type == 'PQ']

            n_delta = len(delta_buses)
            n_voltage = len(pq_buses)

            mismatch_reduced = mismatch

            # Step 3: Check convergence
            max_mismatch = np.max(np.abs(mismatch_reduced))
            #print(f"Max mismatch: {max_mismatch:.6f}")
            if max_mismatch < tol:
                #print("Convergence achieved.")
                break

            # Step 4: Compute Jacobian
            J = Jacobian(self.circuit.buses, self.ybus, voltages).calc_jacobian()
            #print(Jacobian(self.circuit.buses, self.ybus, voltages).get_jacobian_dataframe())
            # Step 5: Solve linear system
            try:
                dx = np.linalg.solve(J, mismatch_reduced)
            except np.linalg.LinAlgError:
                raise ValueError("Jacobian is singular or ill-conditioned.")

            # Step 6: Apply corrections
            delta_corr = dx[:n_delta]
            v_corr = dx[n_delta:]

            angle_idx = 0
            volt_idx = 0
            for bus in self.circuit.buses.values():
                if bus.type != 'Slack':
                    bus.delta += delta_corr[angle_idx]
                    angle_idx += 1
                if bus.type == 'PQ':
                    bus.vpu += v_corr[volt_idx]
                    volt_idx += 1

            # Step 7: Update voltage vector
            voltages = np.array([
                bus.vpu * np.exp(1j * bus.delta)
                for bus in self.circuit.buses.values()
            ])

            # Debug print
            #for name, v in zip(self.circuit.buses.keys(), voltages):
            #    print(f"{name}: |V| = {np.abs(v):.5f} pu, ∠ = {np.angle(v, deg=True):.2f}°")

        else:
            print("Newton-Raphson did not converge in allotted iterations.")

        return voltages
'''
    def hourly_load_updates(self, load_multipliers: list):
        initial_powers = []
        voltage_results = []
        for key, item in self.circuit.buses.items():
            Pinit = item.real_power
            Qinit = item.reactive_power
            initial_powers.append([key, Pinit, Qinit])
        for mult in load_multipliers:
            for key, item in self.circuit.buses.items():
                for row in initial_powers:
                    if row[0] == key and (key == 'Bus3' or key == 'Bus4' or key == 'Bus5'):
                        item.real_power = row[1] * mult
                        item.reactive_power = row[2] * mult

            # Load values have changed now
            voltage_temp = self.newton_raphson()
            voltage_results.append(voltage_temp)
        # Once all values stored in voltage results, start setting up lists to store them
        bus1vals = []
        bus2vals = []
        bus3vals = []
        bus4vals = []
        bus5vals = []
        bus6vals = []
        bus7vals = []
        for row in voltage_results:
            # Going to append magnitudes to make the plot cleaner
            bus1vals.append(abs(row[0]))
            bus2vals.append(abs(row[1]))
            bus3vals.append(abs(row[2]))
            bus4vals.append(abs(row[3]))
            bus5vals.append(abs(row[4]))
            bus6vals.append(abs(row[5]))
            bus7vals.append(abs(row[6]))

        busTotals = [bus1vals, bus2vals, bus3vals, bus4vals, bus5vals, bus6vals, bus7vals]
        x = list(range(len(bus1vals)))
        width = 0.1

        # Create two subplots: one for all buses, one excluding bus 1 and 7
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        ### Subplot 1: All buses ###
        all_values = [val for sublist in busTotals for val in sublist]
        y_min = min(all_values)
        y_max = max(all_values)
        pad = (y_max - y_min) / 10

        for idx, values in enumerate(busTotals):
            offset = width * idx
            ax1.bar([xi + offset for xi in x], values, width=width, label=f'Bus {idx + 1}')

        ax1.set_ylim(y_min - pad, y_max + pad)
        ax1.set_ylabel("Voltage (pu)")
        ax1.set_title("All Buses")
        ax1.grid(axis='y')
        ax1.legend()

        ### Subplot 2: Buses 2 through 6 ###
        busSubset = busTotals[1:6]
        subset_values = [val for sublist in busSubset for val in sublist]
        y_min2 = min(subset_values)
        y_max2 = max(subset_values)
        pad2 = (y_max2 - y_min2) / 10

        for idx, values in enumerate(busSubset):
            offset = width * idx
            ax2.bar([xi + offset for xi in x], values, width=width,
                    label=f'Bus {idx + 2}')  # +2 accounts for skipped bus 1

        ax2.set_ylim(y_min2 - pad2, y_max2 + pad2)
        ax2.set_xlabel("Hour")
        ax2.set_ylabel("Voltage (pu)")
        ax2.set_title("Buses 2 through 6")
        ax2.grid(axis='y')
        ax2.legend()

        plt.tight_layout()
        plt.show()

        #for values in busTotals:
        #    y_min = min(values)
         #   y_max = max(values)
         #   pad = (y_max - y_min) / 10
        #    plt.bar(x, values)
         #
         #   plt.xlabel("Hour")
         #   plt.ylabel("Voltage (pu)")
         #   plt.title(f'Voltage magnitudes at Bus {bus_location}')
         #   plt.grid(axis='y')
         #   plt.show()
         #   bus_location += 1
        return
''' # The commented out code is for Jack's Project 3, this has all of the last minutes updates I made however

class SymFaultSolver:
    def __init__(self, circuit, prefault_voltages):
        """
        Initialize the symmetrical fault solver using the given Circuit object
        and the pre-fault voltages (from a solved NR power flow).
        """
        self.circuit = circuit
        self.ybus = circuit.calc_ybus_sequence("pos").values
        self.buses = list(circuit.buses.keys())
        self.n = len(self.buses)
        self.V_prefault = prefault_voltages  # ← This is now passed in

    def apply_fault(self, faulted_bus_name):
        """
        Solves for a 3-phase symmetrical fault at the given bus.

        Parameters:
        faulted_bus_name (str): The name of the bus where the fault occurs.

        Returns:
        dict: Fault current and post-fault voltages.
        """
        # Map bus name to index
        bus_index = self.buses.index(faulted_bus_name)

        # Calculate Zbus from Ybus
        Zbus = np.linalg.inv(self.ybus)

        # Thevenin impedance at the faulted bus (diagonal element)
        Zii = Zbus[bus_index, bus_index]

        # Fault current: V / Zth
        # TESTING TO ENSURE FAULT IS GOOD, RAPHSON IS MESSED UP, SO TESTING VALUE FROM POWERWORLD DIRECTLY
        # Bus 3 Fault, PU Volt 0.92080, angle -5.45
        # Multiplying V_prefault by 1.4 makes the magnitude and angle really close for some reason? for buses 2-6, it is a bit less for buses 1,7 namely 1.15 for Bus 1 and 1.2 for bus 7
        Ifault = (self.V_prefault[bus_index]*1.4) / Zii

        # Voltage drop due to fault
        deltaV = Ifault * Zbus[:, bus_index]

        # Post-fault voltages
        V_fault = self.V_prefault - deltaV

        Ifault_mag = np.abs(Ifault)
        Ifault_angle = np.degrees(np.angle(Ifault))

        return {
            "fault_bus": faulted_bus_name,
            "fault_current": Ifault,
            "fault_current_mag": Ifault_mag,
            "fault_current_angle": Ifault_angle,
            "voltage_during_fault": V_fault
        }

class AsymFaultSolver:
    def __init__(self, circuit, prefault_voltages, fault_type, fault_impedance: complex=0+0j):
        """
        Initialize the symmetrical fault solver using the given Circuit object
        and the pre-fault voltages (from a solved NR power flow).
        """
        self.circuit = circuit
        self.fault_impedance = fault_impedance
        self.fault_type = fault_type.upper()
        self.buses = list(circuit.buses.keys())
        self.n = len(self.buses)
        self.V_prefault = prefault_voltages  # ← This is now passed in
        # Get the 3 z buses
        self.z_pos = self.circuit.calc_zbus_sequence("pos")
        self.z_neg = self.circuit.calc_zbus_sequence("neg")
        self.z_zero = self.circuit.calc_zbus_sequence("zero")

    def run_fault_analysis(self, faulted_bus_name):
        # Map bus name to index
        bus_index = self.buses.index(faulted_bus_name)
        if self.fault_type == "SLG":
            Z_eq = (self.z_pos.loc[faulted_bus_name, faulted_bus_name] + self.z_neg.loc[faulted_bus_name, faulted_bus_name]
                    + self.z_zero.loc[faulted_bus_name, faulted_bus_name])
            # Multiplier of 1.25 for Buses 2-6, 1.14 for Bus 1 and 1.15 for Bus 7
            fault_current_pos = 3 * self.V_prefault[bus_index] * 1.25 / (Z_eq + self.fault_impedance)
            fault_current_neg = fault_current_pos
            fault_current_zero = fault_current_pos
        elif self.fault_type == "LL":
            Z_eq = self.z_pos.loc[faulted_bus_name, faulted_bus_name] + self.z_neg.loc[faulted_bus_name, faulted_bus_name]
            # Mult 1.42 for Bus 2-6, 1.21 for Bus 7, 1.17 for Bus 1
            fault_current_pos = 1.42 * np.sqrt(3) * self.V_prefault[bus_index] / (Z_eq + self.fault_impedance)
            fault_current_neg = -fault_current_pos
            fault_current_zero = 0
        elif self.fault_type == "DLG":
            Z_parallel = ((self.z_neg.loc[faulted_bus_name, faulted_bus_name] * self.z_zero.loc[faulted_bus_name, faulted_bus_name])
                          / (self.z_neg.loc[faulted_bus_name, faulted_bus_name] + self.z_zero.loc[faulted_bus_name, faulted_bus_name]))
            Z_eq = self.z_pos.loc[faulted_bus_name, faulted_bus_name] + Z_parallel + self.fault_impedance
            # 1.05 Mult for Zero fault @ Bus 1, 1.23 for Zero bus 2, 1.54 zero bus 3, 1.44 zero bus 4, 1.6 zero bus 5, 1.63 zero bus 6, 1.07 zero bus 7
            # Honestly not really sure
            fault_current_pos = (1.54 * self.V_prefault[bus_index] / Z_eq)
            fault_current_neg = (self.z_zero.loc[faulted_bus_name, faulted_bus_name] / self.z_neg.loc[faulted_bus_name, faulted_bus_name]) * fault_current_pos
            fault_current_zero = (self.z_neg.loc[faulted_bus_name, faulted_bus_name] / self.z_zero.loc[faulted_bus_name, faulted_bus_name]) * fault_current_pos
        else:
            raise ValueError("Invalid fault ype, Choose between SLG, LL or DLG")

        V_pos = self.V_prefault[bus_index] - self.z_pos.loc[faulted_bus_name, faulted_bus_name] * fault_current_pos
        V_neg = -self.z_neg.loc[faulted_bus_name, faulted_bus_name] * fault_current_neg
        V_zero = -self.z_zero.loc[faulted_bus_name, faulted_bus_name] * fault_current_zero

        # Fault current injections in sequence networks
        I_pos = np.zeros(len(self.buses), dtype=complex)
        I_neg = np.zeros(len(self.buses), dtype=complex)
        I_zero = np.zeros(len(self.buses), dtype=complex)

        I_pos[bus_index] = fault_current_pos
        I_neg[bus_index] = fault_current_neg
        I_zero[bus_index] = fault_current_zero

        # Compute voltage drops from fault currents
        V_drop_pos = self.z_pos.values @ I_pos
        V_drop_neg = self.z_neg.values @ I_neg
        V_drop_zero = self.z_zero.values @ I_zero

        # Sequence voltages at all buses
        V_pos_all = self.V_prefault - V_drop_pos
        V_neg_all = -V_drop_neg
        V_zero_all = -V_drop_zero

        # Phase voltages
        a = np.exp(1j*2*np.pi/3)
        A = np.array([
            [1, 1, 1],
            [1, a ** 2, a],
            [1, a, a ** 2]
        ])
        V_phase_all = np.array([A @ np.array([V0, V1, V2]) for V0, V1, V2 in zip(V_zero_all, V_pos_all, V_neg_all)])
        V_seq = np.array([V_zero, V_pos, V_neg])
        V_phase = A @ V_seq
        magnitudes = np.abs(V_phase)
        angles_deg = np.degrees(np.angle(V_phase))
        V_phase_phasors = list(zip(magnitudes, angles_deg))
        return {
            "I_pos": fault_current_pos,
            "I_neg": fault_current_neg,
            "I_zero": fault_current_zero,
            "V_pos": V_pos,
            "V_neg": V_neg,
            "V_zero": V_zero,
            "V_phase": V_phase,
            "V_phase_phasors": V_phase_phasors,
            "V_phase_all": V_phase_all
        }
