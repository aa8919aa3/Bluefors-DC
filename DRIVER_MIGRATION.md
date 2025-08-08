# Driver Migration Guide

This document describes the migration from custom drivers to official QCoDeS drivers in the Bluefors-DC package.

## Migration Status

### Official QCoDeS Drivers (Preferred)

| Instrument | Custom Driver | Official Driver | Status | Module |
|------------|---------------|----------------|--------|---------|
| AMI430 | `AMI430MagnetController` | `AMI430` | ✅ **Migrated** | `qcodes.instrument_drivers.american_magnetics.AMI430` |
| Keithley 2636B | `Keithley2636B` | `Keithley2636B` | ✅ **Migrated** | `qcodes.instrument_drivers.Keithley.Keithley_2636B` |
| Lakeshore 372 | `Lakeshore372` | `Model_372` | ✅ **Migrated** | `qcodes.instrument_drivers.Lakeshore.Model_372` |

### Custom Drivers (No Official Equivalent)

| Instrument | Driver | Status | Reason |
|------------|--------|--------|---------|
| Keithley 6221 | `Keithley6221` | ⚠️ **Custom Only** | No official QCoDeS driver available |
| Keithley 2182A | `Keithley2182A` | ⚠️ **Custom Only** | No official QCoDeS driver available |

### Zurich Instruments (Special Case)

| Driver Source | Driver | Status | Notes |
|---------------|--------|--------|-------|
| zhinst-qcodes | `MFLI` | ✅ **Preferred** | Professional support, full functionality |
| Custom fallback | `ZurichMFLI` | ⚠️ **Fallback** | Basic functionality only |

### Contrib Drivers

| Instrument | Driver | Status | Module |
|------------|--------|--------|---------|
| BlueFors Fridge | `BlueFors` | ✅ **Available** | `qcodes_contrib_drivers.drivers.BlueFors.BlueFors` |
| Lakeshore 331 | `Lakeshore331` | ✅ **Available** | `qcodes_contrib_drivers.drivers.Lakeshore.Model_331` |

## Usage

### Automatic Driver Selection

The package automatically selects the best available driver:

```python
from bluefors_dc.instruments import AMI430MagnetController, Keithley2636B

# Uses qcodes.instrument_drivers.american_magnetics.AMI430 if available
# Falls back to custom driver if not
magnet = AMI430MagnetController('magnet', 'TCPIP::192.168.1.100::7180::SOCKET')

# Uses qcodes.instrument_drivers.Keithley.Keithley_2636B if available  
# Falls back to custom driver if not
smu = Keithley2636B('smu', 'TCPIP::192.168.1.105::INSTR')
```

### Check Driver Status

```python
from bluefors_dc.instruments import get_driver_status

status = get_driver_status()
print("Official drivers:", status['official_drivers_available'])
print("Contrib drivers:", status['contrib_drivers_available'])
```

## Migration Benefits

### For Users

1. **No Code Changes Required**: Your existing code continues to work
2. **Automatic Updates**: Get latest driver improvements automatically
3. **Better Support**: Official drivers are professionally maintained
4. **Enhanced Features**: Access to latest instrument capabilities

### For Developers

1. **Reduced Maintenance**: No need to maintain custom drivers where official ones exist
2. **Better Integration**: Official drivers integrate better with QCoDeS ecosystem
3. **Consistent APIs**: Standardized parameter names and validation
4. **Documentation**: Professional documentation and examples

## Installation

### Basic Installation (Custom + Contrib Drivers)

```bash
pip install bluefors-dc
```

### With Zurich Instruments Support

```bash
pip install bluefors-dc[zhinst]
# or
pip install zhinst-qcodes
```

### Development Installation

```bash
pip install bluefors-dc[dev,zhinst]
```

## Deprecation Warnings

Custom drivers that have official equivalents now show deprecation warnings:

```
FutureWarning: Using custom AMI430 driver. Install latest QCoDeS for official driver.
```

These warnings can be suppressed but it's recommended to ensure you have the latest QCoDeS version.

## Driver-Specific Migration Notes

### AMI430 Magnet Controller

**Official Driver**: `qcodes.instrument_drivers.american_magnetics.AMI430.AMI430`

**Changes**:
- Some parameter names may differ
- The official driver uses `has_current_rating` parameter (deprecated but harmless)
- Enhanced safety features and field limit validation

**Example**:
```python
# Same import - automatic selection
from bluefors_dc.instruments import AMI430MagnetController

magnet = AMI430MagnetController('magnet', 'TCPIP::192.168.1.100::7180::SOCKET')
```

### Keithley 2636B

**Official Driver**: `qcodes.instrument_drivers.Keithley.Keithley_2636B.Keithley2636B`

**Changes**:
- Inherits from official Keithley base classes
- Better parameter validation and error handling
- Enhanced compliance and safety features

### Lakeshore 372

**Official Driver**: `qcodes.instrument_drivers.Lakeshore.Model_372.Model_372`

**Changes**:
- Standardized channel naming
- Better temperature sensor support
- Enhanced control loop parameters

### Zurich MFLI

**Preferred Driver**: `zhinst.qcodes.MFLI` (from zhinst-qcodes package)

**Installation**:
```bash
pip install zhinst-qcodes
```

**Benefits**:
- Full access to Zurich Toolkit functionality
- Professional support from Zurich Instruments
- Advanced measurement modes and analysis tools
- Regular updates with new device features

## Troubleshooting

### Official Driver Not Found

If you see warnings about custom drivers being used:

1. **Update QCoDeS**:
   ```bash
   pip install --upgrade qcodes
   ```

2. **Check QCoDeS Version**:
   ```python
   import qcodes
   print(qcodes.__version__)
   ```

3. **Verify Driver Exists**:
   ```python
   from bluefors_dc.instruments import get_driver_status
   print(get_driver_status())
   ```

### Zurich Instruments Issues

For Zurich instruments, install the official package:

```bash
pip install zhinst-qcodes
```

If you encounter issues, the custom driver provides fallback functionality.

### Parameter Name Changes

Official drivers may have different parameter names. Check the driver documentation or use:

```python
instrument.parameters.keys()  # List all parameters
```

## Future Plans

1. **Complete Migration**: All instruments with official drivers will migrate
2. **Custom Driver Deprecation**: Custom drivers will be removed in future versions where official equivalents exist
3. **Enhanced Testing**: Comprehensive testing with official drivers
4. **Documentation Updates**: Full documentation aligned with official drivers

For questions or issues related to the migration, please open an issue on the project repository.