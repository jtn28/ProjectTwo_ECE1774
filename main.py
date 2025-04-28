import pandas as pd
import numpy as np
from circuit import Circuit, Jacobian
from conductor import Conductor
from bus import Bus
from bundle import Bundle
from geometry import Geometry
from solution import Solution
from solution import SymFaultSolver
from solution import AsymFaultSolver

pd.options.display.width = 0

# =============================
# Initialize the 7-Bus Circuit
# =============================
seven_circuit = Circuit('Seven Bus System', 'Fault_Study', "LL", base_mva=100.0)

# Buses (types matched to diagram + data)
seven_circuit.add_bus('Bus1', 125, bus_type='Slack')
seven_circuit.add_bus('Bus2', 230, bus_type='PQ')
seven_circuit.add_bus('Bus3', 230, bus_type='PQ')
seven_circuit.add_bus('Bus4', 230, bus_type='PQ')
seven_circuit.add_bus('Bus5', 230, bus_type='PQ')
seven_circuit.add_bus('Bus6', 230, bus_type='PQ')  # Was PV, should be PQ
seven_circuit.add_bus('Bus7', 18,  vpu=1.0, bus_type='PV')  # Bus7 is the generator bus

# =============================
# Transmission Lines
# =============================

partridge = Conductor("Partridge", 0.642 / 12, 0.0217, 0.385, 460)
seven_bundle = Bundle('test_bundle', 2, 1.5, partridge)
seven_geometry = Geometry("test_bundle", 0, 0, 18.5, 0, 37, 0)

seven_circuit.add_transmission_line("L1", seven_circuit.buses["Bus2"], seven_circuit.buses["Bus4"], seven_bundle, seven_geometry, 10)
seven_circuit.add_transmission_line("L2", seven_circuit.buses["Bus2"], seven_circuit.buses["Bus3"], seven_bundle, seven_geometry, 25)
seven_circuit.add_transmission_line("L3", seven_circuit.buses["Bus3"], seven_circuit.buses["Bus5"], seven_bundle, seven_geometry, 20)
seven_circuit.add_transmission_line("L4", seven_circuit.buses["Bus4"], seven_circuit.buses["Bus6"], seven_bundle, seven_geometry, 20)
seven_circuit.add_transmission_line("L5", seven_circuit.buses["Bus5"], seven_circuit.buses["Bus6"], seven_bundle, seven_geometry, 10)
seven_circuit.add_transmission_line("L6", seven_circuit.buses["Bus4"], seven_circuit.buses["Bus5"], seven_bundle, seven_geometry, 35)

# =============================
# Transformers
# =============================
seven_circuit.add_transformer('T1', seven_circuit.buses["Bus1"], seven_circuit.buses["Bus2"], 125, 8.5, 10)
seven_circuit.add_transformer('T2', seven_circuit.buses["Bus7"], seven_circuit.buses["Bus6"], 200, 10.5, 12)

# =============================
# Loads and Generators
# =============================
seven_circuit.add_load('load3', seven_circuit.buses["Bus3"], 110, 50)
seven_circuit.add_load('load4', seven_circuit.buses["Bus4"], 100, 70)
seven_circuit.add_load('load5', seven_circuit.buses["Bus5"], 100, 65)

# Bus 7 has generator output (PV type: 200 MW, V = 1.0 pu)
seven_circuit.add_generator('generator1', seven_circuit.buses["Bus1"], voltage_setpoint=1.0, mw_setpoint=200,
                            x0=0.05, x1=0.12, x2=0.14, ground_imp=0+0j, isGrounded=True)
seven_circuit.add_generator('generator2', seven_circuit.buses["Bus7"], voltage_setpoint=1.0, mw_setpoint=200,
                            x0=0.05, x1=0.12, x2=0.14, ground_imp=1+0j, isGrounded=True)

# =============================
# Print Per-Unit Info
# =============================
print("\n============================")
print(" Per-Unit Transformer Data ")
print("============================")
for tf_key, tf in seven_circuit.transformers.items():
    print(f"{tf.name}: Rpu = {tf.rpu:.5f}, Xpu = {tf.xpu:.5f}")

print("\n==============================")
print(" Per-Unit Transmission Line Data")
print("==============================")
for key, line in seven_circuit.transmission_lines.items():
    zpu = line.calculate_zpu()
    ypu = line.calculate_ypu()
    r = zpu.real
    x = zpu.imag
    b = ypu.imag
    print(f"{line.name}: R = {r:.5f} pu, X = {x:.5f} pu, B = {b:.5f} pu")

