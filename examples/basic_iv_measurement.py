"""
Example: Basic I-V measurement

This example demonstrates how to set up the station and run a basic
current-voltage measurement equivalent to I(V)_K6221-K2182a_PK.vi
"""

import numpy as np
import matplotlib.pyplot as plt

from bluefors_dc.measurements import BlueforsStation, IVMeasurement, IVSweepParameters
from bluefors_dc.config import INSTRUMENTS, DEFAULT_MEASUREMENT_PARAMS
from bluefors_dc.utils import SafetyChecks


def main():
    """Run basic I-V measurement example."""
    
    # Initialize safety checker
    safety = SafetyChecks()
    
    # Create station
    station = BlueforsStation()
    
    # Add instruments (update addresses for your system)
    try:
        current_source = station.add_current_source(
            address=INSTRUMENTS['current_source']['address']
        )
        nanovoltmeter = station.add_nanovoltmeter(
            address=INSTRUMENTS['nanovoltmeter']['address']
        )
        
        print("Instruments connected successfully")
        
    except Exception as e:
        print(f"Error connecting instruments: {e}")
        print("Running in simulation mode for demonstration")
        return
        
    # Set up I-V measurement
    iv_measurement = IVMeasurement(station)
    
    # Define measurement parameters
    iv_params = IVSweepParameters(
        start_current=-1e-6,        # -1 µA
        stop_current=1e-6,          # +1 µA  
        num_points=101,
        delay_between_points=0.1,   # 100 ms
        bidirectional=True,
        compliance_voltage=10.0     # 10 V compliance
    )
    
    # Check safety
    sweep_params = {
        'current_range': (iv_params.start_current, iv_params.stop_current),
        'num_points': iv_params.num_points,
        'delay_between_points': iv_params.delay_between_points
    }
    
    if not safety.check_sweep_parameters(sweep_params):
        print("Safety check failed!")
        return
        
    # Estimate measurement time
    estimated_time = safety.estimate_sweep_time(sweep_params)
    print(f"Estimated measurement time: {estimated_time:.1f} seconds")
    
    # Run measurement
    print("Starting I-V measurement...")
    
    try:
        data = iv_measurement.run_sweep(iv_params, "example_iv_measurement")
        
        print(f"Measurement completed. Collected {len(data['current'])} points")
        
        # Basic analysis
        current = data['current'] * 1e6  # Convert to µA
        voltage = data['voltage'] * 1e3  # Convert to mV  
        resistance = data['resistance']
        
        # Calculate average resistance (excluding near-zero current points)
        mask = np.abs(data['current']) > 1e-8
        avg_resistance = np.mean(resistance[mask])
        
        print(f"Average resistance: {avg_resistance:.3e} Ω")
        
        # Plot results
        plt.figure(figsize=(12, 4))
        
        # I-V curve
        plt.subplot(1, 2, 1)
        plt.plot(current, voltage, 'b.-', linewidth=2, markersize=4)
        plt.xlabel('Current (µA)')
        plt.ylabel('Voltage (mV)')
        plt.title('I-V Characteristic')
        plt.grid(True, alpha=0.3)
        
        # Resistance vs current
        plt.subplot(1, 2, 2)
        plt.plot(current, resistance, 'r.-', linewidth=2, markersize=4)
        plt.xlabel('Current (µA)')
        plt.ylabel('Resistance (Ω)')
        plt.title('Resistance vs Current')
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        
        plt.tight_layout()
        plt.savefig('iv_measurement_example.png', dpi=300)
        plt.show()
        
    except Exception as e:
        print(f"Measurement error: {e}")
        
    finally:
        # Safe shutdown
        try:
            station.emergency_stop()
            station.close_all_instruments()
            print("Instruments safely shut down")
        except Exception as e:
            print(f"Error during shutdown: {e}")


if __name__ == "__main__":
    main()