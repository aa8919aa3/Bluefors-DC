"""
Tests for Zurich Instruments zhinst-qcodes integration.

This module tests the integration with the official Zurich Instruments
drivers for QCoDeS (zhinst-qcodes).
"""

import pytest


class TestZhinstrumentsIntegration:
    """Test integration with zhinst-qcodes drivers."""

    def test_zhinst_mfli_import_availability(self):
        """Test that ZhinstrumentsMFLI is available when zhinst-qcodes is installed."""
        try:
            # Check if zhinst-qcodes is available
            import zhinst.qcodes
            zhinst_available = True
        except ImportError:
            zhinst_available = False
            
        # Import our instruments module
        from bluefors_dc import instruments
        
        if zhinst_available:
            # If zhinst-qcodes is available, ZhinstrumentsMFLI should be importable
            assert hasattr(instruments, 'ZhinstrumentsMFLI'), \
                "ZhinstrumentsMFLI should be available when zhinst-qcodes is installed"
            assert 'ZhinstrumentsMFLI' in instruments.__all__, \
                "ZhinstrumentsMFLI should be in __all__ when zhinst-qcodes is available"
            
            # The driver should be the official one
            assert instruments.ZhinstrumentsMFLI is not None
            assert instruments._ZHINST_QCODES_AVAILABLE is True
        else:
            # If zhinst-qcodes is not available, ZhinstrumentsMFLI should not be importable
            assert not hasattr(instruments, 'ZhinstrumentsMFLI') or \
                   instruments.ZhinstrumentsMFLI is None, \
                "ZhinstrumentsMFLI should not be available when zhinst-qcodes is not installed"
            assert 'ZhinstrumentsMFLI' not in instruments.__all__, \
                "ZhinstrumentsMFLI should not be in __all__ when zhinst-qcodes is not available"
            assert instruments._ZHINST_QCODES_AVAILABLE is False

    def test_custom_zurich_mfli_always_available(self):
        """Test that the custom ZurichMFLI driver is always available."""
        from bluefors_dc import instruments
        
        # Custom ZurichMFLI should always be available
        assert hasattr(instruments, 'ZurichMFLI'), \
            "Custom ZurichMFLI driver should always be available"
        assert 'ZurichMFLI' in instruments.__all__, \
            "ZurichMFLI should always be in __all__"
        assert instruments.ZurichMFLI is not None

    def test_driver_class_verification(self):
        """Test that imported drivers have expected class properties."""
        from bluefors_dc import instruments
        
        # Test custom driver
        assert hasattr(instruments.ZurichMFLI, '__init__'), \
            "ZurichMFLI should be a proper class with __init__"
        
        # Test official driver if available
        if hasattr(instruments, 'ZhinstrumentsMFLI') and \
           instruments.ZhinstrumentsMFLI is not None:
            assert hasattr(instruments.ZhinstrumentsMFLI, '__init__'), \
                "ZhinstrumentsMFLI should be a proper class with __init__"

    def test_fallback_behavior(self):
        """Test that the module gracefully handles absence of zhinst-qcodes."""
        # This test verifies that the import structure doesn't break
        # when zhinst-qcodes is not available
        
        from bluefors_dc import instruments
        
        # Basic functionality should always work
        assert len(instruments.__all__) >= 6, \
            "At least 6 base drivers should always be available"
        
        # Custom drivers should always be present
        required_drivers = [
            'AMI430MagnetController',
            'Keithley6221', 
            'Keithley2182A',
            'Keithley2636B',
            'ZurichMFLI',
            'Lakeshore372'
        ]
        
        for driver in required_drivers:
            assert driver in instruments.__all__, \
                f"{driver} should always be in __all__"
            assert hasattr(instruments, driver), \
                f"{driver} should always be importable"

    def test_both_drivers_coexist(self):
        """Test that both custom and official drivers can coexist."""
        from bluefors_dc import instruments
        
        # Custom driver should always be available
        assert hasattr(instruments, 'ZurichMFLI')
        
        # If official driver is available, both should coexist
        if hasattr(instruments, 'ZhinstrumentsMFLI') and \
           instruments.ZhinstrumentsMFLI is not None:
            # Both should be different classes
            assert instruments.ZurichMFLI != instruments.ZhinstrumentsMFLI, \
                "Custom and official drivers should be different classes"
            
            # Both should be in __all__
            assert 'ZurichMFLI' in instruments.__all__
            assert 'ZhinstrumentsMFLI' in instruments.__all__