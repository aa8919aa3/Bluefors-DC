"""
Example showing how to use Zurich Instruments MFLI drivers.

This example demonstrates the driver priority system:
1. zhinst-qcodes (preferred - professional support)
2. Custom fallback driver (basic functionality)

MIGRATION NOTE: Custom Zurich driver is deprecated in favor of zhinst-qcodes.
"""

from bluefors_dc.measurements import BlueforsStation
from bluefors_dc.instruments import ZurichMFLI, get_driver_status

def main():
    """Main example function."""
    print("=== Bluefors DC - Zurich Instruments MFLI Example ===\n")
    
    # Check what Zurich drivers are available
    status = get_driver_status()
    zhinst_available = status['official_drivers_available']['ZhinstrumentsMFLI']
    
    if zhinst_available:
        print("✓ Official Zurich Instruments driver (zhinst-qcodes) is available")
        print("  Using professional zhinst-qcodes driver with full functionality")
        official_available = True
    else:
        print("✗ Official Zurich Instruments driver (zhinst-qcodes) is not available")
        print("  Using custom fallback driver with basic functionality")
        print("  Install with: pip install zhinst-qcodes")
        official_available = False
    print()
    
    # Show current driver source
    print("=== Current Driver Configuration ===")
    print(f"ZurichMFLI source: {ZurichMFLI.__module__}")
    if 'zhinst' in ZurichMFLI.__module__:
        print("✓ Using official zhinst-qcodes driver")
    else:
        print("⚠ Using custom fallback driver")
    print()
    
    # Demonstrate driver selection strategy
    print("=== Driver Selection Strategy ===")
    
    if official_available:
        print("✓ RECOMMENDED: Official zhinst-qcodes driver in use")
        print("  Benefits:")
        print("  - Professional maintenance by Zurich Instruments")
        print("  - Access to latest device features")
        print("  - Full Zurich Toolkit integration")
        print("  - Comprehensive parameter access")
        print("  - Advanced measurement modes")
        print()
        
        # Example with official driver
        print("Example using official zhinst-qcodes driver:")
        print("```python")
        print("from bluefors_dc.instruments import ZurichMFLI")
        print()
        print("# Connect to MFLI lock-in amplifier")
        print("lock_in = ZurichMFLI(")
        print("    'mfli_lockin',")
        print("    'dev1234',     # Your device serial")
        print("    host='localhost',  # Data server host")
        print("    port=8004         # Data server port") 
        print(")")
        print()
        print("# Full zhinst-toolkit functionality available")
        print("lock_in.demods[0].freq(1000)      # Set demodulator frequency")
        print("lock_in.demods[0].phase(0)        # Set phase")
        print("lock_in.sigins[0].range(1.0)      # Set input range")
        print("lock_in.demods[0].sample()        # Get measurement sample")
        print("```")
        print()
    else:
        print("⚠ FALLBACK: Custom driver in use")
        print("  Limitations:")
        print("  - Basic functionality only")
        print("  - No access to advanced features")
        print("  - Limited parameter support")
        print("  - No professional maintenance")
        print()
    
        # Example with custom driver
        print("Example using custom fallback driver:")
        print("```python")
        print("from bluefors_dc.instruments import ZurichMFLI")
        print()
        print("# Connect to MFLI lock-in amplifier")
        print("lock_in = ZurichMFLI(")
        print("    'mfli_lockin',")
        print("    device_id='dev1234'  # Your device ID")
        print(")")
        print()
        print("# Basic functionality only")
        print("lock_in.frequency(1000)           # Set frequency")
        print("lock_in.phase(0)                  # Set phase")
        print("lock_in.amplitude(0.1)            # Set output amplitude")
        print("voltage = lock_in.amplitude_x()   # Read X voltage")
        print("```")
        print()
    
    # Station integration example
    print("=== Integration with BlueforsStation ===")
    print("```python")
    print("from bluefors_dc.measurements import BlueforsStation")
    print("from bluefors_dc.instruments import ZurichMFLI")
    print()
    print("# Set up measurement station")
    print("station = BlueforsStation()")
    print()
    print("# Add other instruments (now using official drivers where available)")
    print("station.add_current_source('TCPIP::192.168.1.101::INSTR')  # Keithley6221")
    print("station.add_nanovoltmeter('TCPIP::192.168.1.102::INSTR')   # Keithley2182A")
    print("station.add_magnet_controller('TCPIP::192.168.1.100::7180::SOCKET')  # Official AMI430")
    print()
    print("# Add lock-in amplifier")
    if official_available:
        print("# Using official zhinst-qcodes driver (preferred)")
    else:
        print("# Using custom fallback driver")
    print("lock_in = ZurichMFLI('mfli', 'dev1234')")
    print("station.add_component('lock_in', lock_in)")
    print()
    print("# Use in differential conductance measurements")
    print("from bluefors_dc.measurements import DifferentialConductance")
    print("diff_measurement = DifferentialConductance(station)")
    print("# ... configure and run measurement")
    print("```")
    print()
    
    print("=== Migration Instructions ===")
    print("To migrate from custom to official drivers:")
    print()
    print("1. Install official Zurich Instruments support:")
    print("   pip install bluefors-dc[zhinst]")
    print("   # or")
    print("   pip install zhinst-qcodes")
    print()
    print("2. Update your measurement scripts:")
    print("   # Your import statements stay the same!")
    print("   from bluefors_dc.instruments import ZurichMFLI")
    print("   ")
    print("   # Driver selection happens automatically")
    print("   # Official driver will be used if available")
    print()
    print("3. Review measurement parameters:")
    print("   # Official driver may have different parameter names")
    print("   # Check the zhinst-qcodes documentation for details")
    print()
    print("For development:")
    print("  pip install bluefors-dc[dev,zhinst]")


if __name__ == "__main__":
    main()