"""
Lakeshore 372 Temperature Controller Driver

QCoDeS driver for the Lakeshore 372 AC resistance bridge
used for temperature measurement and control in dilution refrigerators.
"""

import time
from typing import Union, Dict
from qcodes import VisaInstrument, validators as vals
from qcodes.parameters import Parameter


class Lakeshore372(VisaInstrument):
    """
    QCoDeS driver for Lakeshore 372 AC Resistance Bridge Temperature Controller.
    
    Provides temperature measurement and control for dilution refrigerator
    systems with multiple measurement channels.
    """
    
    def __init__(self, name: str, address: str, **kwargs):
        """
        Initialize Lakeshore 372 temperature controller.
        
        Args:
            name: Name of the instrument
            address: VISA resource address
        """
        super().__init__(name, address, terminator='\r\n', **kwargs)
        
        # Temperature reading channels (1-16 available)
        for i in range(1, 17):
            self.add_parameter(
                f'temperature_{i:02d}',
                get_cmd=f'KRDG? {i}',
                unit='K',
                docstring=f'Temperature reading from channel {i}'
            )
            
            self.add_parameter(
                f'resistance_{i:02d}',
                get_cmd=f'SRDG? {i}',
                unit='Ohm',
                docstring=f'Resistance reading from channel {i}'
            )
        
        # Control loop parameters (2 control outputs available)
        for i in range(1, 3):
            self.add_parameter(
                f'setpoint_{i}',
                get_cmd=f'SETP? {i}',
                set_cmd=f'SETP {i},{{:.6f}}',
                unit='K',
                vals=vals.Numbers(0, 400),
                docstring=f'Temperature setpoint for control loop {i}'
            )
            
            self.add_parameter(
                f'heater_output_{i}',
                get_cmd=f'HTR? {i}',
                unit='%',
                docstring=f'Heater output percentage for loop {i}'
            )
            
            self.add_parameter(
                f'heater_range_{i}',
                get_cmd=f'RANGE? {i}',
                set_cmd=f'RANGE {i},{{}}',
                vals=vals.Enum(0, 1, 2, 3, 4, 5),
                docstring=f'Heater range setting for loop {i}'
            )
        
        # PID parameters for control loop 1
        self.add_parameter(
            'pid_p1',
            get_cmd='PID? 1',
            set_cmd=self._set_pid_1,
            docstring='PID parameters for control loop 1 (P, I, D)'
        )
        
        self.add_parameter(
            'pid_p2', 
            get_cmd='PID? 2',
            set_cmd=self._set_pid_2,
            docstring='PID parameters for control loop 2 (P, I, D)'
        )
        
        # Commonly used temperature channels with descriptive names
        self.add_parameter(
            'mixing_chamber_temp',
            get_cmd='KRDG? 1',  # Typically channel 1
            unit='K',
            docstring='Mixing chamber temperature'
        )
        
        self.add_parameter(
            'still_temp',
            get_cmd='KRDG? 2',  # Typically channel 2
            unit='K', 
            docstring='Still temperature'
        )
        
        self.add_parameter(
            'cold_plate_temp',
            get_cmd='KRDG? 3',  # Typically channel 3
            unit='K',
            docstring='Cold plate temperature' 
        )
        
        self.add_parameter(
            'magnet_temp',
            get_cmd='KRDG? 4',  # Typically channel 4
            unit='K',
            docstring='Magnet temperature'
        )
        
        # Scanner configuration
        self.add_parameter(
            'scanner_channel',
            get_cmd='SCAN?',
            set_cmd='SCAN {}',
            vals=vals.Ints(0, 16),
            docstring='Scanner channel (0 for off, 1-16 for channels)'
        )
        
        self.add_parameter(
            'scanner_dwell',
            get_cmd='DWEL?',
            set_cmd='DWEL {:.1f}',
            unit='s',
            vals=vals.Numbers(1, 200),
            docstring='Scanner dwell time per channel'
        )
        
        self.connect_message()
        
    def _set_pid_1(self, pid_values: str) -> None:
        """Set PID parameters for control loop 1."""
        self.write(f'PID 1,{pid_values}')
        
    def _set_pid_2(self, pid_values: str) -> None:
        """Set PID parameters for control loop 2."""
        self.write(f'PID 2,{pid_values}')
        
    def get_all_temperatures(self) -> Dict[int, float]:
        """
        Get temperature readings from all 16 channels.
        
        Returns:
            Dictionary mapping channel numbers to temperatures in K
        """
        temperatures = {}
        for i in range(1, 17):
            try:
                temp = float(self.ask(f'KRDG? {i}'))
                temperatures[i] = temp
            except (ValueError, Exception):
                temperatures[i] = float('nan')
        return temperatures
        
    def get_all_resistances(self) -> Dict[int, float]:
        """
        Get resistance readings from all 16 channels.
        
        Returns:
            Dictionary mapping channel numbers to resistances in Ohms
        """
        resistances = {}
        for i in range(1, 17):
            try:
                res = float(self.ask(f'SRDG? {i}'))
                resistances[i] = res
            except (ValueError, Exception):
                resistances[i] = float('nan')
        return resistances
        
    def configure_control_loop(self, loop: int, input_channel: int, 
                              units: str = 'K', powerup_enable: bool = True,
                              setpoint: float = None) -> None:
        """
        Configure a control loop.
        
        Args:
            loop: Control loop number (1 or 2)
            input_channel: Input channel for control (1-16)
            units: Control units ('K' for Kelvin, 'S' for sensor units)
            powerup_enable: Enable control on power up
            setpoint: Initial setpoint temperature
        """
        enable = 1 if powerup_enable else 0
        self.write(f'CSET {loop},{input_channel},{units},{enable}')
        
        if setpoint is not None:
            self.write(f'SETP {loop},{setpoint:.6f}')
            
    def set_heater_range(self, loop: int, range_setting: int) -> None:
        """
        Set heater range for control loop.
        
        Args:
            loop: Control loop number (1 or 2)  
            range_setting: Range setting (0=Off, 1-5 for different power ranges)
        """
        self.write(f'RANGE {loop},{range_setting}')
        
    def set_pid_parameters(self, loop: int, p: float, i: float, d: float) -> None:
        """
        Set PID parameters for control loop.
        
        Args:
            loop: Control loop number (1 or 2)
            p: Proportional gain
            i: Integral gain  
            d: Derivative gain
        """
        self.write(f'PID {loop},{p:.3f},{i:.3f},{d:.3f}')
        
    def ramp_temperature(self, loop: int, setpoint: float, 
                        ramp_rate: float, units: str = 'K') -> None:
        """
        Ramp temperature to setpoint at specified rate.
        
        Args:
            loop: Control loop number (1 or 2)
            setpoint: Target temperature
            ramp_rate: Ramp rate in K/min or K/s
            units: Rate units ('K/min' or 'K/s')
        """
        # Enable ramping
        self.write(f'RAMP {loop},1,{ramp_rate:.3f}')
        # Set new setpoint
        self.write(f'SETP {loop},{setpoint:.6f}')
        
    def stop_ramp(self, loop: int) -> None:
        """
        Stop temperature ramp for control loop.
        
        Args:
            loop: Control loop number (1 or 2)
        """
        self.write(f'RAMP {loop},0')
        
    def wait_for_temperature(self, loop: int, target: float, 
                           tolerance: float = 0.01, timeout: float = 3600,
                           check_interval: float = 10) -> bool:
        """
        Wait for temperature to reach target within tolerance.
        
        Args:
            loop: Control loop number (1 or 2)
            target: Target temperature in K
            tolerance: Temperature tolerance in K
            timeout: Maximum wait time in seconds
            check_interval: Time between temperature checks in seconds
            
        Returns:
            True if temperature reached target, False if timeout
        """
        start_time = time.time()
        
        # Get the input channel for this loop
        cset_response = self.ask(f'CSET? {loop}')
        input_channel = int(cset_response.split(',')[0])
        
        while time.time() - start_time < timeout:
            current_temp = float(self.ask(f'KRDG? {input_channel}'))
            
            if abs(current_temp - target) <= tolerance:
                return True
                
            time.sleep(check_interval)
            
        return False
        
    def configure_scanner(self, channels: list, dwell_time: float = 10.0) -> None:
        """
        Configure scanner for multiple channel monitoring.
        
        Args:
            channels: List of channel numbers to scan
            dwell_time: Time to spend on each channel in seconds
        """
        if not channels:
            # Turn off scanner
            self.write('SCAN 0')
            return
            
        # Set dwell time
        self.write(f'DWEL {dwell_time:.1f}')
        
        # Configure scanner channels
        channel_str = ','.join(map(str, channels))
        self.write(f'SCAN {channel_str}')
        
    def get_scanner_status(self) -> Dict[str, Union[int, float]]:
        """
        Get scanner configuration and status.
        
        Returns:
            Dictionary with scanner settings
        """
        scan_response = self.ask('SCAN?')
        dwell_time = float(self.ask('DWEL?'))
        
        return {
            'scanning_channels': scan_response,
            'dwell_time': dwell_time
        }
        
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