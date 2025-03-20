# need to create 7 node system here
import pandas as pd
import numpy as np
from Circuit import Circuit
# Seem to need these, just circuit does not work
from conductor import  Conductor
from Bus import Bus
from Bundle import  Bundle
from Geometry import Geometry
from Settings import Settings

pd.options.display.width = 0

# Creating the main circuit
# Initialize the circuit structure
seven_circuit = Circuit('Seven Bus System')
seven_circuit.add_bus('Bus1', 125)
seven_circuit.add_bus('Bus2', 230)
seven_circuit.add_bus('Bus3', 230)
seven_circuit.add_bus('Bus4', 230)
seven_circuit.add_bus('Bus5', 230)
seven_circuit.add_bus('Bus6', 230)
seven_circuit.add_bus('Bus7', 18)
# Initializing the transmission lines
# Basic surround structures first
partridge = Conductor("Partridge", 0.642 / 12, 0.0217, 0.385, 460)
seven_bundle = Bundle('test_bundle', 2, 1.5, partridge) #Spacing in feet
seven_geometry = Geometry("test_bundle", 0, 0, 18.5, 0, 37, 0)
# tLine lengths : 10 25 20 20 10 35
seven_circuit.add_transmission_line("tLine1", seven_circuit.buses.get("Bus2"), seven_circuit.buses.get("Bus4"),
                                       seven_bundle, seven_geometry, 10)
# tLine_key = ('tLine1', seven_circuit.buses.get("Bus2"), seven_circuit.buses.get("Bus4")) for debug
seven_circuit.add_transmission_line("tLine2", seven_circuit.buses.get("Bus2"), seven_circuit.buses.get("Bus3"),
                                       seven_bundle, seven_geometry, 25)
seven_circuit.add_transmission_line("tLine3", seven_circuit.buses.get("Bus3"), seven_circuit.buses.get("Bus5"),
                                       seven_bundle, seven_geometry, 20)
seven_circuit.add_transmission_line("tLine4", seven_circuit.buses.get("Bus4"), seven_circuit.buses.get("Bus6"),
                                       seven_bundle, seven_geometry, 20)
seven_circuit.add_transmission_line("tLine5", seven_circuit.buses.get("Bus5"), seven_circuit.buses.get("Bus6"),
                                       seven_bundle, seven_geometry, 10)
seven_circuit.add_transmission_line("tLine6", seven_circuit.buses.get("Bus4"), seven_circuit.buses.get("Bus5"),
                                       seven_bundle, seven_geometry, 35)
# Transformers
seven_circuit.add_transformer('T1', seven_circuit.buses.get("Bus1"), seven_circuit.buses.get("Bus2"),
                                 125, 8.5, 10)
seven_circuit.add_transformer('T2', seven_circuit.buses.get("Bus6"), seven_circuit.buses.get("Bus7"),
                                 200, 10.5, 12)
seven_circuit.calc_ybus()
print(list(seven_circuit.buses.keys()))
print(seven_circuit.transformers)