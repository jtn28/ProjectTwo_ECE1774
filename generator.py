from bus import Bus
import pandas as pd
class Generator:
    """Models a generator connected to a power system bus."""

    def __init__(self, name: str, bus: Bus, voltage_setpoint: float, mw_setpoint: float,
        x0_subtransient: float = 0.0,
        x1_subtransient: float = 0.0,
        x2_subtransient: float = 0.0,
        grounding_impedance: complex = 0 + 0j,
        is_grounded: bool = True
    ):
        """
        Initializes a generator instance.

        Parameters:
        name (str): Generator identifier.
        bus (Bus): Bus object the generator is connected to.
        voltage_setpoint (float): Desired voltage in per unit (p.u.).
        mw_setpoint (float): Real power generation in MW.
        x2_subtransient (float): Negative sequence subtransient reactance (p.u.).
        x0_subtransient (float): Zero sequence subtransient reactance (p.u.).
        grounding_impedance (complex): Generator grounding impedance (R + jX). Defaults to 0 (solid).
        is_grounded (bool): True if generator is grounded, False if floating (ungrounded).
        """
        self.name = name
        self.bus = bus
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.x2_subtransient = x2_subtransient
        self.x1_subtransient = x1_subtransient
        self.x0_subtransient = x0_subtransient
        self.grounding_impedance = grounding_impedance if is_grounded else None
        self.is_grounded = is_grounded

    def calc_y_primitive_sequence(self, sequence: str = "pos"):
        sequence = sequence.lower()
        y_prim_value = []
        if sequence == "pos":
            """Returns the primitive admittance for the negative sequence network."""
            if self.x1_subtransient == 0:
                y_prim_value = complex("inf")  # Acts like a short circuit
            y_prim_value = 1 / complex(0, self.x1_subtransient)
        elif sequence == "neg":
            """Returns the primitive admittance for the negative sequence network."""
            if self.x2_subtransient == 0:
                y_prim_value = complex("inf")  # Acts like a short circuit
            y_prim_value = 1 / complex(0, self.x2_subtransient)
        elif sequence == "zero":
            """Returns the primitive admittance for the zero sequence network."""
            if not self.is_grounded:
                y_prim_value = 0  # No path for zero sequence current
            total_impedance = complex(0, self.x0_subtransient) + self.grounding_impedance
            if total_impedance == 0:
                y_prim_value = complex("inf")  # Solidly grounded, zero impedance
            y_prim_value = 1 / total_impedance
        else:
            raise ValueError(f"Unknown sequence type: {sequence}")

        df = pd.DataFrame(y_prim_value, index=[self.bus.name], columns=[self.bus.name])
        return df


    def __repr__(self):
        return (f"Generator(name={self.name}, bus={self.bus.name}, Vsp={self.voltage_setpoint} p.u., "
                f"Pgen={self.mw_setpoint} MW, X''2={self.x2_subtransient} p.u., "
                f"X''0={self.x0_subtransient} p.u., "
                f"{'Grounded' if self.is_grounded else 'Ungrounded'}, "
                f"Zg={self.grounding_impedance if self.is_grounded else 'N/A'})")