"""
Safety checks and instrument protection utilities.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings


class SafetyChecks:
    """
    Safety checks for instrument operation and measurement parameters.
    
    Provides protection against dangerous parameter combinations and
    out-of-specification operation.
    """
    
    # Safety limits (conservative defaults)
    DEFAULT_LIMITS = {
        'max_magnetic_field': 9.0,      # Tesla
        'max_field_ramp_rate': 1.0,     # T/min  
        'max_current': 0.1,             # A
        'max_voltage': 200.0,           # V
        'max_temperature': 400.0,       # K
        'min_temperature': 0.01,        # K
        'max_temperature_ramp_rate': 5.0,  # K/min
        'max_heater_power': 100.0,      # W
    }
    
    def __init__(self, custom_limits: Optional[Dict] = None):
        """
        Initialize safety checker.
        
        Args:
            custom_limits: Dictionary of custom safety limits
        """
        self.limits = self.DEFAULT_LIMITS.copy()
        if custom_limits:
            self.limits.update(custom_limits)
            
    def check_magnetic_field(self, field_x: float, field_y: float, 
                           field_z: float = 0.0) -> bool:
        """
        Check if magnetic field vector is within safe limits.
        
        Args:
            field_x: X-axis field in Tesla
            field_y: Y-axis field in Tesla  
            field_z: Z-axis field in Tesla
            
        Returns:
            True if safe, False otherwise
        """
        field_magnitude = np.sqrt(field_x**2 + field_y**2 + field_z**2)
        
        if field_magnitude > self.limits['max_magnetic_field']:
            warnings.warn(f"Field magnitude {field_magnitude:.3f} T exceeds limit "
                         f"{self.limits['max_magnetic_field']:.3f} T")
            return False
            
        return True
        
    def check_field_ramp_rate(self, ramp_rate: float) -> bool:
        """
        Check if field ramp rate is within safe limits.
        
        Args:
            ramp_rate: Ramp rate in T/min
            
        Returns:
            True if safe, False otherwise
        """
        if ramp_rate > self.limits['max_field_ramp_rate']:
            warnings.warn(f"Field ramp rate {ramp_rate:.3f} T/min exceeds limit "
                         f"{self.limits['max_field_ramp_rate']:.3f} T/min")
            return False
            
        return True
        
    def check_current(self, current: float) -> bool:
        """
        Check if current is within safe limits.
        
        Args:
            current: Current in A
            
        Returns:
            True if safe, False otherwise
        """
        if abs(current) > self.limits['max_current']:
            warnings.warn(f"Current {abs(current):.6f} A exceeds limit "
                         f"{self.limits['max_current']:.6f} A")
            return False
            
        return True
        
    def check_voltage(self, voltage: float) -> bool:
        """
        Check if voltage is within safe limits.
        
        Args:
            voltage: Voltage in V
            
        Returns:
            True if safe, False otherwise
        """
        if abs(voltage) > self.limits['max_voltage']:
            warnings.warn(f"Voltage {abs(voltage):.3f} V exceeds limit "
                         f"{self.limits['max_voltage']:.3f} V")
            return False
            
        return True
        
    def check_temperature(self, temperature: float) -> bool:
        """
        Check if temperature is within safe limits.
        
        Args:
            temperature: Temperature in K
            
        Returns:
            True if safe, False otherwise
        """
        if temperature > self.limits['max_temperature']:
            warnings.warn(f"Temperature {temperature:.3f} K exceeds maximum "
                         f"{self.limits['max_temperature']:.3f} K")
            return False
            
        if temperature < self.limits['min_temperature']:
            warnings.warn(f"Temperature {temperature:.6f} K below minimum "
                         f"{self.limits['min_temperature']:.6f} K")
            return False
            
        return True
        
    def check_temperature_ramp_rate(self, ramp_rate: float) -> bool:
        """
        Check if temperature ramp rate is within safe limits.
        
        Args:
            ramp_rate: Temperature ramp rate in K/min
            
        Returns:
            True if safe, False otherwise
        """
        if ramp_rate > self.limits['max_temperature_ramp_rate']:
            warnings.warn(f"Temperature ramp rate {ramp_rate:.3f} K/min exceeds limit "
                         f"{self.limits['max_temperature_ramp_rate']:.3f} K/min")
            return False
            
        return True
        
    def check_sweep_parameters(self, sweep_params: Dict) -> bool:
        """
        Check if sweep parameters are safe.
        
        Args:
            sweep_params: Dictionary with sweep parameters
            
        Returns:
            True if all parameters are safe
        """
        safe = True
        
        # Check current sweep
        if 'current_range' in sweep_params:
            current_min, current_max = sweep_params['current_range']
            if not (self.check_current(current_min) and self.check_current(current_max)):
                safe = False
                
        # Check voltage sweep
        if 'voltage_range' in sweep_params:
            voltage_min, voltage_max = sweep_params['voltage_range']
            if not (self.check_voltage(voltage_min) and self.check_voltage(voltage_max)):
                safe = False
                
        # Check field sweep
        if 'field_range' in sweep_params:
            field_min, field_max = sweep_params['field_range']
            if not (self.check_magnetic_field(field_max, 0) and 
                    self.check_magnetic_field(field_min, 0)):
                safe = False
                
        # Check temperature sweep
        if 'temperature_range' in sweep_params:
            temp_min, temp_max = sweep_params['temperature_range']
            if not (self.check_temperature(temp_min) and self.check_temperature(temp_max)):
                safe = False
                
        return safe
        
    def estimate_sweep_time(self, sweep_params: Dict) -> float:
        """
        Estimate total time for a sweep measurement.
        
        Args:
            sweep_params: Dictionary with sweep parameters
            
        Returns:
            Estimated time in seconds
        """
        total_time = 0.0
        
        # Number of points
        num_points = sweep_params.get('num_points', 100)
        
        # Delay between points
        point_delay = sweep_params.get('delay_between_points', 0.1)
        total_time += num_points * point_delay
        
        # Field ramp time
        if 'field_range' in sweep_params:
            field_min, field_max = sweep_params['field_range']
            field_change = abs(field_max - field_min)
            ramp_rate = sweep_params.get('field_ramp_rate', 0.1)  # T/min
            ramp_time = field_change / ramp_rate * 60  # Convert to seconds
            total_time += ramp_time
            
        # Temperature ramp time
        if 'temperature_range' in sweep_params:
            temp_min, temp_max = sweep_params['temperature_range']
            temp_change = abs(temp_max - temp_min)
            temp_ramp_rate = sweep_params.get('temp_ramp_rate', 1.0)  # K/min
            temp_ramp_time = temp_change / temp_ramp_rate * 60
            temp_settling = sweep_params.get('temp_settling_time', 300)  # seconds per point
            total_time += temp_ramp_time + num_points * temp_settling
            
        return total_time
        
    def validate_measurement_sequence(self, sequence: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate a sequence of measurements for safety.
        
        Args:
            sequence: List of measurement parameter dictionaries
            
        Returns:
            Tuple of (is_safe, list_of_warnings)
        """
        is_safe = True
        warnings_list = []
        
        for i, measurement in enumerate(sequence):
            # Check individual measurement safety
            if not self.check_sweep_parameters(measurement):
                is_safe = False
                warnings_list.append(f"Measurement {i+1} has unsafe parameters")
                
            # Check for dangerous transitions between measurements
            if i > 0:
                prev_measurement = sequence[i-1]
                
                # Check field transitions
                if 'field_setpoint' in measurement and 'field_setpoint' in prev_measurement:
                    field_change = abs(measurement['field_setpoint'] - prev_measurement['field_setpoint'])
                    if field_change > 1.0:  # Large field jump
                        warnings_list.append(f"Large field change ({field_change:.3f} T) "
                                           f"between measurements {i} and {i+1}")
                        
                # Check temperature transitions  
                if 'temperature_setpoint' in measurement and 'temperature_setpoint' in prev_measurement:
                    temp_change = abs(measurement['temperature_setpoint'] - prev_measurement['temperature_setpoint'])
                    if temp_change > 10.0:  # Large temperature jump
                        warnings_list.append(f"Large temperature change ({temp_change:.1f} K) "
                                           f"between measurements {i} and {i+1}")
                        
        return is_safe, warnings_list
        
    def emergency_safe_state(self) -> Dict[str, float]:
        """
        Return parameters for emergency safe state.
        
        Returns:
            Dictionary with safe parameter values
        """
        return {
            'current': 0.0,
            'voltage': 0.0,
            'field_x': 0.0,
            'field_y': 0.0,
            'field_z': 0.0,
            'heater_range': 0,  # Turn off heaters
            'output_enable': False
        }
        
    def check_instrument_limits(self, instrument_type: str, parameter: str, 
                              value: float) -> bool:
        """
        Check parameter against instrument-specific limits.
        
        Args:
            instrument_type: Type of instrument ('keithley6221', 'ami430', etc.)
            parameter: Parameter name
            value: Parameter value
            
        Returns:
            True if within limits
        """
        # Instrument-specific limits
        instrument_limits = {
            'keithley6221': {
                'current': 0.105,  # ±105 mA
                'compliance_voltage': 105.0
            },
            'keithley2182a': {
                'voltage_range': 100.0
            },
            'keithley2636b': {
                'voltage': 200.0,
                'current': 1.5
            },
            'ami430': {
                'field': 9.0,
                'ramp_rate': 1.0
            },
            'lakeshore372': {
                'temperature': 400.0,
                'heater_range': 5
            }
        }
        
        if instrument_type in instrument_limits:
            limits = instrument_limits[instrument_type]
            if parameter in limits:
                limit = limits[parameter]
                if abs(value) > limit:
                    warnings.warn(f"{instrument_type} {parameter} {abs(value):.6f} "
                                 f"exceeds instrument limit {limit:.6f}")
                    return False
                    
        return True


