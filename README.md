# Bluefors DC Measurements - Python/QCoDeS Implementation

This repository contains a complete Python/QCoDeS implementation of measurement protocols originally developed in LabVIEW for the Bluefors LD-400 dilution refrigerator system. The migration provides modern measurement capabilities with improved safety, data management, and analysis tools.

## Overview

This package provides Python/QCoDeS equivalents for all LabVIEW VIs, implementing:

- **Current-Voltage (I-V) Measurements**: High-precision resistance measurements
- **Differential Conductance (dI-dV)**: Lock-in based spectroscopy measurements  
- **Transport Measurements**: Hall resistance, temperature-dependent resistance
- **Vector Magnetic Field Control**: 2-axis field sweeps and angle-dependent measurements
- **Real-time Monitoring**: Continuous measurement capabilities
- **Safety Interlocks**: Comprehensive parameter validation and protection

## Supported Instruments

### Control Electronics
- **AMI 430**: 2-axis vector magnet controller (up to 9T) - *custom driver*
- **Lakeshore 372**: AC resistance bridge temperature controller (16 channels) - *custom driver*
- **Lakeshore 331**: Basic temperature controller (2 channels) - *contrib driver*

### Measurement Electronics  
- **Keithley 6221**: Current source with delta mode capability - *custom driver*
- **Keithley 2182A**: Nanovoltmeter for high-precision voltage measurement - *custom driver*
- **Keithley 2636B**: Dual channel source-measure unit - *custom driver*
- **Zurich Instruments MFLI**: Lock-in amplifier with harmonic analysis - *official zhinst-qcodes driver + custom fallback*

### Monitoring and Control
- **BlueFors**: Fridge monitoring via log files - *contrib driver*

## Installation

```bash
# Clone the repository
git clone https://github.com/aa8919aa3/Bluefors-DC.git
cd Bluefors-DC

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e .[dev]

# Or install with official Zurich Instruments drivers
pip install -e .[zhinst]

# Or install with both dev and Zurich Instruments drivers
pip install -e .[dev,zhinst]
```

## Quick Start

### Basic I-V Measurement with Contrib Drivers

```python
from bluefors_dc.measurements import BlueforsStation, IVMeasurement, IVSweepParameters
from bluefors_dc.instruments import BlueFors  # Contrib driver

# Set up station with instruments
station = BlueforsStation()
station.add_current_source('TCPIP::192.168.1.101::INSTR')
station.add_nanovoltmeter('TCPIP::192.168.1.102::INSTR')

# Add fridge monitoring (contrib driver)
fridge = BlueFors(
    name="bluefors_fridge",
    folder_path="/path/to/bluefors/logs",
    channel_vacuum_can=1,
    channel_pumping_line=2,
    # ... other channel configurations
    channel_mixing_chamber=4
)

# Configure and run measurement
iv_measurement = IVMeasurement(station)
params = IVSweepParameters(
    start_current=-1e-6,  # -1 μA
    stop_current=1e-6,    # +1 μA  
    num_points=101,
    compliance_voltage=10.0
)

# Monitor temperature during measurement
temp_before = fridge.temperature_mixing_chamber()
data = iv_measurement.run_sweep(params)
temp_after = fridge.temperature_mixing_chamber()

print(f"Temperature drift: {temp_after - temp_before:.3f} K")
print(f"Average resistance: {np.mean(data['resistance']):.3e} Ω")
```

### Using Multiple Temperature Controllers

```python
from bluefors_dc.instruments import Lakeshore372, Lakeshore331  # Custom + contrib

# High-precision AC resistance bridge (16 channels)
lakeshore_372 = Lakeshore372(name="temp_primary", address="TCPIP::192.168.1.110::INSTR")

# Basic temperature controller (2 channels)  
lakeshore_331 = Lakeshore331(name="temp_secondary", address="GPIB0::12::INSTR")

# Use both controllers in measurement
sample_temp = lakeshore_372.temperature()  # High precision
setpoint_temp = lakeshore_331.A.temperature()  # Basic monitoring
```

### Differential Conductance Measurement

