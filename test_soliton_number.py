"""Test the simplified soliton_number implementation."""

import sys
sys.path.insert(0, r'c:\Users\DanielHickstein\Documents\GitHub\laserfun')

from laserfun import Pulse, Fiber
from laserfun.tools import soliton_number
import numpy as np

print("=" * 70)
print("SOLITON NUMBER TESTS - SIMPLIFIED IMPLEMENTATION")
print("=" * 70)
print()

# Test 1: Basic function with D parameter
print("Test 1: Basic function with D parameter")
print("-" * 70)
gamma = 10  # 1/(W km)
pulse_duration = 0.1  # ps
pulse_energy = 100  # pJ
D = 20  # ps/(nm km)
wavelength = 1550  # nm

N, L_D, L_NL = soliton_number(gamma, pulse_duration, pulse_energy, D=D, wavelength=wavelength)
print(f"  Soliton number: {N:.3f}")
print(f"  Dispersion length: {L_D:.3e} m")
print(f"  Nonlinear length: {L_NL:.3e} m")
print()

# Test 2: Basic function with beta2 parameter
print("Test 2: Basic function with beta2 parameter")
print("-" * 70)
# Calculate equivalent beta2 from D
c = 3e5  # nm/ps
beta2 = D * wavelength**2 / (2 * np.pi * c)  # ps²/km

N2, L_D2, L_NL2 = soliton_number(gamma, pulse_duration, pulse_energy, beta2=beta2)
print(f"  Soliton number: {N2:.3f}")
print(f"  Dispersion length: {L_D2:.3e} m")
print(f"  Nonlinear length: {L_NL2:.3e} m")
print(f"  Match with Test 1: {np.allclose([N, L_D, L_NL], [N2, L_D2, L_NL2])}")
print()

# Test 3: Pulse.soliton_number() with Fiber (GVD format)
print("Test 3: Pulse.soliton_number() with Fiber (GVD format)")
print("-" * 70)
pulse = Pulse(
    pulse_type='sech',
    center_wavelength_nm=1550,
    fwhm_ps=0.1,
    epp=100e-12  # 100 pJ
)

fiber_gvd = Fiber(
    gamma_W_m=0.01,  # 10 1/(W km)
    dispersion_format='GVD',
    dispersion=[beta2 * 1e-3]  # Convert ps²/km to ps²/m
)

N3, L_D3, L_NL3 = pulse.soliton_number(fiber_gvd)
print(f"  Soliton number: {N3:.3f}")
print(f"  Dispersion length: {L_D3:.3e} m")
print(f"  Nonlinear length: {L_NL3:.3e} m")
print(f"  Match with Test 1: {np.allclose([N, L_D, L_NL], [N3, L_D3, L_NL3], rtol=0.01)}")
print()

# Test 4: Pulse.soliton_number() with Fiber (D format)
print("Test 4: Pulse.soliton_number() with Fiber (D format)")
print("-" * 70)
wavelengths = np.linspace(1500, 1600, 100)
D_values = np.ones_like(wavelengths) * D  # Constant D

fiber_D = Fiber(
    gamma_W_m=0.01,
    dispersion_format='D',
    dispersion=[wavelengths, D_values]
)

N4, L_D4, L_NL4 = pulse.soliton_number(fiber_D)
print(f"  Soliton number: {N4:.3f}")
print(f"  Dispersion length: {L_D4:.3e} m")
print(f"  Nonlinear length: {L_NL4:.3e} m")
print(f"  Match with Test 1: {np.allclose([N, L_D, L_NL], [N4, L_D4, L_NL4], rtol=0.01)}")
print()

# Test 5: Error handling - no D or beta2
print("Test 5: Error handling - neither D nor beta2 provided")
print("-" * 70)
try:
    soliton_number(gamma, pulse_duration, pulse_energy)
    print("  ERROR: Should have raised ValueError!")
except ValueError as e:
    print(f"  ✓ Correctly raised ValueError: {e}")
print()

# Test 6: Error handling - both D and beta2
print("Test 6: Error handling - both D and beta2 provided")
print("-" * 70)
try:
    soliton_number(gamma, pulse_duration, pulse_energy, D=D, beta2=beta2)
    print("  ERROR: Should have raised ValueError!")
except ValueError as e:
    print(f"  ✓ Correctly raised ValueError: {e}")
print()

print("=" * 70)
print("ALL TESTS COMPLETED!")
print("=" * 70)
