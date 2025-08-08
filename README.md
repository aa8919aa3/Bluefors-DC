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
- **AMI 430**: 2-axis vector magnet controller (up to 9T)
- **Lakeshore 372**: AC resistance bridge temperature controller (16 channels)

### Measurement Electronics  
- **Keithley 6221**: Current source with delta mode capability
- **Keithley 2182A**: Nanovoltmeter for high-precision voltage measurement
- **Keithley 2636B**: Dual channel source-measure unit
- **Zurich Instruments MFLI**: Lock-in amplifier with harmonic analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/aa8919aa3/Bluefors-DC.git
cd Bluefors-DC

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

## Quick Start

### Basic I-V Measurement

```python
from bluefors_dc.measurements import BlueforsStation, IVMeasurement, IVSweepParameters

# Set up station with instruments
station = BlueforsStation()
station.add_current_source('TCPIP::192.168.1.101::INSTR')
station.add_nanovoltmeter('TCPIP::192.168.1.102::INSTR')

# Configure and run measurement
iv_measurement = IVMeasurement(station)
params = IVSweepParameters(
    start_current=-1e-6,  # -1 μA
    stop_current=1e-6,    # +1 μA  
    num_points=101,
    compliance_voltage=10.0
)

data = iv_measurement.run_sweep(params)
print(f"Average resistance: {np.mean(data['resistance']):.3e} Ω")
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