```python
from bluefors_dc.measurements import DifferentialConductance, DifferentialParameters

# Add lock-in amplifier
station.add_dual_smu('TCPIP::192.168.1.103::INSTR')  
station.add_lock_in('dev1234')

# Run dI/dV measurement
diff_measurement = DifferentialConductance(station)
params = DifferentialParameters(
    start_voltage=-0.01,    # -10 mV
    stop_voltage=0.01,      # +10 mV
    num_points=201,
    ac_amplitude=0.001,     # 1 mV modulation
    frequency=1000.0        # 1 kHz
)

data = diff_measurement.run_sweep(params)
```

## Key Features

### 🎯 QCoDeS Contrib Drivers Integration
- **Extended instrument support**: Access to 50+ additional drivers from the QCoDeS community
- **Automatic fallback**: Import contrib drivers when available, gracefully handle absence
- **BlueFors monitoring**: Read fridge parameters from log files
- **Multiple temperature controllers**: Support for both Lakeshore 372 (custom) and 331 (contrib)

### 🛡️ Enhanced Safety
- Comprehensive parameter validation before measurements
- Software interlocks for magnetic field and temperature control
- Instrument-specific limit checking
- Emergency stop functionality

### 📊 Advanced Data Management
- QCoDeS dataset integration with SQLite backend
- Automatic metadata storage
- HDF5 export capability
- Structured data organization

### 🔬 Measurement Protocols
- **I-V Sweeps**: DC and AC measurements with various field/temperature conditions
- **Hall Measurements**: Transverse resistance with vector field control
- **Spectroscopy**: dI/dV measurements with harmonic analysis
- **Temperature Sweeps**: Automated resistance vs temperature measurements

### 📈 Analysis & Visualization
- Built-in data analysis tools
- Matplotlib/PyQtGraph plotting integration
- Statistical analysis and fitting utilities
- Real-time monitoring capabilities

## LabVIEW VI Equivalents

| LabVIEW VI | Python Class | Description |
|------------|---------------|-------------|
| `I(V)_K6221-K2182a_PK.vi` | `IVMeasurement` | Basic I-V measurements |
| `I(V) at various fields_*.vi` | `IVFieldSweep` | Field-dependent I-V measurements |
| `dI-dV(V)_MFLI_*.vi` | `DifferentialConductance` | Lock-in based dI/dV measurements |
| `STS at various H_*.vi` | `STSMeasurement` | Tunneling spectroscopy |
| `RH_BF_LD-400_MFLI_*.vi` | `HallMeasurement` | Hall resistance measurements |
| `RT_BF_LD-400_MFLI_*.vi` | `TemperatureResistanceSweep` | R vs T measurements |
| `AMI430_Magnet controller_*.vi` | `AMI430MagnetController` | Vector field control |

See [MIGRATION_GUIDE.py](MIGRATION_GUIDE.py) for detailed mapping information.

## QCoDeS Contrib Drivers Integration

