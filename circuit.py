import pandas as pd
import numpy as np
from settings import Settings
from bus import Bus
from conductor import Conductor
from bundle import Bundle
from geometry import Geometry
from transformer_Class import Transformer
from transmissionLine import TransmissionLine
from generator import Generator
from load import Load

class Circuit:
    def __init__(self, name:str):
        self.name = name
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.generators = {}
        self.loads = {}


    def add_bus(self, name:str, baseKV:float, vpu:float = 1, delta:float = 0, bus_type:str = 'Slack'):
        bus = Bus(name, baseKV, vpu, delta, bus_type)
        self.buses[bus.name] = bus
        return

    def add_transformer(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float,
                 x_over_r_ratio: float):
        transformer = Transformer(name, bus1, bus2, power_rating, impedance_percent, x_over_r_ratio)
        instance = (transformer.name, transformer.bus1, transformer.bus2)
        self.transformers[instance] = transformer
        return

    def add_transmission_line(self, name:str, bus1:Bus, bus2:Bus, bundle:Bundle, geometry:Geometry, length:float):
        transmission_line = TransmissionLine(name, bus1, bus2, bundle, geometry, length)
        instance = (transmission_line.name, transmission_line.bus1, transmission_line.bus2)
        self.transmission_lines[instance] = transmission_line
        return

    def add_generator(self, name:str, bus:Bus, voltage_setpoint:float, mw_setpoint:float):
        generator = Generator(name, bus, voltage_setpoint, mw_setpoint)
        instance = (generator.name, generator.bus)
        self.generators[instance] = generator
        self.buses[bus.name].real_power += mw_setpoint

    def add_load(self, name: str, bus, real_power: float, reactive_power: float):
        load = Load(name, bus, real_power, reactive_power)
        instance = (load.name, load.bus)
        self.loads[instance] = load
        self.buses[bus.name].real_power += real_power
        self.buses[bus.name].imaginary_power += reactive_power

    # For Creating the big Y Bus, use a for loop for each element, then grab the y primitive, then add it
    # to the y bus matrix, and keep going, use tags to know how to orient the whole thing
    def calc_ybus(self):
        bus_names = list(self.buses.keys())
        y_bus = pd.DataFrame(0, index=bus_names, columns=bus_names, dtype=complex)
        for item in self.transformers:
            prim = self.transformers[item].calc_y_primitive()
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value
        for item in self.transmission_lines:
            prim = self.transmission_lines[item].calc_y_primitive()
            for row in prim.index:
                for col in prim.columns:
                    value = prim.loc[row, col]
                    y_bus.loc[row, col] += value



        # Currently here to make it easier to debug, remove print statement the final implementation
        print(y_bus)
        return y_bus

    def compute_power_injection(self, busDict, yBusFrame, voltageVector):
        for bus in busDict:
            pass


        return

    # Power Mismatch Calculations, Slack has none, PQ includes both and PV excludes.
    def compute_power_mismatch(self, busDict, yBusFrame, voltageVector):
        Vpu = np.ones(Bus.counter)
        delta = np.zeros(Bus.counter)
        busNames = list(busDict.keys())
        # Get the results of the injection
        injection_results = Settings.compute_power_injection(busDict, yBusFrame, voltageVector)

        # Initialize mismatch arrays for real (P) and reactive (Q) power
        real_power_mismatch = np.zeros(Bus.counter)
        reactive_power_mismatch = np.zeros(Bus.counter)
        for k in range(len(busNames)):
        # 1. Loop through to get voltages and angles
        # 2. Separate Call compute_power_injection (Will take voltages and angles)
        # 3. loop through generators and loads to find given power
            # Need to add those to main, do later
        # Subtract the two values
            bus_name = busNames[k]
            bus = busDict[bus_name]

            Vpu[k] = busDict[bus_name].vpu
            delta[k] = busDict[bus_name].delta
            #Compute the real and reactive power injection from the method
            injected_real_power = injection_results[bus_name]['P']
            injected_reactive_power = injection_results[bus_name]['Q']

            # Fetch the specified (expected) power for the bus
            if bus.bus_type == 'Slack':
                specified_real_power = 0  # Real power demand or generation
                specified_reactive_power = 0  # Reactive power demand or generation
            elif bus.bus_type == 'PV':
                specified_real_power = bus.real_power
                specified_reactive_power = 0
            elif bus.bus_type == 'PQ':
                specified_real_power = bus.real_power
                specified_reactive_power = bus.reactive_power
            else:
                print('Incorrect bus type, setting vals to 0')
                specified_real_power = 0
                specified_reactive_power = 0

        # Calculate mismatch (injection - specified power)
            real_power_mismatch[k] = specified_real_power - injected_real_power
            reactive_power_mismatch[k] = specified_reactive_power - injected_reactive_power

        # Combine the real and reactive mismatches into one array (stacked)
        power_mismatch = np.concatenate((real_power_mismatch, reactive_power_mismatch))

        return power_mismatch


