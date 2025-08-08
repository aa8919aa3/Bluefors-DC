"""
Tests for QCoDeS contrib drivers integration.
"""

import pytest
import importlib

def test_contrib_drivers_import():
    """Test that contrib drivers can be imported when available."""
    try:
        # Test importing the contrib drivers integration
        from bluefors_dc.instruments import BlueFors, Lakeshore331
        assert BlueFors is not None
        assert Lakeshore331 is not None
        
        # Test that they are the expected classes
        assert BlueFors.__name__ == 'BlueFors'
        assert Lakeshore331.__name__ == 'Model_331'
        
        print("Contrib drivers successfully imported")
    
    except ImportError:
        # This is expected if qcodes-contrib-drivers is not installed
        pytest.skip("qcodes-contrib-drivers not available")

def test_custom_drivers_always_available():
    """Test that custom drivers are always available as fallback.""" 
    from bluefors_dc.instruments import (
        AMI430MagnetController,
        Keithley6221,
        Keithley2182A, 
        Keithley2636B,
        ZurichMFLI,
        Lakeshore372
    )
    
    # All drivers should be available (either official or custom fallback)
    assert AMI430MagnetController is not None
    assert Keithley6221 is not None
    assert Keithley2182A is not None
    assert Keithley2636B is not None
    assert ZurichMFLI is not None
    assert Lakeshore372 is not None

def test_official_drivers_preferred():
    """Test that official drivers are used when available."""
    from bluefors_dc.instruments import (
        AMI430MagnetController,
        Keithley2636B,
        Lakeshore372,
        get_driver_status
    )
    
    # Check driver status
    status = get_driver_status()
    official_available = status['official_drivers_available']
    
    # Verify official drivers are being used when available
    if official_available['AMI430']:
        assert 'qcodes.instrument_drivers.american_magnetics.AMI430' in AMI430MagnetController.__module__
    else:
        assert 'bluefors_dc.instruments.ami430' in AMI430MagnetController.__module__
        
    if official_available['Keithley2636B']:
        assert 'qcodes.instrument_drivers.Keithley.Keithley_2636B' in Keithley2636B.__module__
    else:
        assert 'bluefors_dc.instruments.keithley' in Keithley2636B.__module__
        
    if official_available['Lakeshore372']:
        assert 'qcodes.instrument_drivers.Lakeshore.Model_372' in Lakeshore372.__module__
    else:
        assert 'bluefors_dc.instruments.lakeshore' in Lakeshore372.__module__

def test_custom_drivers_for_instruments_without_official():
    """Test that instruments without official drivers still use custom ones."""
    from bluefors_dc.instruments import Keithley6221, Keithley2182A
    
    # These should always use custom drivers (no official equivalents)
    assert 'bluefors_dc.instruments.keithley' in Keithley6221.__module__
    assert 'bluefors_dc.instruments.keithley' in Keithley2182A.__module__

def test_instruments_module_exports():
    """Test that the instruments module exports include both official/custom and contrib drivers when available."""
    import bluefors_dc.instruments as instruments
    
    # All primary drivers should always be in __all__ (official or custom fallback)
    primary_drivers = [
        'AMI430MagnetController',
        'Keithley6221',
        'Keithley2182A',
        'Keithley2636B', 
        'ZurichMFLI',
        'Lakeshore372'
    ]
    
    for driver in primary_drivers:
        assert driver in instruments.__all__, f"Driver {driver} not in __all__"
    
    # Check if contrib drivers are available and in __all__ 
    try:
        import qcodes_contrib_drivers
        # If contrib drivers are installed, they should be in __all__
        contrib_drivers = ['BlueFors', 'Lakeshore331'] 
        for driver in contrib_drivers:
            assert driver in instruments.__all__, f"Contrib driver {driver} not in __all__ when contrib package is available"
    except ImportError:
        # If contrib drivers not installed, that's fine - they shouldn't be in __all__
        pass

def test_driver_status_function():
    """Test that the driver status function works correctly."""
    from bluefors_dc.instruments import get_driver_status
    
    status = get_driver_status()
    
    # Check structure
    assert 'official_drivers_available' in status
    assert 'contrib_drivers_available' in status
    
    # Check that expected drivers are tracked
    official_drivers = status['official_drivers_available']
    assert 'AMI430' in official_drivers
    assert 'Keithley2636B' in official_drivers
    assert 'Lakeshore372' in official_drivers
    assert 'ZurichMFLI' in official_drivers
    
    contrib_drivers = status['contrib_drivers_available']
    assert 'BlueFors' in contrib_drivers
    assert 'Lakeshore331' in contrib_drivers

def test_package_dependency():
    """Test that the package dependency is correctly configured."""
    try:
        import bluefors_dc
        # If we can import bluefors_dc, it should work with or without contrib drivers
        assert bluefors_dc.__version__ == "1.0.0"
    except ImportError as e:
        pytest.fail(f"Main package import failed: {e}")