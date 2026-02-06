# Soliton Number Implementation - Final Version

## Overview

Implemented a clean, well-organized interface for calculating soliton number with proper separation of concerns:

1. **`Fiber.get_beta_expansion()`**: New method in `Fiber` class to get beta coefficients
2. **`tools.soliton_number()`**: Accepts either `beta2` or `D` parameter
3. **`Pulse.soliton_number()`**: Simple method using `fiber.get_beta_expansion()`

## Architecture

### Design Principle: Separation of Concerns
- **Fiber class**: Responsible for providing its own dispersion parameters
- **Pulse class**: Uses fiber's methods to get needed parameters
- **Tools module**: Contains the core calculation logic

This follows good object-oriented design principles!

## Implementation Details

### 1. New `Fiber.get_beta_expansion()` Method

**Location**: `laserfun/fiber.py`, after line 201

**Purpose**: Calculate beta expansion coefficients (beta2, beta3, etc.) at any wavelength

**Key Features**:
- Works with **all** fiber dispersion formats (GVD, D, or n)
- Can calculate multiple orders: beta2, beta3, beta4, etc.
- Can use an existing pulse or create a temporary one
- Returns dictionary with beta coefficients in ps^n/km

**Signature**:
```python
def get_beta_expansion(self, pulse=None, wavelength_nm=None, z=0, orders=[2, 3]):
    """Get the beta expansion coefficients at a wavelength.
    
    Parameters
    ----------
    pulse : Pulse, optional
        Pulse object for frequency grid. If None, creates temporary pulse.
    wavelength_nm : float, optional
        Wavelength in nm. If None, uses fiber's center wavelength.
    z : float, optional
        Position along fiber in meters. Default is 0.
    orders : list of int, optional
        Which orders to calculate (e.g., [2, 3]). Default is [2, 3].
    
    Returns
    -------
    betas : dict
        Dictionary like {'beta2': ..., 'beta3': ...} in ps^n/km
    """
```

**How it works**:
1. Creates or uses pulse for frequency grid
2. Calls `self.get_B(pulse, z)` to get propagation constant B(ω)
3. Takes numerical derivatives using `np.gradient()`
4. Converts units from THz^n/m to ps^n/km
5. Returns dictionary of beta coefficients

**Example usage**:
```python
fiber = Fiber(dispersion_format='GVD', dispersion=[0.02])

# Get beta2 and beta3 at 1550 nm
betas = fiber.get_beta_expansion(wavelength_nm=1550, orders=[2, 3])
print(f"beta2 = {betas['beta2']:.3f} ps²/km")
print(f"beta3 = {betas['beta3']:.3e} ps³/km")

# Or use with a pulse object
pulse = Pulse(center_wavelength_nm=1550, fwhm_ps=0.1)
betas = fiber.get_beta_expansion(pulse=pulse, orders=[2, 3, 4])
```

### 2. Updated `tools.soliton_number()` Function

**Location**: `laserfun/tools.py`, line 320

**Changes**: Now accepts either `D` or `beta2` (with validation)

**Signature**:
```python
def soliton_number(gamma, pulse_duration, pulse_energy, D=None, beta2=None, wavelength=1560):
    """Calculate soliton number, nonlinear length, and dispersion length.
    
    Either D or beta2 must be provided, but not both.
    """
```

### 3. Simplified `Pulse.soliton_number()` Method

**Location**: `laserfun/pulse.py`, line 520

**Now much simpler**:
```python
def soliton_number(self, fiber):
    # Extract pulse parameters
    pulse_duration_ps = self.calc_width(level=0.5)
    pulse_energy_pJ = self.epp * 1e12
    gamma_W_km = fiber.get_gamma(z=0) * 1e3
    
    # Get beta2 from fiber - this is the key simplification!
    betas = fiber.get_beta_expansion(pulse=self, orders=[2])
    beta2_ps2_per_km = betas['beta2']
    
    # Call tools function
    return tools.soliton_number(
        gamma=gamma_W_km,
        pulse_duration=pulse_duration_ps,
        pulse_energy=pulse_energy_pJ,
        beta2=beta2_ps2_per_km
    )
```

**Reduced from ~30 lines to ~15 lines** by delegating to `fiber.get_beta_expansion()`!

## Usage Examples

