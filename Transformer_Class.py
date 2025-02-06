from Bus import Bus  # Ensure Bus.py is correctly set up


class Transformer:
    """Represents a transformer in the power system."""

    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float,
                 x_over_r_ratio: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.zt = self.calc_impedance()
        self.yt = self.calc_admittance()
        self.y_primitive = self.calc_y_primitive()  # Renamed yprim for clarity

    def calc_impedance(self):
        """Calculates the transformer impedance in per unit."""
        zt_pu = (self.impedance_percent / 100) * (self.power_rating / (self.bus1.baseKV ** 2))
        return complex(zt_pu, zt_pu * self.x_over_r_ratio)

    def calc_admittance(self):
        """Calculates the transformer admittance in per unit."""
        return 1 / self.zt if self.zt != 0 else 0

    def calc_y_primitive(self):
        """Computes the primitive admittance matrix."""
        return [[self.yt, -self.yt], [-self.yt, self.yt]]

    def __repr__(self):
        return f"Transformer(name={self.name}, buses=({self.bus1.name}, {self.bus2.name}), impedance={self.zt})"


# ✅ Move the testing code outside the class
if __name__ == "__main__":
    # Validation Code
    test_bus1 = Bus("Bus 1", 230)  # Renamed from bus1 to avoid shadowing
    test_bus2 = Bus("Bus 2", 230)

    test_transformer = Transformer("T1", test_bus1, test_bus2, 100, 8.5, 10)

    print("Transformer Attributes Validation:")
    print(f"Name: {test_transformer.name}")
    print(f"Connected Buses: {test_transformer.bus1.name}, {test_transformer.bus2.name}")
    print(f"Power Rating: {test_transformer.power_rating} MVA")
    print(f"Impedance Percent: {test_transformer.impedance_percent}%")
    print(f"X/R Ratio: {test_transformer.x_over_r_ratio}")

    print("\nImpedance Calculation:")
    print(f"Calculated Impedance (Zt): {test_transformer.zt}")

    print("\nAdmittance Calculation:")
    print(f"Calculated Admittance (Yt): {test_transformer.yt}")

    print("\nPrimitive Admittance Matrix:")
    for row in test_transformer.y_primitive:
        print(row)
