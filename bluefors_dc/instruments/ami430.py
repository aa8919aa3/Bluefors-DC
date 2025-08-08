"""
AMI430 2-Axis Magnet Controller Driver

Provides QCoDeS interface for the AMI430 magnet power supply used 
for vector magnetic field control in the Bluefors LD-400 system.
"""

import time
import numpy as np
from typing import Union, Tuple
from qcodes import VisaInstrument, validators as vals
from qcodes.parameters import Parameter


class AMI430MagnetController(VisaInstrument):
    """
    QCoDeS driver for AMI430 2-axis magnet controller.
    
    Supports vector field control with X and Y axis coils for
    generating arbitrary in-plane magnetic field directions.
    """
    
    def __init__(self, name: str, address: str, **kwargs):
        """
        Initialize AMI430 magnet controller.
        
        Args:
            name: Name of the instrument
            address: VISA resource address
            **kwargs: Additional arguments passed to VisaInstrument
        """
        super().__init__(name, address, terminator='\r\n', **kwargs)
        
        # Field limits in Tesla (typical for AMI430 2-axis)
        self.field_limit = 9.0  # Maximum field magnitude
        
        # X-axis magnetic field
        self.add_parameter(
            'field_x',
            get_cmd='FIELD:MAG:X?',
            set_cmd='CONF:FIELD:MAG:X {:.6f}',
            unit='T',
            vals=vals.Numbers(-self.field_limit, self.field_limit),
            docstring='X-axis magnetic field component'
        )
        
        # Y-axis magnetic field  
        self.add_parameter(
            'field_y',
            get_cmd='FIELD:MAG:Y?',
            set_cmd='CONF:FIELD:MAG:Y {:.6f}',
            unit='T',
            vals=vals.Numbers(-self.field_limit, self.field_limit),
            docstring='Y-axis magnetic field component'
        )
        
        # Field magnitude (calculated)
        self.add_parameter(
            'field_magnitude',
            get_cmd=self._get_field_magnitude,
            set_cmd=False,
            unit='T',
            docstring='Total magnetic field magnitude'
        )
        
        # Field angle (calculated)
        self.add_parameter(
            'field_angle',
            get_cmd=self._get_field_angle,
            set_cmd=False,
            unit='deg',
            docstring='Magnetic field angle in degrees'
        )
        
        # Ramp rate parameters
        self.add_parameter(
            'ramp_rate_x',
            get_cmd='RAMP:RATE:FIELD:X?',
            set_cmd='CONF:RAMP:RATE:FIELD:X {:.4f}',
            unit='T/min',
            vals=vals.Numbers(0, 1.0),  # Safe ramp rate limit
            docstring='X-axis field ramp rate'
        )
        
        self.add_parameter(
            'ramp_rate_y', 
            get_cmd='RAMP:RATE:FIELD:Y?',
            set_cmd='CONF:RAMP:RATE:FIELD:Y {:.4f}',
            unit='T/min',
            vals=vals.Numbers(0, 1.0),  # Safe ramp rate limit
            docstring='Y-axis field ramp rate'
        )
        
        # Status parameters
        self.add_parameter(
            'magnet_status',
            get_cmd='STATE?',
            set_cmd=False,
            docstring='Magnet system status'
        )
        
        # Set safe default ramp rates
        self.connect_message()
        
    def _get_field_magnitude(self) -> float:
        """Calculate total field magnitude from X and Y components."""
        fx = self.field_x()
        fy = self.field_y()
        return np.sqrt(fx**2 + fy**2)
        
    def _get_field_angle(self) -> float:
        """Calculate field angle in degrees from X and Y components."""
        fx = self.field_x()
        fy = self.field_y()
        return np.degrees(np.arctan2(fy, fx))
        
    def set_field_vector(self, field_x: float, field_y: float, 
                        wait_for_completion: bool = True) -> None:
        """
        Set magnetic field vector components.
        
        Args:
            field_x: X-axis field in Tesla
            field_y: Y-axis field in Tesla  
            wait_for_completion: Whether to wait for ramp completion
        """
        magnitude = np.sqrt(field_x**2 + field_y**2)
        if magnitude > self.field_limit:
            raise ValueError(f"Field magnitude {magnitude:.3f}T exceeds limit {self.field_limit}T")
            
        self.field_x(field_x)
        self.field_y(field_y)
        
        # Start ramp
        self.write('RAMP')
        
        if wait_for_completion:
            self.wait_for_ramp_completion()
            
    def set_field_polar(self, magnitude: float, angle_deg: float,
                       wait_for_completion: bool = True) -> None:
        """
        Set magnetic field using polar coordinates.
        
        Args:
            magnitude: Field magnitude in Tesla
            angle_deg: Field angle in degrees
            wait_for_completion: Whether to wait for ramp completion
        """
        angle_rad = np.radians(angle_deg)
        field_x = magnitude * np.cos(angle_rad)
        field_y = magnitude * np.sin(angle_rad)
        
        self.set_field_vector(field_x, field_y, wait_for_completion)
        
    def wait_for_ramp_completion(self, timeout: float = 300) -> None:
        """
        Wait for magnetic field ramp to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.magnet_status()
            if 'HOLDING' in status.upper():
                break
            time.sleep(1.0)
        else:
            raise TimeoutError("Magnet ramp did not complete within timeout")
            
    def ramp_to_zero(self, wait_for_completion: bool = True) -> None:
        """
        Safely ramp magnetic field to zero.
        
        Args:
            wait_for_completion: Whether to wait for ramp completion
        """
        self.set_field_vector(0.0, 0.0, wait_for_completion)
        
    def emergency_stop(self) -> None:
        """Emergency stop all magnet operations."""
        self.write('PAUSE')
        
    def get_idn(self) -> dict:
        """Get instrument identification."""
        response = self.ask('*IDN?')
        parts = response.split(',')
        return {
            'vendor': parts[0] if len(parts) > 0 else '',
            'model': parts[1] if len(parts) > 1 else '',
            'serial': parts[2] if len(parts) > 2 else '', 
            'firmware': parts[3] if len(parts) > 3 else ''
        }