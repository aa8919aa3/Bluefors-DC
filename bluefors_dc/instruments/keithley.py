"""
Keithley Instrument Drivers

QCoDeS drivers for Keithley measurement instruments:
- Keithley 6221: Current source
- Keithley 2182A: Nanovoltmeter  
- Keithley 2636B: Dual voltage source
"""

import time
from typing import Union, List
from qcodes import VisaInstrument, validators as vals
from qcodes.parameters import Parameter


class Keithley6221(VisaInstrument):
    """
    QCoDeS driver for Keithley 6221 AC/DC Current Source.
    
    Provides precise current sourcing capabilities for resistance
    and I-V measurements.
    """
    
    def __init__(self, name: str, address: str, **kwargs):
        """
        Initialize Keithley 6221 current source.
        
        Args:
            name: Name of the instrument
            address: VISA resource address
        """
        super().__init__(name, address, terminator='\n', **kwargs)
        
        # Current source parameter
        self.add_parameter(
            'current',
            get_cmd='SOUR:CURR?',
            set_cmd='SOUR:CURR {:.9f}',
            unit='A',
            vals=vals.Numbers(-0.105, 0.105),  # ±105 mA max
            docstring='Current source level'
        )
        
        # Current range
        self.add_parameter(
            'current_range',
            get_cmd='SOUR:CURR:RANG?',
            set_cmd='SOUR:CURR:RANG {:.6f}',
            unit='A',
            vals=vals.Numbers(2e-9, 0.105),
            docstring='Current source range'
        )
        
        # Output state
        self.add_parameter(
            'output',
            get_cmd='OUTP?',
            set_cmd='OUTP {}',
            val_mapping={'ON': 1, 'OFF': 0},
            docstring='Output state'
        )
        
        # Compliance voltage
        self.add_parameter(
            'compliance_voltage',
            get_cmd='SOUR:CURR:COMP?',
            set_cmd='SOUR:CURR:COMP {:.3f}',
            unit='V',
            vals=vals.Numbers(-105, 105),
            docstring='Current source compliance voltage'
        )
        
        self.connect_message()
        
    def reset(self) -> None:
        """Reset instrument to default state."""
        self.write('*RST')
        self.write('*CLS')
        
    def configure_delta_mode(self, high_current: float, low_current: float, 
                           delta_delay: float = 0.001) -> None:
        """
        Configure delta mode for differential measurements.
        
        Args:
            high_current: High current level in A
            low_current: Low current level in A  
            delta_delay: Delay between current levels in seconds
        """
        self.write(f'SOUR:DELT:HIGH {high_current:.9f}')
        self.write(f'SOUR:DELT:LOW {low_current:.9f}')
        self.write(f'SOUR:DELT:DEL {delta_delay:.6f}')
        self.write('SOUR:DELT:STAT ON')


class Keithley2182A(VisaInstrument):
    """
    QCoDeS driver for Keithley 2182A Nanovoltmeter.
    
    Provides high precision voltage measurements for low-resistance
    and low-voltage applications.
    """
    
    def __init__(self, name: str, address: str, **kwargs):
        """
        Initialize Keithley 2182A nanovoltmeter.
        
        Args:
            name: Name of the instrument
            address: VISA resource address
        """
        super().__init__(name, address, terminator='\n', **kwargs)
        
        # Voltage measurement parameter
        self.add_parameter(
            'voltage',
            get_cmd='READ?',
            unit='V',
            docstring='Measured voltage'
        )
        
        # Voltage range
        self.add_parameter(
            'voltage_range',
            get_cmd='SENS:VOLT:RANG?',
            set_cmd='SENS:VOLT:RANG {:.6f}',
            unit='V',
            vals=vals.Numbers(10e-9, 100),
            docstring='Voltage measurement range'
        )
        
        # Integration time/NPLC
        self.add_parameter(
            'nplc',
            get_cmd='SENS:VOLT:NPLC?',
            set_cmd='SENS:VOLT:NPLC {:.3f}',
            vals=vals.Numbers(0.01, 50),
            docstring='Integration time in number of power line cycles'
        )
        
        # Channel selection
        self.add_parameter(
            'channel',
            get_cmd='SENS:CHAN?',
            set_cmd='SENS:CHAN {}',
            vals=vals.Ints(1, 2),
            docstring='Input channel selection'
        )
        
        # Auto range
        self.add_parameter(
            'auto_range',
            get_cmd='SENS:VOLT:RANG:AUTO?',
            set_cmd='SENS:VOLT:RANG:AUTO {}',
            val_mapping={'ON': 1, 'OFF': 0},
            docstring='Auto range state'
        )
        
        self.connect_message()
        
    def configure_delta_mode(self) -> None:
        """Configure for delta mode measurements with K6221."""
        self.write('SENS:VOLT:DFIL:STAT ON')  # Enable delta filter
        self.write('SENS:VOLT:LPAS:STAT OFF') # Disable low pass filter
        
    def take_measurement(self, average_count: int = 1) -> float:
        """
        Take voltage measurement with optional averaging.
        
        Args:
            average_count: Number of measurements to average
            
        Returns:
            Averaged voltage measurement
        """
        if average_count == 1:
            return float(self.ask('READ?'))
        
        measurements = []
        for _ in range(average_count):
            measurements.append(float(self.ask('read?')))
            
        return sum(measurements) / len(measurements)


