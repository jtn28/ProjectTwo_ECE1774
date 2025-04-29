from bus import Bus  # Ensure bus.py is correctly set up
from settings import Settings
import pandas as pd
import numpy as np

class Transformer:
    """Represents a transformer in the power system using per-unit calculations."""

    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float,
                 x_over_r_ratio: float, base_power: float = Settings.base_power * 1e-6,
                 connection_type: str = "Y-Y", ground_imp_1: complex = 0 + 0j, ground_imp_2: complex = 0 + 0j):
        """
        Initializes a transformer instance.

        Parameters:
        name (str): Name of the transformer.
        bus1, bus2 (Bus): Connected buses.
        power_rating (float): Transformer rating in MVA.
        impedance_percent (float): Transformer impedance in percentage.
        x_over_r_ratio (float): Reactance-to-resistance ratio.
        base_power (float): System base power in MVA (default: 100, pulled from settings file, with 1e-6 to compensate for settings being in VA not MVA).
        """
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.base_power = base_power
        self.ground_imp_1 = ground_imp_1
        self.ground_imp_2 = ground_imp_2
        self.connection_type = connection_type

        # Ensure these are initialized before calling calc_impedance
        self.v2rated = self.bus2.baseKV  # Renamed to lowercase
        self.srated = self.power_rating  # Renamed to lowercase

        self.rpu, self.xpu = self.calc_impedance()  # Now it can access self.v2rated
        self.yseries = self.calc_admittance()
        self.y_primitive = self.calc_y_primitive()

    def calc_impedance(self, vbase_new=None, sbase_new=None):
        """
        Calculates the per-unit resistance (rpu) and reactance (xpu).

        Parameters:
        vbase_new (float, optional): Voltage base for per-unit calculation.
        sbase_new (float, optional): Power base for per-unit calculation.

        Returns:
        tuple: (rpu, xpu) representing resistance and reactance in per-unit.
        """
        if vbase_new is None:
            vbase_new = self.v2rated
        if sbase_new is None:
            sbase_new = self.srated

        z_base = (vbase_new ** 2) / sbase_new  # Ensured lowercase variable name
        z_pu = (self.impedance_percent / 100) * (self.base_power / self.power_rating)* np.exp(1j * np.arctan(self.x_over_r_ratio)) #verify this equation
        xpu = z_pu.imag  #need x over r
        rpu = z_pu.real
        return rpu, xpu

    def calc_admittance(self):
        """
        Computes per-unit admittance (yseries).

        Returns:
        float: Admittance value in per-unit.
        """
        return 1 / complex(self.rpu, self.xpu) if self.rpu or self.xpu else 0

    def calc_y_primitive(self):
        """
        Computes the primitive admittance matrix (y_primitive) and formats it using pandas.

        Returns:
        DataFrame: 2x2 primitive admittance matrix with bus names as labels.
        """
        y_matrix = [[self.yseries, -self.yseries], [-self.yseries, self.yseries]]
        df = pd.DataFrame(y_matrix, index=[self.bus1.name, self.bus2.name], columns=[self.bus1.name, self.bus2.name])
        return df

    # Milestone 10
    def calc_y_primitive_sequence(self, sequence: str = "pos"):
        """
        Calculate primitive admittance for a specified sequence.

        sequence (str): 'positive', 'negative', or 'zero'
        """
        sequence = sequence.lower()

        if sequence in ['pos', 'neg']:
            return self.calc_y_primitive()
        elif sequence == 'zero':
            # Handling zero-sequence based on transformer type
            return self.zero_sequence_admittance()

    def zero_sequence_admittance(self):
        match self.connection_type:
            case "Y-Y":
                y_ground1 = 1 / self.ground_imp_1 if self.ground_imp_1 != 0 else complex("inf")
                y_ground2 = 1 / self.ground_imp_2 if self.ground_imp_2 != 0 else complex("inf")
                self.yseries =  1 / (complex(self.rpu, self.xpu) + 1 / (y_ground1 + y_ground2)) if y_ground1 or y_ground2 else 0
                return self.calc_y_primitive()
            case "Y-DELTA":
                #return 0
                y_ground1 = 1 / self.ground_imp_1 if self.ground_imp_1 != 0 else complex("inf")
                sector =  1 / (complex(self.rpu, self.xpu) + 1 / y_ground1) if y_ground1 != complex("inf") else 0
                y_matrix = [[sector, 0], [0, 0]]
                df = pd.DataFrame(y_matrix, index=[self.bus1.name, self.bus2.name],
                                  columns=[self.bus1.name, self.bus2.name])
                return df
            case "DELTA-Y":
                #return 0
                y_ground2 = 1 / self.ground_imp_2 if self.ground_imp_2 != 0 else complex("inf")
                sector =  1 / (complex(self.rpu, self.xpu) + 1 / y_ground2) if y_ground2 != complex("inf") else 0
                y_matrix = [[0, 0], [0, sector]]
                df = pd.DataFrame(y_matrix, index=[self.bus1.name, self.bus2.name],
                                  columns=[self.bus1.name, self.bus2.name])
                return df
            case "DELTA-DELTA":
                return pd.DataFrame([[0,0],[0,0]], index=[self.bus1.name, self.bus2.name],
                                  columns=[self.bus1.name, self.bus2.name])
            case _:
                raise ValueError(f"Unknown transformer connection type: {self.connection_type}")
    def __repr__(self):
        """String representation of the transformer instance."""
        return f"Transformer(name={self.name}, buses=({self.bus1.name}, {self.bus2.name}), Zpu=({self.rpu:.4f}, 1j*{self.xpu:.4f}))"


# Validation Code inside `__main__`
if __name__ == "__main__":
    test_bus1 = Bus("Bus 1", 20)
    test_bus2 = Bus("Bus 2", 230)

    transformer1 = Transformer("T1", test_bus1, test_bus2, 125, 8.5, 10)

    print("\nTransformer Attributes Validation:")
    print(transformer1)

    print("\nCheck Impedance and Admittance Calculations:")
    print(transformer1.rpu, transformer1.xpu, transformer1.yseries)  # Corrected variable names (no caps)

    print("\nVerify the Primitive Admittance Matrix:")
    print(transformer1.calc_y_primitive().to_string())  # Ensures DataFrame prints correctly
