class Generator:
    """Models a generator connected to a power system bus."""

    def __init__(self, name: str, bus, voltage_setpoint: float, mw_setpoint: float):
        """
        Initializes a generator instance.

        Parameters:
        name (str): Generator identifier.
        bus (Bus): Bus object the generator is connected to.
        voltage_setpoint (float): Desired voltage in per unit (p.u.).
        mw_setpoint (float): Real power generation in MW.
        """
        self.name = name
        self.bus = bus
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint

    def __repr__(self):
        return f"Generator(name={self.name}, bus={self.bus.name}, Vsp={self.voltage_setpoint} p.u., Pgen={self.mw_setpoint} MW)"
