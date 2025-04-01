import pandas as pd
import numpy as np
from circuit import Circuit, Jacobian
from conductor import Conductor
from bus import Bus
from bundle import Bundle
from geometry import Geometry
from settings import Settings

pd.options.display.width = 0

# =============================
# Initialize the 7-Bus Circuit
# =============================
seven_circuit = Circuit('Seven Bus System')

# Buses with explicit types
seven_circuit.add_bus('Bus1', 125, bus_type='Slack')
seven_circuit.add_bus('Bus2', 230, bus_type='PQ')
seven_circuit.add_bus('Bus3', 230, bus_type='PQ')
seven_circuit.add_bus('Bus4', 230, bus_type='PQ')
seven_circuit.add_bus('Bus5', 230, bus_type='PQ')
seven_circuit.add_bus('Bus6', 230, bus_type='PV')  # Has a generator
seven_circuit.add_bus('Bus7', 18,  bus_type='PQ')

# =============================
# Transmission Line Setup
# =============================
partridge = Conductor("Partridge", 0.642 / 12, 0.0217, 0.385, 460)
seven_bundle = Bundle('test_bundle', 2, 1.5, partridge)
seven_geometry = Geometry("test_bundle", 0, 0, 18.5, 0, 37, 0)

seven_circuit.add_transmission_line("tLine1", seven_circuit.buses["Bus2"], seven_circuit.buses["Bus4"], seven_bundle, seven_geometry, 10)
seven_circuit.add_transmission_line("tLine2", seven_circuit.buses["Bus2"], seven_circuit.buses["Bus3"], seven_bundle, seven_geometry, 25)
seven_circuit.add_transmission_line("tLine3", seven_circuit.buses["Bus3"], seven_circuit.buses["Bus5"], seven_bundle, seven_geometry, 20)
seven_circuit.add_transmission_line("tLine4", seven_circuit.buses["Bus4"], seven_circuit.buses["Bus6"], seven_bundle, seven_geometry, 20)
seven_circuit.add_transmission_line("tLine5", seven_circuit.buses["Bus5"], seven_circuit.buses["Bus6"], seven_bundle, seven_geometry, 10)
seven_circuit.add_transmission_line("tLine6", seven_circuit.buses["Bus4"], seven_circuit.buses["Bus5"], seven_bundle, seven_geometry, 35)

# =============================
# Transformers
# =============================
seven_circuit.add_transformer('T1', seven_circuit.buses["Bus1"], seven_circuit.buses["Bus2"], 125, 8.5, 10)
seven_circuit.add_transformer('T2', seven_circuit.buses["Bus6"], seven_circuit.buses["Bus7"], 200, 10.5, 12)

# =============================
# Loads and Generators
# =============================
seven_circuit.add_load('load2', seven_circuit.buses["Bus2"], 0, 0)
seven_circuit.add_load('load3', seven_circuit.buses["Bus3"], 110, 50)
seven_circuit.add_load('load4', seven_circuit.buses["Bus4"], 100, 70)
seven_circuit.add_load('load5', seven_circuit.buses["Bus5"], 100, 65)
seven_circuit.add_load('load6', seven_circuit.buses["Bus6"], 0, 0)

seven_circuit.add_generator('generator1', seven_circuit.buses["Bus6"], 1.0, 200)

# =============================
# Jacobian Matrix Validation
# =============================
print("\n==========================")
print(" JACOBIAN VALIDATION TEST ")
print("==========================")

# Step 1: Flat-start voltage vector (V = 1∠0°)
voltages = np.array([
    bus.vpu * np.exp(1j * bus.delta)
    for bus in seven_circuit.buses.values()
])

# Step 2: Calculate Ybus
ybus = seven_circuit.calc_ybus()

# Step 3: Compute Jacobian matrix
jacobian = Jacobian(seven_circuit.buses, ybus, voltages)
J = jacobian.calc_jacobian()

# Step 4: Output
print("\nJacobian Matrix Shape:")
print(J.shape)

print("\nJacobian Matrix (rounded):")
print(np.round(J, 5))
