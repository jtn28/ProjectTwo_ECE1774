import math


class Geometry:
    """Represent the physical arrangement for conductors in a transmission line."""

    def __init__(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
        """
        Initialize geometry.

        Parameters:
        name (str): Name of geometry config
        xa, ya (float): Coordinates of conductor A
        xb, yb (float): Coordinates of conductor B
        xc, yc (float): Coordinates of conductor C
        """
        self.name = name
        self.xa, self.ya = xa, ya
        self.xb, self.yb = xb, yb
        self.xc, self.yc = xc, yc
        self.Deq = self.calc_deq()  # Fixed method call

    def calc_deq(self) -> float:
        """Calculates the equivalent distance (Deq)."""
        dab = math.sqrt((self.xb - self.xa) ** 2 + (self.yb - self.ya) ** 2)
        dbc = math.sqrt((self.xc - self.xb) ** 2 + (self.yc - self.yb) ** 2)
        dac = math.sqrt((self.xc - self.xa) ** 2 + (self.yc - self.ya) ** 2)
        return (dab * dbc * dac) ** (1 / 3)  # Geometric mean distance

    def __repr__(self):
        return f"Geometry(name={self.name}, Deq={self.Deq:.4f})"

# Test instance
if __name__ == "__main__":
    geom1 = Geometry("Test Config", 0, 0, 18.5, 0, 37, 0)

    # Print attributes
    print(geom1)  # Should display Geometry(name=Test Config, Deq=<computed value>)
    print(f"Deq Calculation: {geom1.Deq}")
