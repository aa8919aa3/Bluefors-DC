"""
Example showing how to use Zurich Instruments MFLI drivers.

This example demonstrates how to use both the custom ZurichMFLI driver
and the official ZhinstrumentsMFLI driver from zhinst-qcodes.
"""

from bluefors_dc.measurements import BlueforsStation
from bluefors_dc.instruments import ZurichMFLI

def main():
    """Main example function."""
    print("=== Bluefors DC - Zurich Instruments MFLI Example ===\n")
    
    # Check what Zurich drivers are available
    from bluefors_dc import instruments
    
    if instruments._ZHINST_QCODES_AVAILABLE:
        print("✓ Official Zurich Instruments driver (zhinst-qcodes) is available")
        official_available = True
    else:
        print("✗ Official Zurich Instruments driver (zhinst-qcodes) is not available")
        print("  Install with: pip install zhinst-qcodes")
        official_available = False
    
    print("✓ Custom Zurich MFLI driver is available")
    print()
    
    # Demonstrate driver selection
    print("=== Driver Selection Strategy ===")
    
    if official_available:
        print("Recommendation: Use official ZhinstrumentsMFLI for full functionality")
        print("  - Professional maintenance by Zurich Instruments")
        print("  - Access to latest device features")
        print("  - Full Zurich Toolkit integration")
        print("  - Comprehensive parameter access")
        print()
        
        # Example with official driver
        print("Example using official driver:")
        print("```python")
        print("from bluefors_dc.instruments import ZhinstrumentsMFLI")
        print()
        print("# Connect to MFLI lock-in amplifier")
        print("lock_in = ZhinstrumentsMFLI(")
        print("    name='mfli_lockin',")
        print("    serial='dev1234',  # Your device serial")
        print("    host='localhost',  # Data server host")
        print("    port=8004         # Data server port")
        print(")")
        print()
        print("# Full functionality available through zhinst-toolkit")
        print("# lock_in.demods[0].freq(1000)  # Set demodulator frequency to 1 kHz")
        print("# lock_in.demods[0].phase(0)    # Set phase to 0 degrees")
        print("# lock_in.sigins[0].range(1.0)  # Set input range to 1V")
        print("```")
        print()
    
    print("Fallback: Use custom ZurichMFLI for basic functionality")
    print("  - Basic lock-in parameters")
    print("  - Simple measurement functions")
    print("  - Always available (no external dependencies)")
    print()
    
    # Example with custom driver
    print("Example using custom driver:")
    print("```python")
    print("from bluefors_dc.instruments import ZurichMFLI")
    print()
    print("# Connect to MFLI lock-in amplifier")
    print("lock_in = ZurichMFLI(")
    print("    name='mfli_lockin',")
    print("    device_id='dev1234'  # Your device ID")
    print(")")
    print()
    print("# Basic functionality")
    print("# lock_in.frequency(1000)      # Set frequency to 1 kHz")
    print("# lock_in.phase(0)             # Set phase to 0 degrees")
    print("# lock_in.amplitude(0.1)       # Set output amplitude to 100 mV")
    print("# voltage = lock_in.amplitude_x()  # Read X voltage")
    print("```")
    print()
    
    # Station integration example
    print("=== Integration with BlueforsStation ===")
    print("```python")
    print("from bluefors_dc.measurements import BlueforsStation")
    print("from bluefors_dc.instruments import ZurichMFLI")
    if official_available:
        print("from bluefors_dc.instruments import ZhinstrumentsMFLI")
    print()
    print("# Set up measurement station")
    print("station = BlueforsStation()")
    print()
    print("# Add other instruments")
    print("station.add_current_source('TCPIP::192.168.1.101::INSTR')")
    print("station.add_nanovoltmeter('TCPIP::192.168.1.102::INSTR')")
    print()
    print("# Add lock-in amplifier")
    if official_available:
        print("# Option 1: Official driver (recommended)")
        print("lock_in = ZhinstrumentsMFLI('mfli', 'dev1234', 'localhost')")
    print("# Option 2: Custom driver (fallback)")
    print("# lock_in = ZurichMFLI('mfli', 'dev1234')")
    print()
    print("# Use in differential conductance measurements")
    print("from bluefors_dc.measurements import DifferentialConductance")
    print("diff_measurement = DifferentialConductance(station)")
    print("# ... configure and run measurement")
    print("```")
    print()
    
    print("=== Installation Instructions ===")
    print("For basic functionality (custom drivers only):")
    print("  pip install bluefors-dc")
    print()
    print("For enhanced Zurich Instruments functionality:")
    print("  pip install bluefors-dc[zhinst]")
    print()
    print("For development:")
    print("  pip install bluefors-dc[dev,zhinst]")


if __name__ == "__main__":
    main()