#!/usr/bin/env python3
"""
Example demonstrating the use of QCoDeS contrib drivers in Bluefors DC measurements.

This example shows how to use contrib drivers alongside the custom drivers 
for enhanced functionality and broader instrument support.
"""

import time
from bluefors_dc.instruments import (
    # Custom drivers
    AMI430MagnetController, 
    Keithley6221, 
    Lakeshore372,
    # Contrib drivers
    BlueFors,
    Lakeshore331
)

def main():
    print("QCoDeS Contrib Drivers Integration Example")
    print("=" * 50)
    
    # Example 1: Using BlueFors contrib driver for fridge monitoring
    print("\n1. BlueFors Fridge Monitoring (contrib driver)")
    try:
        # Note: This is a mock example - actual usage requires valid log folder path
        # and proper channel configuration based on your specific setup
        fridge = BlueFors(
            name="bluefors_fridge",
            folder_path="/path/to/bluefors/logs",  # Update with actual path
            channel_vacuum_can=1,
            channel_pumping_line=2, 
            channel_compressor_outlet=3,
            channel_compressor_inlet=4,
            channel_mixture_tank=5,
            channel_venting_line=6,
            channel_50k_plate=1,
            channel_4k_plate=2,
            channel_still=3,
            channel_mixing_chamber=4,
            channel_magnet=5
        )
        print(f"BlueFors fridge driver initialized: {fridge.name}")
        print("Available parameters:", list(fridge.parameters.keys()))
        
        # Example of how you would read temperatures (requires actual hardware)
        # temp_mc = fridge.temperature_mixing_chamber()
        # print(f"Mixing chamber temperature: {temp_mc} K")
        
    except Exception as e:
        print(f"BlueFors setup failed (expected without hardware): {e}")
    
    # Example 2: Using Lakeshore 331 contrib driver alongside Lakeshore 372 custom driver
    print("\n2. Lakeshore Temperature Controllers")
    print("   - Custom Lakeshore 372 driver for AC resistance bridge")  
    print("   - Contrib Lakeshore 331 driver for basic temperature control")
    
    try:
        # Custom driver for Lakeshore 372 (16-channel AC resistance bridge)
        lakeshore_372 = Lakeshore372(
            name="lakeshore_372",
            address="TCPIP::192.168.1.110::INSTR"  # Example address
        )
        print(f"Lakeshore 372 (custom): {lakeshore_372.name}")
        
    except Exception as e:
        print(f"Lakeshore 372 setup failed (expected without hardware): {e}")
    
    try:
        # Contrib driver for Lakeshore 331 (basic temperature controller)
        lakeshore_331 = Lakeshore331(
            name="lakeshore_331", 
            address="GPIB0::12::INSTR"  # Example address
        )
        print(f"Lakeshore 331 (contrib): {lakeshore_331.name}")
        print("Available channels:", [ch.name for ch in lakeshore_331.channels])
        
    except Exception as e:
        print(f"Lakeshore 331 setup failed (expected without hardware): {e}")
    
    # Example 3: Station setup combining custom and contrib drivers  
    print("\n3. Combined Station Setup")
    from bluefors_dc.measurements import BlueforsStation
    
    station = BlueforsStation()
    
    print("Station can combine:")
    print("  - Custom measurement drivers (Keithley 6221/2182A, AMI430, Zurich MFLI)")  
    print("  - Contrib monitoring drivers (BlueFors fridge, Lakeshore 331)")
    print("  - Both provide complementary functionality for complete system control")
    
    # Show available driver classes
    print("\n4. Available Driver Classes:")
    print("Custom drivers:")
    custom_drivers = [
        'AMI430MagnetController', 'Keithley6221', 'Keithley2182A', 
        'Keithley2636B', 'ZurichMFLI', 'Lakeshore372'
    ]
    for driver in custom_drivers:
        print(f"  - {driver}")
    
    print("\nContrib drivers:")
    contrib_drivers = ['BlueFors', 'Lakeshore331']
    for driver in contrib_drivers:
        print(f"  - {driver}")

if __name__ == "__main__":
    main()