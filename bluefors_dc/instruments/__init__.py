"""
QCoDeS instrument drivers for Bluefors DC measurement system.

This module provides instrument drivers for:
- AMI430: 2-axis magnet controller (custom)
- Keithley 6221: Current source (custom)
- Keithley 2182A: Nanovoltmeter (custom)
- Keithley 2636B: Dual voltage source (custom)
- Zurich MFLI: Lock-in amplifier (zhinst-qcodes + custom fallback)
- Lakeshore 372: Temperature controller (custom)
- BlueFors: Fridge monitoring (contrib)
- Lakeshore 331: Temperature controller (contrib)
"""

# Custom drivers
from .ami430 import AMI430MagnetController
from .keithley import Keithley6221, Keithley2182A, Keithley2636B
from .zurich import ZurichMFLI
from .lakeshore import Lakeshore372

# Zurich Instruments official drivers
try:
    from zhinst.qcodes import MFLI as ZhinstrumentsMFLI
    _ZHINST_QCODES_AVAILABLE = True
except ImportError:
    _ZHINST_QCODES_AVAILABLE = False
    ZhinstrumentsMFLI = None

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
if _ZHINST_QCODES_AVAILABLE:
    __all__.append('ZhinstrumentsMFLI')

# Add contrib drivers to exports if available
if _BLUEFORS_AVAILABLE:
    __all__.append('BlueFors')
    
if _LAKESHORE331_AVAILABLE:
    __all__.append('Lakeshore331')