### Example 1: Get beta expansion from fiber
```python
from laserfun import Fiber

fiber = Fiber(
    dispersion_format='D',
    dispersion=[wavelengths, D_values]
)

# Get beta2 and beta3 at 1550 nm
betas = fiber.get_beta_expansion(wavelength_nm=1550, orders=[2, 3])
print(f"beta2 = {betas['beta2']:.3f} ps²/km")
print(f"beta3 = {betas['beta3']:.3e} ps³/km")
```

### Example 2: Calculate soliton number
```python
from laserfun import Pulse, Fiber

pulse = Pulse(fwhm_ps=0.1, center_wavelength_nm=1550, epp=100e-12)
fiber = Fiber(gamma_W_m=0.01, dispersion_format='GVD', dispersion=[0.025e-3])

N, L_D, L_NL = pulse.soliton_number(fiber)
print(f"Soliton number: {N:.3f}")
```

### Example 3: Direct calculation with beta2
```python
from laserfun.tools import soliton_number

N, L_D, L_NL = soliton_number(
    gamma=10,           # 1/(W km)
    pulse_duration=0.1, # ps
    pulse_energy=100,   # pJ
    beta2=0.025        # ps²/km
)
```

### Example 4: Direct calculation with D
```python
from laserfun.tools import soliton_number

N, L_D, L_NL = soliton_number(
    gamma=10,           # 1/(W km)
    pulse_duration=0.1, # ps
    pulse_energy=100,   # pJ
    D=20,              # ps/(nm km)
    wavelength=1550    # nm
)
```

## Benefits of This Design

### 1. Separation of Concerns ✨
- **Fiber class** owns its dispersion parameters
- **Pulse class** delegates to fiber for dispersion info
- **Tools module** contains pure calculation logic

### 2. Reusability 🔄
- `get_beta_expansion()` is useful beyond soliton calculations
- Can be used for any application needing beta coefficients
- Works at any wavelength, not just pulse center wavelength

### 3. Maintainability 🛠️
- Dispersion extraction logic in one place (`Fiber` class)
- No duplication of derivative calculations
- Easy to test each component independently

### 4. Flexibility 💪
- Works with all fiber formats (GVD, D, n)
- Can get any order of beta (beta2, beta3, beta4, ...)
- Can evaluate at any wavelength

### 5. Clean API 🎯
- Simple method calls: `fiber.get_beta_expansion()`, `pulse.soliton_number(fiber)`
- Intuitive: ask the fiber for its properties
- Self-documenting code

## Unit Conversions

### In `Fiber.get_beta_expansion()`:
- Takes derivatives in THz^n/m
- Converts to ps^n/km using:
  ```
  conversion = (2π × 10¹²)^n × (10⁻¹²)^n × 10³
  ```
  where n is the order (2, 3, 4, ...)

### In `Pulse.soliton_number()`:
- Gamma: 1/(W m) → 1/(W km) (multiply by 1000)
- Energy: J → pJ (multiply by 10¹²)
- Beta2: Already in ps²/km from `get_beta_expansion()`

### In `tools.soliton_number()`:
- If D provided: D (ps/nm/km) → beta2 (ps²/km)
- beta2 (ps²/km) → beta2 (ps²) (divide by 1000)

## Testing

Created `test_beta_expansion.py` with tests for:
1. `get_beta_expansion()` with GVD format
2. `get_beta_expansion()` with D format
3. Using `get_beta_expansion()` with pulse object
4. `pulse.soliton_number()` with new implementation
5. Comparison with direct `tools.soliton_number()` call
6. Beta expansion at different wavelengths

## Summary of Changes

### Files Modified:
1. **`laserfun/fiber.py`**: Added `get_beta_expansion()` method (~95 lines)
2. **`laserfun/tools.py`**: Updated `soliton_number()` to accept beta2 or D
3. **`laserfun/pulse.py`**: Simplified `soliton_number()` to use `fiber.get_beta_expansion()`

### Lines of Code:
- **Before**: ~70 lines in `Pulse.soliton_number()`
- **After**: ~15 lines in `Pulse.soliton_number()` + 95 lines in `Fiber.get_beta_expansion()`
- **Net**: More total lines, but better organized and reusable!

### Key Improvement:
The `get_beta_expansion()` method is a **general-purpose utility** that will be useful for many other applications beyond soliton calculations. This is good software design!
