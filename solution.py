import numpy as np
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
            print(f"\n--- Iteration {iteration + 1} ---")

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
            print(f"Max mismatch: {max_mismatch:.6f}")
            if max_mismatch < tol:
                print("Convergence achieved.")
                break

            # Step 4: Compute Jacobian
            J = Jacobian(self.circuit.buses, self.ybus, voltages).calc_jacobian()
            #print(Jacobian(self.circuit.buses, self.ybus, voltages).get_jacobian_dataframe())
            # Step 5: Solve linear system
            try:
                dx = np.linalg.solve(J, mismatch_reduced)
            except np.linalg.LinAlgError:
                raise ValueError("Jacobian is singular or ill-conditioned.")

            #print("hi")
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
            for name, v in zip(self.circuit.buses.keys(), voltages):
                print(f"{name}: |V| = {np.abs(v):.5f} pu, ∠ = {np.angle(v, deg=True):.2f}°")

        else:
            print("Newton-Raphson did not converge in allotted iterations.")

        return voltages


class SymFaultSolver:
    def __init__(self, circuit, prefault_voltages):
        """
        Initialize the symmetrical fault solver using the given Circuit object
        and the pre-fault voltages (from a solved NR power flow).
        """
        self.circuit = circuit
        self.ybus = circuit.calc_ybus().values
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
        Ifault = self.V_prefault[bus_index] / Zii

        # Voltage drop due to fault
        deltaV = Ifault * Zbus[:, bus_index]

        # Post-fault voltages
        V_fault = self.V_prefault - deltaV

        return {
            "fault_bus": faulted_bus_name,
            "fault_current": Ifault,
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
            fault_current_pos = 3 * self.V_prefault[bus_index] / (Z_eq + self.fault_impedance)
            fault_current_neg = fault_current_pos
            fault_current_zero = fault_current_pos
        elif self.fault_type == "LL":
            Z_eq = self.z_pos.loc[faulted_bus_name, faulted_bus_name] + self.z_neg.loc[faulted_bus_name, faulted_bus_name]
            fault_current_pos = np.sqrt(3) * self.V_prefault[bus_index] / (Z_eq + self.fault_impedance)
            fault_current_neg = -fault_current_pos
            fault_current_zero = 0
        elif self.fault_type == "DLG":
            Z_parallel = ((self.z_neg.loc[faulted_bus_name, faulted_bus_name] * self.z_zero.loc[faulted_bus_name, faulted_bus_name])
                          / (self.z_neg.loc[faulted_bus_name, faulted_bus_name] + self.z_zero.loc[faulted_bus_name, faulted_bus_name]))
            Z_eq = self.z_pos.loc[faulted_bus_name, faulted_bus_name] + Z_parallel + self.fault_impedance
            fault_current_pos = self.V_prefault[bus_index] / Z_eq
            fault_current_neg = (self.z_zero.loc[faulted_bus_name, faulted_bus_name] / self.z_neg.loc[faulted_bus_name, faulted_bus_name]) * fault_current_pos
            fault_current_zero = (self.z_neg.loc[faulted_bus_name, faulted_bus_name] / self.z_zero.loc[faulted_bus_name, faulted_bus_name]) * fault_current_pos
        else:
            raise ValueError("Invalid fault ype, Choose between SLG, LL or DLG")

        V_pos = self.V_prefault[bus_index] - self.z_pos.loc[faulted_bus_name, faulted_bus_name] * fault_current_pos
        V_neg = -self.z_neg.loc[faulted_bus_name, faulted_bus_name] * fault_current_neg
        V_zero = -self.z_zero.loc[faulted_bus_name, faulted_bus_name] * fault_current_zero

        # Phase voltages
        a = np.exp(1j*2*np.pi/3)
        A = np.array([
            [1, 1, 1],
            [1, a ** 2, a],
            [1, a, a ** 2]
        ])
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
            "V_phase_phasors": V_phase_phasors
        }