# =============================
# Ybus Matrix Output
# =============================
if seven_circuit.analysis_mode == 'Power_Flow':
    print("\n===================")
    print(" Ybus Admittance Matrix (Rounded)")
    print("===================")
    ybus = seven_circuit.calc_ybus()
    print(ybus.round(5).to_string())
# =============================
# Fault Ybus Matrix Output
# =============================
elif seven_circuit.analysis_mode == 'Fault_Study':
    print("\n===================")
    print(" Fault Positive Ybus Admittance Matrix (Rounded)")
    print("===================")
    ybus = seven_circuit.calc_zbus_sequence()
    print(ybus.round(5).to_string())
    print("\n===================")
    print(" Fault Negative Ybus Admittance Matrix (Rounded)")
    print("===================")
    ybus = seven_circuit.calc_zbus_sequence("neg")
    print(ybus.round(5).to_string())
    print("\n===================")
    print(" Fault Zero Ybus Admittance Matrix (Rounded)")
    print("===================")
    ybus = seven_circuit.calc_zbus_sequence("zero")
    print(ybus.round(5).to_string())
else:
    raise ValueError("Invalid Analysis Mode")

# =============================
# JACOBIAN VALIDATION TEST
# =============================
print("\n==========================")
print(" JACOBIAN VALIDATION TEST ")
print("==========================")

voltages = np.array([
    bus.vpu * np.exp(1j * bus.delta)
    for bus in seven_circuit.buses.values()
])
jacobian = Jacobian(seven_circuit.buses, ybus, voltages)
jacobian_df = jacobian.get_jacobian_dataframe()
print("\nJacobian Matrix Shape:", jacobian_df.shape)
print(jacobian_df.to_string())

# =============================
# Symmetric Faults
# =============================
if seven_circuit.analysis_mode == 'Fault_Study' and seven_circuit.fault_type == 'SYM':
    print("\n==============================")
    print(" Symmetric Faults Test")
    print("==============================")
    # Run NR to get V_pre
    solver = Solution(seven_circuit)
    voltages_solution = solver.newton_raphson()

    # Simulate symmetrical fault at Bus3
    fault_solver = SymFaultSolver(seven_circuit, voltages_solution)
    fault_results = fault_solver.apply_fault("Bus3")

    # Output
    print("\n--- Symmetrical Fault at Bus 3 ---")
    print(f"Fault current: {fault_results['fault_current']:.4f}")
    print("Voltages during fault:")
    for name, V in zip(seven_circuit.buses.keys(), fault_results['voltage_during_fault']):
        print(f"{name}: |V| = {abs(V):.4f} pu, ∠ = {np.angle(V, deg=True):.2f}°")
elif seven_circuit.analysis_mode == 'Fault_Study' and seven_circuit.fault_type != 'SYM':
    print("\n==============================")
    print(" Asymmetric Faults Test")
    print("==============================")
    # Run NR to get V_pre
    solver = Solution(seven_circuit)
    voltages_solution = solver.newton_raphson()

    # Simulate symmetrical fault at Bus3
    fault_solver = AsymFaultSolver(seven_circuit, voltages_solution, seven_circuit.fault_type)
    fault_results = fault_solver.run_fault_analysis("Bus3")
    phasor_outputs = fault_results['V_phase_phasors']
    # Output
    print(f"\n--- Asymmetrical Fault at Bus 3 ---")
    print(f"Fault type: {seven_circuit.fault_type}")
    print(f"Positive Fault current: {fault_results['I_pos']:.4f}")
    print(f"Negative Fault current: {fault_results['I_neg']:.4f}")
    print(f"Zero Fault current: {fault_results['I_zero']:.4f}")
    print("Voltages at bus fault:")
    print(f"Positive Fault current: {fault_results['V_pos']:.4f}")
    print(f"Negative Fault current: {fault_results['V_neg']:.4f}")
    print(f"Zero Fault current: {fault_results['V_zero']:.4f}")
    print(f"Phasor representation of phase at fault")
    phase_labels =['V pos', 'V neg', 'V zero']
    for phase_labels, (mag, angle) in zip(phase_labels, phasor_outputs):
        print(f"{phase_labels}: {mag:.4f} ∠ {angle:.2f}°")

if seven_circuit.analysis_mode == "Power_Flow":
    print("\n==============================")
    print(" Newton-Raphson Power Flow Test")
    print("==============================")
    solver = Solution(seven_circuit)
    voltages_solution = solver.newton_raphson(max_iter=10, tol=1e-9)

    # Step 4: Final Result
    print("\nFinal Voltage Magnitudes and Angles:")
    for name, v in zip(seven_circuit.buses.keys(), voltages_solution):
        mag = np.abs(v)
        angle = np.angle(v, deg=True)
        print(f"{name}: |V| = {mag:.4f} pu, ∠ = {angle:.2f}°")


