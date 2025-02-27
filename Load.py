class Load:
    """Models a load connected to a power system bus."""

    def __init__(self, name: str, bus, real_power: float, reactive_power: float):
        """
        Initializes a load instance.

        Parameters:
        name (str): Load identifier.
        bus (Bus): Bus object the load is connected to.
        real_power (float): Real power demand in MW.
        reactive_power (float): Reactive power demand in Mvar.
        """
        self.name = name
        self.bus = bus
        self.real_power = real_power
        self.reactive_power = reactive_power

    def __repr__(self):
        return f"Load(name={self.name}, bus={self.bus.name}, Pload={self.real_power} MW, Qload={self.reactive_power} Mvar)"
