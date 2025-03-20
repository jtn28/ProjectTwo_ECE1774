import numpy as np

class Settings:
    frequency = 60
    base_power = 100e6
    def __init__(self, frequency:float = 60, base_power:float = 100e6):
        Settings.frequency = frequency
        Settings.base_power = base_power
#implementing Power Injection

    @staticmethod
    def compute_power_injection(bus, ybus, voltages):
        """
        Computes real (P) and reactive (Q) power injections at a given bus.

        Parameters:
        bus (Bus): The bus object for which power injection is computed.
        ybus (ndarray): The system admittance matrix (NxN complex array).
        voltages (ndarray): The voltage magnitudes and angles in complex form (Nx1 array).

        Returns:
        tuple: (P, Q) - Real and reactive power injections in per-unit.
        """
        i = bus.index  # Bus index in YBus matrix

        # Extract magnitude and angle of voltage
        v_k = np.abs(voltages[i])  # Magnitude of bus voltage
        delta_k = np.angle(voltages[i])  # Angle of bus voltage (radians)

        # Initialize power injections
        p_k = 0
        q_k = 0

        # Loop through all buses to compute summation
        for n in range(len(ybus)):
            y_kn = np.abs(ybus[i, n])  # Magnitude of admittance
            theta_kn = np.angle(ybus[i, n])  # Phase angle of admittance

            v_n = np.abs(voltages[n])  # Magnitude of voltage at bus n
            delta_n = np.angle(voltages[n])  # Angle at bus n

            # Compute active and reactive power components
            p_k += v_k * y_kn * v_n * np.cos(delta_k - delta_n - theta_kn)
            q_k += v_k * y_kn * v_n * np.sin(delta_k - delta_n - theta_kn)

        # Handle bus type-specific behavior
        if bus.type == "Slack":
            return None  # No mismatch calculation for Slack Bus
        elif bus.type == "PQ":
            return p_k, q_k  # PQ Bus needs both P and Q
        elif bus.type == "PV":
            return p_k  # PV Bus only needs P

        return None  # Fallback case (should not happen)
