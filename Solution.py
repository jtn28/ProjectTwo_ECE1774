import numpy as np
from Bus import Bus
from Settings import Settings

class Solution:
    """Handles the verification of power injection calculations."""

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

    def verify_power_injection(self):
        """Verifies power injection calculations for all buses."""
        print("\n--- Power Injection Testing ---")

        for bus in self.buses:
            result = Settings.compute_power_injection(bus, self.ybus, self.voltages)
            print(f"{bus.name} ({bus.type}) Injection: {result}")

    def debug_indices(self):
        """Prints bus indices and voltage array size for debugging."""
        print("\n--- Debugging Index Issues ---")
        for bus in self.buses:
            print(f"{bus.name} Index: {bus.index}")
        print(f"Voltage Array Size: {len(self.voltages)}")

# Example Test
if __name__ == "__main__":
    # Reset bus index counter before defining buses
    Bus.counter = 0

    # Define test system buses
    bus1 = Bus("Bus 1", 230, bus_type="Slack")
    bus2 = Bus("Bus 2", 230, bus_type="PQ")
    bus3 = Bus("Bus 3", 230, bus_type="PV")

    buses = [bus1, bus2, bus3]

    # Define YBus matrix (3x3 for three buses)
    ybus = np.array([
        [5+1j, -2-1j, -3-2j],
        [-2-1j, 4+2j, -1-1j],
        [-3-2j, -1-1j, 6+3j]
    ])

    # Define voltage vector (should match YBus dimensions)
    voltages = np.array([1+0j, 0.95+0.1j, 1.05+0j])

    # Initialize solution object
    sol = Solution(ybus, voltages, buses)

    # Debug indices to catch errors before running injections
    sol.debug_indices()

    # Run power injection validation
    sol.verify_power_injection()