class Keithley2636B(VisaInstrument):
    """
    QCoDeS driver for Keithley 2636B Dual Channel Source Measure Unit.
    
    Provides voltage/current sourcing and measurement capabilities
    for both channels A and B.
    """
    
    def __init__(self, name: str, address: str, **kwargs):
        """
        Initialize Keithley 2636B dual SMU.
        
        Args:
            name: Name of the instrument
            address: VISA resource address
        """
        super().__init__(name, address, terminator='\n', **kwargs)
        
        # Channel A parameters
        self.add_parameter(
            'voltage_a',
            get_cmd='print(smua.measure.v())',
            set_cmd='smua.source.levelv = {:.6f}',
            unit='V',
            vals=vals.Numbers(-200, 200),
            docstring='Channel A voltage'
        )
        
        self.add_parameter(
            'current_a',
            get_cmd='print(smua.measure.i())',
            set_cmd='smua.source.leveli = {:.9f}',
            unit='A',
            vals=vals.Numbers(-1.5, 1.5),
            docstring='Channel A current'
        )
        
        # Channel B parameters  
        self.add_parameter(
            'voltage_b',
            get_cmd='print(smub.measure.v())',
            set_cmd='smub.source.levelv = {:.6f}',
            unit='V', 
            vals=vals.Numbers(-200, 200),
            docstring='Channel B voltage'
        )
        
        self.add_parameter(
            'current_b',
            get_cmd='print(smub.measure.i())',
            set_cmd='smub.source.leveli = {:.9f}',
            unit='A',
            vals=vals.Numbers(-1.5, 1.5),
            docstring='Channel B current'
        )
        
        # Output states
        self.add_parameter(
            'output_a',
            get_cmd='print(smua.source.output)',
            set_cmd='smua.source.output = {}',
            val_mapping={True: 'smua.OUTPUT_ON', False: 'smua.OUTPUT_OFF'},
            docstring='Channel A output state'
        )
        
        self.add_parameter(
            'output_b',
            get_cmd='print(smub.source.output)',
            set_cmd='smub.source.output = {}',
            val_mapping={True: 'smub.OUTPUT_ON', False: 'smub.OUTPUT_OFF'},
            docstring='Channel B output state'
        )
        
        self.connect_message()
        
    def configure_voltage_source(self, channel: str = 'a') -> None:
        """
        Configure channel as voltage source.
        
        Args:
            channel: 'a' or 'b' for channel selection
        """
        smu = f'smu{channel}'
        self.write(f'{smu}.source.func = {smu}.OUTPUT_DCVOLTS')
        
    def configure_current_source(self, channel: str = 'a') -> None:
        """
        Configure channel as current source.
        
        Args:
            channel: 'a' or 'b' for channel selection
        """
        smu = f'smu{channel}'
        self.write(f'{smu}.source.func = {smu}.OUTPUT_DCAMPS')
        
    def set_compliance(self, channel: str, voltage_limit: float = None,
                      current_limit: float = None) -> None:
        """
        Set compliance limits for a channel.
        
        Args:
            channel: 'a' or 'b' for channel selection
            voltage_limit: Voltage compliance limit in V
            current_limit: Current compliance limit in A
        """
        smu = f'smu{channel}'
        if voltage_limit is not None:
            self.write(f'{smu}.source.limitv = {voltage_limit:.6f}')
        if current_limit is not None:
            self.write(f'{smu}.source.limiti = {current_limit:.9f}')
            
    def measure_iv(self, channel: str) -> tuple:
        """
        Measure current and voltage simultaneously.
        
        Args:
            channel: 'a' or 'b' for channel selection
            
        Returns:
            Tuple of (current, voltage) measurements
        """
        smu = f'smu{channel}'
        result = self.ask(f'print({smu}.measure.iv())')
        values = result.split('\t')
        return float(values[0]), float(values[1])
        
    def reset(self) -> None:
        """Reset both channels to safe defaults."""
        self.write('reset()')
        self.write('smua.source.output = smua.OUTPUT_OFF')
        self.write('smub.source.output = smub.OUTPUT_OFF')