if __name__ == '__main__':
    test_circuit = Circuit('Test Circuit')
    # Checking attribute initialization
    print(test_circuit.name)
    print(type(test_circuit.name))
    print(test_circuit.buses)
    print(type(test_circuit.buses))
    print(test_circuit.transformers)
    print(type(test_circuit.transformers))
    print(test_circuit.transmission_lines)
    print(type(test_circuit.transmission_lines))
    # Initializing different class types are adding them
    test_circuit.add_bus('Bus1', 20)
    test_circuit.add_bus('Bus2', 130)
    test_circuit.add_bus('Bus3', 230)
    print(type(test_circuit.buses["Bus1"]))
    print(test_circuit.buses["Bus1"].name, test_circuit.buses["Bus1"].baseKV)
    print(test_circuit.buses["Bus2"].name, test_circuit.buses["Bus2"].baseKV)
    print(test_circuit.buses["Bus3"].name, test_circuit.buses["Bus3"].baseKV)
    # Creating a transformer
    test_circuit.add_transformer('T1', test_circuit.buses.get("Bus1"), test_circuit.buses.get("Bus2"),
                                 130, 50, 11)
    T1_key = ('T1', test_circuit.buses.get("Bus1"), test_circuit.buses.get("Bus2"))
    print(type(test_circuit.transformers[T1_key]))
    print(test_circuit.transformers[T1_key].name, test_circuit.transformers[T1_key].bus1, test_circuit.transformers[T1_key].bus2,
          test_circuit.transformers[T1_key].power_rating, test_circuit.transformers[T1_key].impedance_percent,
          test_circuit.transformers[T1_key].x_over_r_ratio)
    # Creating a Transmission Line
    # Creating these out, since they would be defined in a parameters file or similar
    cardinal = Conductor("Cardinal", 1.196 / 12, 0.0403, 0.1128, 1010)
    test_bundle = Bundle('test_bundle', 2, 3, cardinal)
    test_geometry = Geometry("test_bundle", 0, 0, 18.5, 0, 37, 0)
    #
    test_circuit.add_transmission_line("Tline1", test_circuit.buses.get("Bus2"), test_circuit.buses.get("Bus3"),
                                       test_bundle, test_geometry, 100)
    Tline_key = ('Tline1', test_circuit.buses.get("Bus2"), test_circuit.buses.get("Bus3"))
    print(type(test_circuit.transmission_lines[Tline_key]))
    print(test_circuit.transmission_lines[Tline_key].name, test_circuit.transmission_lines[Tline_key].bus1,
          test_circuit.transmission_lines[Tline_key].bus2,
          test_circuit.transmission_lines[Tline_key].bundle, test_circuit.transmission_lines[Tline_key].geometry,
          test_circuit.transmission_lines[Tline_key].length)

    test_circuit.calc_ybus()