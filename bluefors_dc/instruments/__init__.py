"""
QCoDeS instrument drivers for Bluefors DC measurement system.

This module provides instrument drivers with preference for official drivers:
- AMI430: 2-axis magnet controller (official QCoDeS + custom fallback)
- Keithley 6221: Current source (custom - no official equivalent)
- Keithley 2182A: Nanovoltmeter (custom - no official equivalent)
- Keithley 2636B: Dual voltage source (official QCoDeS + custom fallback)
- Zurich MFLI: Lock-in amplifier (official drivers + custom fallback)
- Lakeshore 372: Temperature controller (official QCoDeS + custom fallback)
- BlueFors: Fridge monitoring (contrib)
- Lakeshore 331: Temperature controller (contrib)

MIGRATION NOTE: Custom drivers are deprecated in favor of official QCoDeS drivers.
"""

import warnings
import sys

# Import custom drivers for fallback
from .keithley import Keithley6221, Keithley2182A
from .ami430 import AMI430MagnetController as CustomAMI430
from .keithley import Keithley2636B as CustomKeithley2636B
from .zurich import ZurichMFLI as CustomZurichMFLI
from .lakeshore import Lakeshore372 as CustomLakeshore372

# Try to import official QCoDeS drivers
_OFFICIAL_DRIVERS_AVAILABLE = {}

# AMI430 from official QCoDeS
try:
    from qcodes.instrument_drivers.american_magnetics.AMI430 import AMI430 as AMI430MagnetController
    _OFFICIAL_DRIVERS_AVAILABLE['AMI430'] = True
except ImportError:
    AMI430MagnetController = CustomAMI430
    _OFFICIAL_DRIVERS_AVAILABLE['AMI430'] = False
    warnings.warn(
        "Using custom AMI430 driver. Install latest QCoDeS for official driver.",
        FutureWarning,
        stacklevel=2
    )

# Keithley 2636B from official QCoDeS
try:
    from qcodes.instrument_drivers.Keithley.Keithley_2636B import Keithley2636B
    _OFFICIAL_DRIVERS_AVAILABLE['Keithley2636B'] = True
except ImportError:
    Keithley2636B = CustomKeithley2636B
    _OFFICIAL_DRIVERS_AVAILABLE['Keithley2636B'] = False
    warnings.warn(
        "Using custom Keithley2636B driver. Install latest QCoDeS for official driver.",
        FutureWarning,
        stacklevel=2
    )

# Lakeshore 372 from official QCoDeS
try:
    from qcodes.instrument_drivers.Lakeshore.Model_372 import Model_372 as Lakeshore372
    _OFFICIAL_DRIVERS_AVAILABLE['Lakeshore372'] = True
except ImportError:
    Lakeshore372 = CustomLakeshore372
    _OFFICIAL_DRIVERS_AVAILABLE['Lakeshore372'] = False
    warnings.warn(
        "Using custom Lakeshore372 driver. Install latest QCoDeS for official driver.",
        FutureWarning,
        stacklevel=2
    )

# Zurich MFLI - prefer zhinst-qcodes, then official QCoDeS, then custom
ZhinstrumentsMFLI = None
ZurichMFLI = None

try:
    from zhinst.qcodes import MFLI as ZhinstrumentsMFLI
    ZurichMFLI = ZhinstrumentsMFLI
    _OFFICIAL_DRIVERS_AVAILABLE['ZhinstrumentsMFLI'] = True
    _OFFICIAL_DRIVERS_AVAILABLE['ZurichMFLI'] = True
except ImportError:
    _OFFICIAL_DRIVERS_AVAILABLE['ZhinstrumentsMFLI'] = False
    # Try to fall back to official QCoDeS zurich instruments driver
    # Note: The official driver requires zhinst-toolkit, so it may not be available
    try:
        from qcodes.instrument_drivers.zurich_instruments import ZIUHFLI
        # For now, keep using custom driver as the official one has different interface
        ZurichMFLI = CustomZurichMFLI
        _OFFICIAL_DRIVERS_AVAILABLE['ZurichMFLI'] = False
        warnings.warn(
            "Using custom Zurich MFLI driver. Install zhinst-qcodes for full functionality.",
            FutureWarning,
            stacklevel=2
        )
    except ImportError:
        ZurichMFLI = CustomZurichMFLI
        _OFFICIAL_DRIVERS_AVAILABLE['ZurichMFLI'] = False
        warnings.warn(
            "Using custom Zurich MFLI driver. Install zhinst-qcodes for official drivers.",
            FutureWarning,
            stacklevel=2
        )

# QCoDeS contrib drivers
try:
    from qcodes_contrib_drivers.drivers.BlueFors.BlueFors import BlueFors
    _BLUEFORS_AVAILABLE = True
except ImportError:
    _BLUEFORS_AVAILABLE = False
    BlueFors = None

try:
    from qcodes_contrib_drivers.drivers.Lakeshore.Model_331 import Model_331 as Lakeshore331
    _LAKESHORE331_AVAILABLE = True
except ImportError:
    _LAKESHORE331_AVAILABLE = False
    Lakeshore331 = None

# Base exports (always available)
__all__ = [
    'AMI430MagnetController',
    'Keithley6221',
    'Keithley2182A', 
    'Keithley2636B',
    'ZurichMFLI',
    'Lakeshore372',
]

# Add official Zurich Instruments drivers to exports if available
if _OFFICIAL_DRIVERS_AVAILABLE.get('ZhinstrumentsMFLI'):
    __all__.append('ZhinstrumentsMFLI')

# Add contrib drivers to exports if available
if _BLUEFORS_AVAILABLE:
    __all__.append('BlueFors')
    
if _LAKESHORE331_AVAILABLE:
    __all__.append('Lakeshore331')

# Migration status information
def get_driver_status():
    """Get status of official vs custom drivers."""
    return {
        'official_drivers_available': _OFFICIAL_DRIVERS_AVAILABLE,
        'contrib_drivers_available': {
            'BlueFors': _BLUEFORS_AVAILABLE,
            'Lakeshore331': _LAKESHORE331_AVAILABLE,
        }
    }