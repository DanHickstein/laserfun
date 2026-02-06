"""Test the get_beta_expansion method and updated soliton_number implementation."""

import sys
sys.path.insert(0, r'c:\Users\DanielHickstein\Documents\GitHub\laserfun')

from laserfun import Pulse, Fiber
from laserfun.tools import soliton_number
import numpy as np

print("=" * 70)
print("TESTING fiber.get_beta_expansion() METHOD")
print("=" * 70)
print()

# Test 1: GVD format - verify get_beta_expansion returns correct beta2
print("Test 1: get_beta_expansion() with GVD format")
print("-" * 70)
beta2_input = 0.025  # ps²/km
fiber_gvd = Fiber(
    gamma_W_m=0.01,
    dispersion_format='GVD',
    dispersion=[beta2_input * 1e-3]  # Convert to ps²/m
)

betas = fiber_gvd.get_beta_expansion(wavelength_nm=1550, orders=[2, 3])
print(f"  Input beta2: {beta2_input:.6f} ps²/km")
print(f"  Retrieved beta2: {betas['beta2']:.6f} ps²/km")
print(f"  Retrieved beta3: {betas['beta3']:.6e} ps³/km")
print(f"  Match: {np.isclose(beta2_input, betas['beta2'], rtol=0.01)}")
print()

# Test 2: D format - verify get_beta_expansion works
print("Test 2: get_beta_expansion() with D format")
print("-" * 70)
D = 20  # ps/(nm km)
wavelength = 1550  # nm
wavelengths = np.linspace(1500, 1600, 100)
D_values = np.ones_like(wavelengths) * D

fiber_D = Fiber(
    gamma_W_m=0.01,
    dispersion_format='D',
    dispersion=[wavelengths, D_values]
)

betas_D = fiber_D.get_beta_expansion(wavelength_nm=wavelength, orders=[2])
print(f"  Input D: {D} ps/(nm km)")
print(f"  Retrieved beta2: {betas_D['beta2']:.6f} ps²/km")

# Calculate expected beta2 from D
c = 3e5  # nm/ps
expected_beta2 = D * wavelength**2 / (2 * np.pi * c)
print(f"  Expected beta2: {expected_beta2:.6f} ps²/km")
print(f"  Match: {np.isclose(expected_beta2, betas_D['beta2'], rtol=0.05)}")
print()

# Test 3: Using get_beta_expansion with a pulse object
print("Test 3: get_beta_expansion() with Pulse object")
print("-" * 70)
pulse = Pulse(
    pulse_type='sech',
    center_wavelength_nm=1550,
    fwhm_ps=0.1,
    epp=100e-12
)

betas_with_pulse = fiber_gvd.get_beta_expansion(pulse=pulse, orders=[2, 3, 4])
print(f"  beta2: {betas_with_pulse['beta2']:.6f} ps²/km")
print(f"  beta3: {betas_with_pulse['beta3']:.6e} ps³/km")
print(f"  beta4: {betas_with_pulse['beta4']:.6e} ps⁴/km")
print()

# Test 4: Verify soliton_number still works with new implementation
print("Test 4: Pulse.soliton_number() with new get_beta_expansion()")
print("-" * 70)
N, L_D, L_NL = pulse.soliton_number(fiber_gvd)
print(f"  Soliton number: {N:.3f}")
print(f"  Dispersion length: {L_D:.3e} m")
print(f"  Nonlinear length: {L_NL:.3e} m")
print()

# Test 5: Compare with direct calculation
print("Test 5: Compare with direct tools.soliton_number() call")
print("-" * 70)
pulse_duration = pulse.calc_width(level=0.5)
pulse_energy_pJ = pulse.epp * 1e12
gamma_W_km = fiber_gvd.get_gamma(z=0) * 1e3

N_direct, L_D_direct, L_NL_direct = soliton_number(
    gamma=gamma_W_km,
    pulse_duration=pulse_duration,
    pulse_energy=pulse_energy_pJ,
    beta2=beta2_input
)

print(f"  Direct calculation:")
print(f"    Soliton number: {N_direct:.3f}")
print(f"    Dispersion length: {L_D_direct:.3e} m")
print(f"    Nonlinear length: {L_NL_direct:.3e} m")
print()
print(f"  Match with pulse.soliton_number(): {np.allclose([N, L_D, L_NL], [N_direct, L_D_direct, L_NL_direct], rtol=0.01)}")
print()

# Test 6: Test at different wavelengths
print("Test 6: get_beta_expansion() at different wavelengths")
print("-" * 70)
test_wavelengths = [1500, 1550, 1600]
for wl in test_wavelengths:
    betas_wl = fiber_D.get_beta_expansion(wavelength_nm=wl, orders=[2])
    expected = D * wl**2 / (2 * np.pi * c)
    print(f"  λ = {wl} nm: beta2 = {betas_wl['beta2']:.6f} ps²/km (expected: {expected:.6f})")
print()

print("=" * 70)
print("ALL TESTS COMPLETED!")
print("=" * 70)
