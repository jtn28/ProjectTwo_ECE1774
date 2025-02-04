import Bus as Bus
class Transformer:
    """Represents a transformer in the power system."""

    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float, #need bus syntax to ensure proper definition
                 x_over_r_ratio: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.zt = self.calc_impedance()
        self.yt = self.calc_admittance()
        self.yprim = self.calc_yprim()

    def calc_impedance(self):
        """Calculates the transformer impedance in per unit."""
        zt_pu = (self.impedance_percent / 100) * (self.power_rating / (self.bus1.base_kv ** 2))
        return complex(zt_pu, zt_pu * self.x_over_r_ratio)

    def calc_admittance(self):
        """Calculates the transformer admittance in per unit."""
        return 1 / self.zt if self.zt != 0 else 0

    def calc_yprim(self):
        """Computes the primitive admittance matrix."""
        y_matrix = [[self.yt, -self.yt],
                    [-self.yt, self.yt]]
        return y_matrix

    def __repr__(self):
        return f"Transformer(name={self.name}, buses=({self.bus1.name}, {self.bus2.name}), impedance={self.zt})"