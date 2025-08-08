#!/usr/bin/env python3
"""
Example demonstrating the use of QCoDeS contrib drivers in Bluefors DC measurements.

This example shows how to use contrib drivers alongside the official/custom drivers 
for enhanced functionality and broader instrument support.

MIGRATION NOTE: This example now uses official QCoDeS drivers where available,
with contrib and custom drivers for additional functionality.
"""

import time
from bluefors_dc.instruments import (
    # Official QCoDeS drivers (preferred)
    AMI430MagnetController,  # Now uses qcodes.instrument_drivers.american_magnetics.AMI430
    Keithley2636B,           # Now uses qcodes.instrument_drivers.Keithley.Keithley_2636B
    Lakeshore372,            # Now uses qcodes.instrument_drivers.Lakeshore.Model_372
    
    # Custom drivers (no official equivalent)
    Keithley6221,            # Custom - no official QCoDeS equivalent
    Keithley2182A,           # Custom - no official QCoDeS equivalent
    ZurichMFLI,              # Custom fallback - use zhinst-qcodes for official
    
    # Contrib drivers
    BlueFors,                # From qcodes_contrib_drivers
    Lakeshore331,            # From qcodes_contrib_drivers
    
    # Status function
    get_driver_status
)

def main():
    print("QCoDeS Official + Contrib Drivers Integration Example")
    print("=" * 60)
    
    # Show driver status
    print("\n0. Driver Migration Status")
    status = get_driver_status()
    print("\nOfficial QCoDeS drivers (preferred):")
    for driver, available in status['official_drivers_available'].items():
        symbol = "✓" if available else "✗"
        source = "official QCoDeS" if available else "custom fallback"
        print(f"  {symbol} {driver}: {source}")
    
    print("\nContrib drivers:")
    for driver, available in status['contrib_drivers_available'].items():
        symbol = "✓" if available else "✗"
        source = "qcodes_contrib_drivers" if available else "not available"
        print(f"  {symbol} {driver}: {source}")
    
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
        print("Available parameters:", list(fridge.parameters.keys())[:5], "...")
        
        # Example of how you would read temperatures (requires actual hardware)
        # temp_mc = fridge.temperature_mixing_chamber()
        # print(f"Mixing chamber temperature: {temp_mc} K")
        
    except Exception as e:
        print(f"BlueFors setup failed (expected without hardware): {e}")
    
    # Example 2: Using official QCoDeS drivers (now preferred)
    print("\n2. Official QCoDeS Drivers (Preferred)")
    print("   - AMI430: Official american_magnetics.AMI430")  
    print("   - Keithley2636B: Official Keithley.Keithley_2636B")
    print("   - Lakeshore372: Official Lakeshore.Model_372")
    
    try:
        # Official AMI430 driver
        magnet = AMI430MagnetController(
            name="ami430_magnet",
            address="TCPIP::192.168.1.100::7180::SOCKET",  # Example address
            has_current_rating=True  # Official driver parameter
        )
        print(f"AMI430 (official): {magnet.name}")
        print(f"  Module source: {magnet.__class__.__module__}")
        
    except Exception as e:
        print(f"AMI430 setup failed (expected without hardware): {e}")
    
    try:
        # Official Keithley2636B driver  
        smu = Keithley2636B(
            name="keithley_2636b",
            address="TCPIP::192.168.1.105::INSTR"  # Example address
        )
        print(f"Keithley2636B (official): {smu.name}")
        print(f"  Module source: {smu.__class__.__module__}")
        
    except Exception as e:
        print(f"Keithley2636B setup failed (expected without hardware): {e}")
    
    # Example 3: Custom drivers still used where no official equivalent exists
    print("\n3. Custom Drivers (Where No Official Equivalent)")
    print("   - Keithley6221: Custom current source driver")
    print("   - Keithley2182A: Custom nanovoltmeter driver")
    
    try:
        current_source = Keithley6221(
            name="keithley_6221",
            address="TCPIP::192.168.1.103::INSTR"
        )
        print(f"Keithley6221 (custom): {current_source.name}")
        
    except Exception as e:
        print(f"Keithley6221 setup failed (expected without hardware): {e}")
    
    # Example 4: Station setup combining official, contrib, and custom drivers  
    print("\n4. Combined Station Setup")
    from bluefors_dc.measurements import BlueforsStation
    
    station = BlueforsStation()
    
    print("Station can now combine:")
    print("  - Official QCoDeS drivers (AMI430, Keithley2636B, Lakeshore372)")  
    print("  - Contrib monitoring drivers (BlueFors fridge, Lakeshore331)")
    print("  - Custom drivers only where no official equivalent exists")
    print("  - All provide complementary functionality for complete system control")
    
    print("\n5. Migration Benefits")
    print("✓ Official maintenance and support")
    print("✓ Latest device features and bug fixes")  
    print("✓ Better integration with QCoDeS ecosystem")
    print("✓ Consistent parameter naming and validation")
    print("✓ Professional documentation and examples")

if __name__ == "__main__":
    main()