"""
Example: Differential Conductance Measurement

This example demonstrates dI-dV measurements equivalent to the LabVIEW VI:
dI-dV(V)_MFLI_MF-MD_K3636B_measureX_PK_V4.0_withaveraging.vi
"""

import numpy as np
import matplotlib.pyplot as plt

from bluefors_dc.measurements import BlueforsStation, DifferentialConductance, DifferentialParameters
from bluefors_dc.config import INSTRUMENTS


def main():
    """Run differential conductance measurement example."""
    
    # Create station
    station = BlueforsStation()
    
    # Add instruments
    try:
        smu = station.add_dual_smu(
            address=INSTRUMENTS['dual_smu']['address']
        )
        lockin = station.add_lock_in(
            device_id=INSTRUMENTS['lock_in']['device_id']
        )
        
        print("Instruments connected for differential measurement")
        
    except Exception as e:
        print(f"Error connecting instruments: {e}")
        print("Running in simulation mode")
        return
        
    # Set up differential measurement
    diff_measurement = DifferentialConductance(station, smu_channel='a')
    
    # Define measurement parameters
    diff_params = DifferentialParameters(
        start_voltage=-0.01,        # -10 mV
        stop_voltage=0.01,          # +10 mV
        num_points=201,
        ac_amplitude=0.001,         # 1 mV AC amplitude
        frequency=1000.0,           # 1 kHz
        time_constant=0.03,         # 30 ms time constant
        averages=5,                 # 5-point averaging
        delay_between_points=0.1,
        bidirectional=True
    )
    
    print("Starting differential conductance measurement...")
    
    try:
        data = diff_measurement.run_sweep(diff_params, "example_didv_measurement")
        
        print(f"Measurement completed. Collected {len(data['voltage'])} points")
        
        # Extract data
        voltage = data['voltage'] * 1000  # Convert to mV
        diff_conductance = data['diff_conductance'] * 1e6  # Convert to µS (microsiemens)
        dc_current = data['current'] * 1e9  # Convert to nA
        dc_resistance = data['resistance']
        
        # Calculate statistics
        print(f"Voltage range: {np.min(voltage):.1f} to {np.max(voltage):.1f} mV")
        print(f"Conductance range: {np.min(diff_conductance):.3f} to {np.max(diff_conductance):.3f} µS")
        print(f"Average DC resistance: {np.mean(dc_resistance):.3e} Ω")
        
        # Plot results
        plt.figure(figsize=(15, 5))
        
        # DC I-V curve
        plt.subplot(1, 3, 1)
        plt.plot(voltage, dc_current, 'b.-', linewidth=2, markersize=3)
        plt.xlabel('Voltage (mV)')
        plt.ylabel('Current (nA)')
        plt.title('DC I-V Characteristic')
        plt.grid(True, alpha=0.3)
        
        # Differential conductance
        plt.subplot(1, 3, 2)
        plt.plot(voltage, diff_conductance, 'r.-', linewidth=2, markersize=3)
        plt.xlabel('Voltage (mV)')
        plt.ylabel('dI/dV (µS)')
        plt.title('Differential Conductance')
        plt.grid(True, alpha=0.3)
        
        # DC resistance
        plt.subplot(1, 3, 3)
        plt.plot(voltage, dc_resistance, 'g.-', linewidth=2, markersize=3)
        plt.xlabel('Voltage (mV)')
        plt.ylabel('DC Resistance (Ω)')
        plt.title('DC Resistance')
        plt.grid(True, alpha=0.3)
        plt.yscale('log')
        
        plt.tight_layout()
        plt.savefig('differential_measurement_example.png', dpi=300)
        plt.show()
        
        # Look for interesting features
        # Find peaks in differential conductance
        diff_cond_smooth = np.convolve(diff_conductance, np.ones(5)/5, mode='same')
        peaks = []
        for i in range(1, len(diff_cond_smooth)-1):
            if (diff_cond_smooth[i] > diff_cond_smooth[i-1] and 
                diff_cond_smooth[i] > diff_cond_smooth[i+1] and
                diff_cond_smooth[i] > np.mean(diff_cond_smooth) + np.std(diff_cond_smooth)):
                peaks.append(i)
                
        if peaks:
            print(f"\nFound {len(peaks)} conductance peaks:")
            for i, peak_idx in enumerate(peaks):
                peak_voltage = voltage[peak_idx]
                peak_conductance = diff_conductance[peak_idx]
                print(f"Peak {i+1}: V = {peak_voltage:.2f} mV, dI/dV = {peak_conductance:.3f} µS")
        else:
            print("No significant conductance peaks detected")
            
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