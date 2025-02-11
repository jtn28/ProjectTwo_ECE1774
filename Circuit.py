from Bus import Bus
from Conductor import Conductor
from Bundle import Bundle
from Geometry import Geometry
from Transformer_Class import Transformer
from TransmissionLine import TransmissionLine

class Circuit:
    def __init__(self, name:str):
        self.name = name
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}

    def add_bus(self, name:str, baseKV:float):
        bus = Bus(name, baseKV)
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