class InterlocksManager:
    """
    Manages software interlocks for the measurement system.
    """
    
    def __init__(self):
        """Initialize interlocks manager."""
        self.interlocks = {
            'magnetic_field_enabled': True,
            'temperature_control_enabled': True,
            'high_current_enabled': False,
            'high_voltage_enabled': False
        }
        
        self.interlock_conditions = []
        
    def add_interlock(self, name: str, condition_func: callable, 
                     message: str) -> None:
        """
        Add a custom interlock condition.
        
        Args:
            name: Interlock name
            condition_func: Function that returns True if safe
            message: Error message if interlock triggers
        """
        self.interlock_conditions.append({
            'name': name,
            'condition': condition_func,
            'message': message
        })
        
    def check_interlocks(self, station) -> Tuple[bool, List[str]]:
        """
        Check all interlocks.
        
        Args:
            station: BlueforsStation instance
            
        Returns:
            Tuple of (all_safe, list_of_errors)
        """
        all_safe = True
        errors = []
        
        # Check basic interlocks
        if not self.interlocks['magnetic_field_enabled'] and station.magnet:
            field_magnitude = station.magnet.field_magnitude()
            if field_magnitude > 0.1:  # Small tolerance for zero field
                all_safe = False
                errors.append("Magnetic field interlock: Field is not at zero")
                
        # Check custom interlocks
        for interlock in self.interlock_conditions:
            try:
                if not interlock['condition'](station):
                    all_safe = False
                    errors.append(f"Interlock '{interlock['name']}': {interlock['message']}")
            except Exception as e:
                all_safe = False
                errors.append(f"Interlock '{interlock['name']}' error: {str(e)}")
                
        return all_safe, errors
        
    def enable_interlock(self, interlock_name: str) -> None:
        """Enable specific interlock."""
        if interlock_name in self.interlocks:
            self.interlocks[interlock_name] = True
            
    def disable_interlock(self, interlock_name: str) -> None:
        """Disable specific interlock (use with caution!)."""
        if interlock_name in self.interlocks:
            self.interlocks[interlock_name] = False
            warnings.warn(f"Interlock '{interlock_name}' disabled - use with extreme caution!")
            
    def reset_interlocks(self) -> None:
        """Reset all interlocks to default safe state."""
        self.interlocks = {
            'magnetic_field_enabled': True,
            'temperature_control_enabled': True,
            'high_current_enabled': False,
            'high_voltage_enabled': False
        }