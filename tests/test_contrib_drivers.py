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
    """Test that custom drivers are always available.""" 
    from bluefors_dc.instruments import (
        AMI430MagnetController,
        Keithley6221,
        Keithley2182A, 
        Keithley2636B,
        ZurichMFLI,
        Lakeshore372
    )
    
    # All custom drivers should be available
    assert AMI430MagnetController is not None
    assert Keithley6221 is not None
    assert Keithley2182A is not None
    assert Keithley2636B is not None
    assert ZurichMFLI is not None
    assert Lakeshore372 is not None

def test_instruments_module_exports():
    """Test that the instruments module exports include both custom and contrib drivers when available."""
    import bluefors_dc.instruments as instruments
    
    # Custom drivers should always be in __all__
    custom_drivers = [
        'AMI430MagnetController',
        'Keithley6221',
        'Keithley2182A',
        'Keithley2636B', 
        'ZurichMFLI',
        'Lakeshore372'
    ]
    
    for driver in custom_drivers:
        assert driver in instruments.__all__, f"Custom driver {driver} not in __all__"
    
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

def test_package_dependency():
    """Test that the package dependency is correctly configured."""
    try:
        import bluefors_dc
        # If we can import bluefors_dc, it should work with or without contrib drivers
        assert bluefors_dc.__version__ == "1.0.0"
    except ImportError as e:
        pytest.fail(f"Main package import failed: {e}")