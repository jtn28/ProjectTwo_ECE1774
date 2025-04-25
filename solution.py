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
