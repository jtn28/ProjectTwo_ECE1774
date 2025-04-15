import numpy as np
from circuit import Circuit, Jacobian
from bus import Bus

class Solution:
    def __init__(self, ybus, voltages, buses):
        self.ybus = ybus
        self.voltages = voltages
        self.buses = buses  # Dictionary of bus objects

    def newton_raphson(self, iter_max=5, tol=1e-6):
        voltages = self.voltages.copy()

        for iteration in range(iter_max):
            print(f"\nIteration {iteration + 1}")

            for name, v in zip(self.buses.keys(), voltages):
                mag = np.abs(v)
                angle = np.angle(v, deg=True)
                print(f"{name}: |V| = {mag:.4f} pu, ∠ = {angle:.2f}°")
            # Step 1: Calculate full power mismatch vector
            full_mismatch = self.compute_power_mismatch(voltages)

            # Determine the relevant indices: ∆δ for all non-slack, ∆V for PQ buses
            delta_indices = [i for i, bus in enumerate(self.buses.values()) if bus.type != 'Slack']
            v_indices = [i for i, bus in enumerate(self.buses.values()) if bus.type == 'PQ']

            # Build filtered mismatch: [∆P (no slack), ∆Q (PQ only)]
            filtered_mismatch = np.concatenate([
                full_mismatch[delta_indices],
                full_mismatch[len(self.buses) + np.array(v_indices)]
            ])

            print("  ∆P (non-slack):", full_mismatch[delta_indices])
            print("  ∆Q (PQ):", full_mismatch[len(self.buses) + np.array(v_indices)])

            max_mismatch = np.max(np.abs(filtered_mismatch))
            print(f"  Max Power Mismatch: {max_mismatch:.6f}")
            if max_mismatch < tol:
                print("  Convergence achieved.")
                break

            # Step 2: Compute Jacobian
            J = Jacobian(self.buses, self.ybus, voltages).calc_jacobian()

            # Step 3: Solve for corrections
            try:
                correction = np.linalg.solve(J, filtered_mismatch)
            except np.linalg.LinAlgError:
                raise ValueError("Jacobian is singular or ill-conditioned.")

            # Step 4: Update voltages
            delta = [bus.delta for bus in self.buses.values() if bus.type != 'Slack']
            v_mags = [bus.vpu for bus in self.buses.values() if bus.type == 'PQ']

            num_angle = len(delta)
            num_voltage = len(v_mags)

            delta_correction = correction[:num_angle]
            v_correction = correction[num_angle:]

            angle_idx = 0
            voltage_idx = 0
            for bus in self.buses.values():
                if bus.type != 'Slack':
                    bus.delta += delta_correction[angle_idx]
                    angle_idx += 1
                if bus.type == 'PQ':
                    bus.vpu += v_correction[voltage_idx]
                    voltage_idx += 1

            # Rebuild voltages for next iteration
            voltages = np.array([
                bus.vpu * np.exp(1j * bus.delta)
                for bus in self.buses.values()
            ])
#print
        else:
            print("Newton-Raphson did not converge within the maximum iterations.")

        return voltages


    def compute_power_mismatch(self, voltages):
        from circuit import Circuit  # avoid circular import
        dummy = Circuit("dummy")     # just to access method
        return dummy.compute_power_mismatch(self.buses, self.ybus, voltages)