This package integrates with the [QCoDeS Community Contributed Drivers](https://github.com/QCoDeS/Qcodes_contrib_drivers) repository to provide access to a broader range of instrument drivers developed by the QCoDeS community.

### Available Contrib Drivers

- **BlueFors**: Fridge monitoring via log file parsing - provides temperature and pressure monitoring
- **Lakeshore Model 331**: Basic temperature controller (2-channel) - complements the custom Lakeshore 372 driver
- **50+ additional drivers**: Available for various manufacturers (Keysight, Rohde & Schwarz, Oxford, etc.)

### Usage

Contrib drivers are automatically imported when available and can be used alongside custom drivers:

```python
from bluefors_dc.instruments import (
    # Custom drivers (always available)
    AMI430MagnetController, Keithley6221, Lakeshore372,
    # Contrib drivers (imported when available)  
    BlueFors, Lakeshore331
)
```

### Fallback Behavior

If `qcodes-contrib-drivers` is not installed, the package continues to work with only the custom drivers. The contrib drivers are optional dependencies that extend functionality when available.

## Official Zurich Instruments Integration

This package also integrates with the [official Zurich Instruments drivers for QCoDeS](https://github.com/zhinst/zhinst-qcodes) to provide access to professionally maintained drivers for Zurich Instruments devices.

### Available Official Drivers

- **MFLI**: Multi-frequency lock-in amplifier - provides comprehensive lock-in functionality with advanced features
- **Additional ZI devices**: MFIA, UHFLI, HDAWG, SHFQA, etc. (available through the ZhinstrumentsMFLI import pattern)

### Installation

```bash
# Install with official Zurich Instruments drivers
pip install -e .[zhinst]
```

### Usage

The official drivers are automatically imported when available and can be used alongside the custom drivers:

```python
from bluefors_dc.instruments import (
    # Custom Zurich driver (always available - basic functionality)
    ZurichMFLI,
    # Official Zurich driver (imported when zhinst-qcodes available - full functionality)
    ZhinstrumentsMFLI
)

# Use the official driver for advanced features
try:
    lock_in = ZhinstrumentsMFLI('lock_in', 'dev1234', 'localhost')
    # Full zhinst-toolkit functionality available
except NameError:
    # Fall back to custom driver if zhinst-qcodes not installed
    lock_in = ZurichMFLI('lock_in', 'dev1234')
    # Basic lock-in functionality available
```

### Benefits of Official Integration

- **Professional maintenance**: Drivers maintained by Zurich Instruments engineering team
- **Latest features**: Access to newest device capabilities and firmware features  
- **Comprehensive functionality**: Full device parameter access and advanced measurement modes
- **Zurich Toolkit integration**: Direct access to high-level measurement workflows
- **Automatic fallback**: Graceful degradation to custom driver when official drivers unavailable

## Project Structure

```
bluefors_dc/
├── instruments/          # QCoDeS instrument drivers
│   ├── ami430.py        # AMI430 magnet controller  
│   ├── keithley.py      # Keithley 6221/2182A/2636B
│   ├── zurich.py        # Zurich MFLI lock-in
│   └── lakeshore.py     # Lakeshore 372 temperature controller
├── measurements/         # Measurement protocols
│   ├── station_setup.py # Station configuration
│   ├── iv_measurements.py # I-V measurement classes
│   ├── differential_measurements.py # dI/dV measurements
│   └── transport_measurements.py # Hall, R-T measurements
├── utils/               # Utility functions
│   └── safety.py        # Safety checks and interlocks
├── config/              # Configuration files
├── analysis/            # Data analysis tools
└── examples/            # Usage examples
```

## Safety Features

⚠️ **IMPORTANT**: This system includes comprehensive safety interlocks that were not present in the original LabVIEW implementation:

- **Magnetic field limits**: Maximum field magnitude and ramp rate protection
- **Temperature limits**: Safe operating range enforcement  
- **Current/voltage limits**: Instrument compliance and safety limits
- **Parameter validation**: Automatic checking of measurement parameters
- **Emergency stop**: Immediate safe shutdown of all instruments

## Examples

The `examples/` directory contains complete measurement examples:

- `basic_iv_measurement.py`: Simple I-V measurement with plotting
- `differential_conductance_example.py`: dI/dV measurement with peak detection
- `contrib_drivers_example.py`: Using QCoDeS contrib drivers for extended functionality
- `field_sweep_example.py`: Magnetic field dependent measurements
- `temperature_sweep_example.py`: Temperature dependent transport

## Testing

Run the test suite:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## Migration from LabVIEW

For users migrating from the original LabVIEW implementation:

1. **Parameter mapping**: Most VI parameters have direct Python equivalents
2. **Data structures**: LabVIEW clusters → Python dictionaries, arrays → NumPy arrays
3. **File formats**: TDMS files → QCoDeS SQLite databases + HDF5 export
4. **Safety**: Enhanced protection compared to original LabVIEW VIs
5. **Performance**: Similar measurement speeds with improved analysis capabilities

## License

This project maintains the same open approach as the original LabVIEW implementation while adding modern software engineering practices and safety features.

## Acknowledgments

This implementation is based on the original LabVIEW measurement system developed for Ph.D. research on the Bluefors LD-400 system. The Python version maintains full functional equivalence while adding significant improvements in safety, data management, and analysis capabilities.
