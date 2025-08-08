"""
Keithley Instrument Drivers

QCoDeS drivers for Keithley measurement instruments:
- Keithley 6221: Current source
- Keithley 2182A: Nanovoltmeter  
- Keithley 2636B: Dual voltage source

Enhanced drivers following PyMeasure reference implementations and QCoDeS guidelines.
"""

import time
import warnings
import numpy as np
from typing import Union, List, Optional, Tuple
from qcodes import VisaInstrument, validators as vals
from qcodes.parameters import Parameter


class Keithley6221(VisaInstrument):
    """
    QCoDeS driver for Keithley 6221 AC/DC Current Source.
    
    Enhanced driver providing precise current sourcing capabilities for resistance
    and I-V measurements, with support for delta mode operations, waveform generation,
    and advanced triggering.

    Args:
        name: Name of the instrument
        address: VISA resource address
        **kwargs: Additional arguments passed to VisaInstrument
    """
    
    def __init__(self, name: str, address: str, **kwargs):
        """Initialize Keithley 6221 current source."""
        super().__init__(name, address, terminator='\n', **kwargs)
        
        # OUTPUT PARAMETERS
        self.add_parameter(
            'source_enabled',
            get_cmd='OUTP?',
            set_cmd='OUTP {}',
            val_mapping={True: 1, False: 0},
            docstring='Control whether the source is enabled'
        )
        
        # Backward compatibility alias
        self.add_parameter(
            'output',
            get_cmd='OUTP?',
            set_cmd='OUTP {}',
            val_mapping={'ON': 1, 'OFF': 0},
            docstring='Output state (backward compatibility)'
        )
        
        self.add_parameter(
            'shield_to_guard_enabled',
            get_cmd=':OUTP:ISH?',
            set_cmd=':OUTP:ISH {}',
            val_mapping={True: 'GUAR', False: 'OLOW'},
            docstring='Control if shield is connected to the guard'
        )
        
        self.add_parameter(
            'source_delay',
            get_cmd=':SOUR:DEL?',
            set_cmd=':SOUR:DEL {:.6f}',
            unit='s',
            vals=vals.Numbers(1e-3, 999999.999),
            docstring='Manual delay for the source after output is turned on'
        )
        
        self.add_parameter(
            'output_low_grounded',
            get_cmd=':OUTP:LTE?',
            set_cmd=':OUTP:LTE {}',
            val_mapping={True: 1, False: 0},
            docstring='Whether low output is connected to earth ground or floating'
        )
        
        # SOURCE PARAMETERS
        self.add_parameter(
            'source_current',
            get_cmd=':SOUR:CURR?',
            set_cmd=':SOUR:CURR {:.9f}',
            unit='A',
            vals=vals.Numbers(-0.105, 0.105),
            docstring='Source current level'
        )
        
        # Backward compatibility alias
        self.add_parameter(
            'current',
            get_cmd='SOUR:CURR?',
            set_cmd='SOUR:CURR {:.9f}',
            unit='A',
            vals=vals.Numbers(-0.105, 0.105),
            docstring='Current source level (backward compatibility)'
        )
        
        self.add_parameter(
            'source_compliance',
            get_cmd=':SOUR:CURR:COMP?',
            set_cmd=':SOUR:CURR:COMP {:.3f}',
            unit='V',
            vals=vals.Numbers(0.1, 105),
            docstring='Compliance of the current source in Volts'
        )
        
        # Backward compatibility alias
        self.add_parameter(
            'compliance_voltage',
            get_cmd='SOUR:CURR:COMP?',
            set_cmd='SOUR:CURR:COMP {:.3f}',
            unit='V',
            vals=vals.Numbers(-105, 105),
            docstring='Current source compliance voltage (backward compatibility)'
        )
        
        self.add_parameter(
            'source_range',
            get_cmd=':SOUR:CURR:RANG?',
            set_cmd=':SOUR:CURR:RANG:AUTO 0;:SOUR:CURR:RANG {:.6f}',
            unit='A',
            vals=vals.Numbers(-0.105, 0.105),
            docstring='Source current range (auto-range disabled when set)'
        )
        
        # Backward compatibility alias
        self.add_parameter(
            'current_range',
            get_cmd='SOUR:CURR:RANG?',
            set_cmd='SOUR:CURR:RANG {:.6f}',
            unit='A',
            vals=vals.Numbers(2e-9, 0.105),
            docstring='Current source range (backward compatibility)'
        )
        
        self.add_parameter(
            'source_auto_range',
            get_cmd=':SOUR:CURR:RANG:AUTO?',
            set_cmd=':SOUR:CURR:RANG:AUTO {}',
            val_mapping={True: 1, False: 0},
            docstring='Auto range of the current source'
        )
        
        # DELTA MODE PARAMETERS
        self.add_parameter(
            'delta_unit',
            get_cmd=':UNIT:VOLT:DC?',
            set_cmd=':UNIT:VOLT:DC {}',
            val_mapping={'V': 'V', 'Ohms': 'OHMS', 'W': 'W', 'Siemens': 'SIEM'},
            docstring='Reading unit for delta measurements'
        )
        
        self.add_parameter(
            'delta_high_source',
            get_cmd=':SOUR:DELT:HIGH?',
            set_cmd=':SOUR:DELT:HIGH {:.9f}',
            unit='A',
            vals=vals.Numbers(0, 0.105),
            docstring='Delta high source value in A'
        )
        
        self.add_parameter(
            'delta_low_source',
            get_cmd=':SOUR:DELT:LOW?',
            set_cmd=':SOUR:DELT:LOW {:.9f}',
            unit='A',
            vals=vals.Numbers(-0.105, 0),
            docstring='Delta low source value in A'
        )
        
        self.add_parameter(
            'delta_delay',
            get_cmd=':SOUR:DELT:DEL?',
            set_cmd=':SOUR:DELT:DEL {}',
            vals=vals.MultiType(vals.Numbers(0, 9999.999), vals.Enum('INF')),
            docstring='Delta delay in seconds or INF'
        )
        
        self.add_parameter(
            'delta_cycles',
            get_cmd=':SOUR:DELT:COUN?',
            set_cmd=':SOUR:DELT:COUN {}',
            vals=vals.MultiType(vals.Ints(1, 65536), vals.Enum('INF')),
            docstring='Number of cycles to run for delta measurements'
        )
        
        self.add_parameter(
            'delta_measurement_sets',
            get_cmd=':SOUR:SWE:COUN?',
            set_cmd=':SOUR:SWE:COUN {}',
            vals=vals.MultiType(vals.Ints(1, 65536), vals.Enum('INF')),
            docstring='Number of measurement sets to repeat for delta measurements'
        )
        
        self.add_parameter(
            'delta_compliance_abort_enabled',
            get_cmd=':SOUR:DELT:CAB?',
            set_cmd=':SOUR:DELT:CAB {}',
            val_mapping={True: 'ON', False: 'OFF'},
            docstring='Whether compliance abort is enabled for delta mode'
        )
        
        # WAVEFORM PARAMETERS
        self.add_parameter(
            'waveform_function',
            get_cmd=':SOUR:WAVE:FUNC?',
            set_cmd=':SOUR:WAVE:FUNC {}',
            val_mapping={
                'sine': 'SIN', 'ramp': 'RAMP', 'square': 'SQU',
                'arbitrary1': 'ARB1', 'arbitrary2': 'ARB2', 
                'arbitrary3': 'ARB3', 'arbitrary4': 'ARB4'
            },
            docstring='Selected wave function'
        )
        
        self.add_parameter(
            'waveform_frequency',
            get_cmd=':SOUR:WAVE:FREQ?',
            set_cmd=':SOUR:WAVE:FREQ {:.6f}',
            unit='Hz',
            vals=vals.Numbers(1e-3, 1e5),
            docstring='Frequency of the waveform in Hz'
        )
        
        self.add_parameter(
            'waveform_amplitude',
            get_cmd=':SOUR:WAVE:AMPL?',
            set_cmd=':SOUR:WAVE:AMPL {:.9f}',
            unit='A',
            vals=vals.Numbers(2e-12, 0.105),
            docstring='Peak amplitude of the waveform in Amps'
        )
        
        self.add_parameter(
            'waveform_offset',
            get_cmd=':SOUR:WAVE:OFFS?',
            set_cmd=':SOUR:WAVE:OFFS {:.9f}',
            unit='A',
            vals=vals.Numbers(-0.105, 0.105),
            docstring='Offset of the waveform in Amps'
        )
        
        self.add_parameter(
            'waveform_dutycycle',
            get_cmd=':SOUR:WAVE:DCYC?',
            set_cmd=':SOUR:WAVE:DCYC {:.3f}',
            unit='%',
            vals=vals.Numbers(0, 100),
            docstring='Duty-cycle of the waveform for square and ramp waves'
        )
        
        self.add_parameter(
            'waveform_duration_time',
            get_cmd=':SOUR:WAVE:DUR:TIME?',
            set_cmd=':SOUR:WAVE:DUR:TIME {:.6f}',
            unit='s',
            vals=vals.Numbers(100e-9, 999999.999),
            docstring='Duration of the waveform in seconds'
        )
        
        self.add_parameter(
            'waveform_duration_cycles',
            get_cmd=':SOUR:WAVE:DUR:CYCL?',
            set_cmd=':SOUR:WAVE:DUR:CYCL {:.6f}',
            vals=vals.Numbers(1e-3, 99999999900),
            docstring='Duration of the waveform in cycles'
        )
        
        self.add_parameter(
            'waveform_ranging',
            get_cmd=':SOUR:WAVE:RANG?',
            set_cmd=':SOUR:WAVE:RANG {}',
            val_mapping={'best': 'BEST', 'fixed': 'FIX'},
            docstring='Source ranging of the waveform'
        )
        
        # STATUS BIT PARAMETERS
        self.add_parameter(
            'measurement_event_enabled',
            get_cmd=':STAT:MEAS:ENAB?',
            set_cmd=':STAT:MEAS:ENAB {}',
            vals=vals.Ints(0, 65535),
            docstring='Measurement events registered in MSB status bit'
        )
        
        self.add_parameter(
            'operation_event_enabled', 
            get_cmd=':STAT:OPER:ENAB?',
            set_cmd=':STAT:OPER:ENAB {}',
            vals=vals.Ints(0, 65535),
            docstring='Operation events registered in OSB status bit'
        )
        
        self.add_parameter(
            'questionable_event_enabled',
            get_cmd=':STAT:QUES:ENAB?',
            set_cmd=':STAT:QUES:ENAB {}', 
            vals=vals.Ints(0, 65535),
            docstring='Questionable events registered in QSB status bit'
        )
        
        self.add_parameter(
            'srq_event_enabled',
            get_cmd='*SRE?',
            set_cmd='*SRE {}',
            vals=vals.Ints(0, 255),
            docstring='Event registers that trigger SRQ status bit'
        )
        
        # DISPLAY PARAMETER
        self.add_parameter(
            'display_enabled',
            get_cmd=':DISP:ENAB?',
            set_cmd=':DISP:ENAB {}',
            val_mapping={True: 1, False: 0},
            docstring='Whether the display is enabled'
        )
        
        self.connect_message()
    
    # DELTA MODE METHODS
    def delta_arm(self) -> None:
        """Arm delta mode."""
        self.write(':SOUR:DELT:ARM')
        
    def delta_start(self) -> None:
        """Start delta measurements."""
        self.write(':INIT:IMM')
        
    def delta_abort(self) -> None:
        """Stop delta and place the Model 2182A in local mode."""
        self.write(':SOUR:SWE:ABOR')
    
    def delta_sense(self) -> float:
        """Get the latest delta reading results from 2182/2182A."""
        return float(self.ask(':SENS:DATA?'))
        
    def delta_values(self) -> List[float]:
        """Get delta sense readings stored in 6221 buffer."""
        response = self.ask(':TRAC:DATA?')
        return [float(x) for x in response.split(',')]
        
    def delta_connected(self) -> bool:
        """Get connection status to 2182A."""
        return bool(int(self.ask(':SOUR:DELT:NVPR?')))
    
    # WAVEFORM METHODS  
    def waveform_arm(self) -> None:
        """Arm the current waveform function."""
        self.write(':SOUR:WAVE:ARM')
        
    def waveform_start(self) -> None:
        """Start the waveform output. Must already be armed."""
        self.write(':SOUR:WAVE:INIT')
        
    def waveform_abort(self) -> None:
        """Abort the waveform output and disarm the waveform function."""
        self.write(':SOUR:WAVE:ABOR')
        
    def waveform_duration_set_infinity(self) -> None:
        """Set the waveform duration to infinity."""
        self.write(':SOUR:WAVE:DUR:TIME INF')
        
    def define_arbitrary_waveform(self, datapoints: Union[List[float], np.ndarray], 
                                 location: int = 1) -> None:
        """
        Define the data points for arbitrary waveform and copy to storage location.
        
        Args:
            datapoints: List or numpy array of data points; all values between -1 and 1;
                       100 points maximum
            location: Integer storage location (1-4) to store the waveform
        """
        # Validate parameters
        if not isinstance(datapoints, (list, np.ndarray)):
            raise ValueError("datapoints must be a list or numpy array")
        elif len(datapoints) > 100:
            raise ValueError("datapoints cannot be longer than 100 points")
        elif not all([x >= -1 and x <= 1 for x in datapoints]):
            raise ValueError("all data points must be between -1 and 1")
            
        if location not in [1, 2, 3, 4]:
            raise ValueError("location must be in [1, 2, 3, 4]")
            
        # Convert to strings and create comma-separated data
        datapoints_str = [str(x) for x in datapoints]
        data = ", ".join(datapoints_str)
        
        # Write the data points and copy to specified location
        self.write(f':SOUR:WAVE:ARB:DATA {data}')
        self.write(f':SOUR:WAVE:ARB:COPY {location}')
        
        # Select the newly made arbitrary waveform as waveform function
        self.waveform_function(f'arbitrary{location}')
        
    # TRIGGER METHODS
    def trigger(self) -> None:
        """Execute a bus trigger."""
        self.write('*TRG')
        
    def trigger_immediately(self) -> None:
        """Configure measurements with internal trigger at maximum sampling rate."""
        self.write(':ARM:SOUR IMM;:TRIG:SOUR IMM;')
        
    def trigger_on_bus(self) -> None:
        """Configure trigger to detect events based on bus trigger."""
        self.write(':ARM:SOUR BUS;:TRIG:SOUR BUS;')
        
    def set_timed_arm(self, interval: float) -> None:
        """
        Set up measurement with internal trigger at variable sampling rate.
        
        Args:
            interval: Interval in seconds between sampling points (0.001 to 99999.99)
        """
        if interval > 99999.99 or interval < 0.001:
            raise ValueError("Keithley 6221 can only be time triggered between 1 mS and 1 Ms")
        self.write(f':ARM:SOUR TIM;:ARM:TIM {interval:.3f}')
        
    def trigger_on_external(self, line: int = 1) -> None:
        """
        Configure measurement trigger from specific line of external trigger.
        
        Args:
            line: Trigger line from 1 to 4
        """
        if line not in [1, 2, 3, 4]:
            raise ValueError("line must be between 1 and 4")
        cmd = f':ARM:SOUR TLIN;:TRIG:SOUR TLIN;:ARM:ILIN {line};:TRIG:ILIN {line};'
        self.write(cmd)
        
    def output_trigger_on_external(self, line: int = 1, after: str = 'DEL') -> None:
        """
        Configure output trigger on specified trigger link line.
        
        Args:
            line: Trigger line from 1 to 4
            after: Event string that determines when to trigger (default 'DEL')
        """
        if line not in [1, 2, 3, 4]:
            raise ValueError("line must be between 1 and 4")
        self.write(f':TRIG:OUTP {after};:TRIG:OLIN {line};')
        
    def disable_output_trigger(self) -> None:
        """Disable the output trigger for the Trigger layer."""
        self.write(':TRIG:OUTP NONE')
        
    # UTILITY METHODS
    def enable_source(self) -> None:
        """Enable the current source output."""
        self.write('OUTPUT ON')
        
    def disable_source(self) -> None:
        """Disable the current source output."""
        self.write('OUTPUT OFF')
        
    def beep(self, frequency: float, duration: float) -> None:
        """
        Sound a system beep.
        
        Args:
            frequency: Frequency in Hz between 65 Hz and 2 MHz
            duration: Time in seconds between 0 and 7.9 seconds
        """
        if not (65 <= frequency <= 2e6):
            raise ValueError("frequency must be between 65 Hz and 2 MHz")
        if not (0 <= duration <= 7.9):
            raise ValueError("duration must be between 0 and 7.9 seconds")
        self.write(f':SYST:BEEP {frequency:g}, {duration:g}')
        
    def triad(self, base_frequency: float, duration: float) -> None:
        """
        Sound a musical triad using the system beep.
        
        Args:
            base_frequency: Frequency in Hz between 65 Hz and 1.3 MHz
            duration: Time in seconds between 0 and 7.9 seconds
        """
        if not (65 <= base_frequency <= 1.3e6):
            raise ValueError("base_frequency must be between 65 Hz and 1.3 MHz")
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency * 5.0 / 4.0, duration) 
        time.sleep(duration)
        self.beep(base_frequency * 6.0 / 4.0, duration)
        
    def reset(self) -> None:
        """Reset instrument to default state and clear queue."""
        self.write('status:queue:clear;*RST;:stat:pres;:*CLS;')
        
    def configure_delta_mode(self, high_current: float, low_current: float, 
                           delta_delay: float = 0.001) -> None:
        """
        Configure delta mode for differential measurements (backward compatibility).
        
        Args:
            high_current: High current level in A
            low_current: Low current level in A  
            delta_delay: Delay between current levels in seconds
        """
        warnings.warn("configure_delta_mode is deprecated. Use delta_* parameters instead.", 
                     DeprecationWarning, stacklevel=2)
        self.delta_high_source(high_current)
        self.delta_low_source(low_current) 
        self.delta_delay(delta_delay)
        self.write('SOUR:DELT:STAT ON')
        
    def shutdown(self) -> None:
        """Disable output and shutdown."""
        self.disable_source()
        super().shutdown()


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


class Keithley2182AChannel:
    """
    Channel implementation for Keithley 2182A.
    
    Channel 1 is the fundamental measurement channel, while channel 2 provides
    sense measurements. Channel 2 inputs are referenced to Channel 1 LO.
    
    Args:
        parent: Parent Keithley2182A instrument
        channel: Channel number (1 or 2)
    """
    
    def __init__(self, parent: 'Keithley2182A', channel: int):
        self.parent = parent
        self.channel = channel
        
        # Set voltage range limits based on channel
        if channel == 1:
            self.voltage_range_limits = (0, 120)
            self.voltage_offset_limits = (-120, 120)
        else:
            self.voltage_range_limits = (0, 12)
            self.voltage_offset_limits = (-12, 12)
            
    def voltage_range(self, value: Optional[float] = None) -> Optional[float]:
        """Control the positive full-scale measurement voltage range."""
        if value is not None:
            if not (self.voltage_range_limits[0] <= value <= self.voltage_range_limits[1]):
                raise ValueError(f"Voltage range must be between {self.voltage_range_limits[0]} and {self.voltage_range_limits[1]} V")
            self.parent.write(f':SENS:VOLT:CHAN{self.channel}:RANG {value:.6f}')
        else:
            return float(self.parent.ask(f':SENS:VOLT:CHAN{self.channel}:RANG?'))
            
    def voltage_range_auto_enabled(self, value: Optional[bool] = None) -> Optional[bool]:
        """Control the auto voltage ranging option."""
        if value is not None:
            self.parent.write(f':SENS:VOLT:CHAN{self.channel}:RANG:AUTO {1 if value else 0}')
        else:
            return bool(int(self.parent.ask(f':SENS:VOLT:CHAN{self.channel}:RANG:AUTO?')))
            
    def voltage_offset(self, value: Optional[float] = None) -> Optional[float]:
        """Control the relative offset for measuring voltage."""
        if value is not None:
            if not (self.voltage_offset_limits[0] <= value <= self.voltage_offset_limits[1]):
                raise ValueError(f"Voltage offset must be between {self.voltage_offset_limits[0]} and {self.voltage_offset_limits[1]} V")
            self.parent.write(f':SENS:VOLT:CHAN{self.channel}:REF {value:.6f}')
        else:
            return float(self.parent.ask(f':SENS:VOLT:CHAN{self.channel}:REF?'))
            
    def voltage_offset_enabled(self, value: Optional[bool] = None) -> Optional[bool]:
        """Control whether voltage is measured as relative or absolute value."""
        if value is not None:
            self.parent.write(f':SENS:VOLT:CHAN{self.channel}:REF:STAT {1 if value else 0}')
        else:
            return bool(int(self.parent.ask(f':SENS:VOLT:CHAN{self.channel}:REF:STAT?')))
            
    def temperature_offset(self, value: Optional[float] = None) -> Optional[float]:
        """Control the relative offset for measuring temperature."""
        if value is not None:
            if not (-273 <= value <= 1800):
                raise ValueError("Temperature offset must be between -273 and 1800 C")
            self.parent.write(f':SENS:TEMP:CHAN{self.channel}:REF {value:.6f}')
        else:
            return float(self.parent.ask(f':SENS:TEMP:CHAN{self.channel}:REF?'))
            
    def temperature_offset_enabled(self, value: Optional[bool] = None) -> Optional[bool]:
        """Control whether temperature is measured as relative or absolute value."""
        if value is not None:
            self.parent.write(f':SENS:TEMP:CHAN{self.channel}:REF:STAT {1 if value else 0}')
        else:
            return bool(int(self.parent.ask(f':SENS:TEMP:CHAN{self.channel}:REF:STAT?')))
            
    def setup_voltage(self, auto_range: bool = True, nplc: float = 5) -> None:
        """
        Set active channel and configure for voltage measurement.
        
        Args:
            auto_range: Enable auto_range if True, else use set voltage range
            nplc: Number of power line cycles (NPLC) from 0.01 to 50/60
        """
        self.parent.write(f':SENS:CHAN {self.channel};'
                         f':SENS:FUNC "VOLT";'
                         f':SENS:VOLT:NPLC {nplc};')
        if auto_range:
            self.parent.write(':SENS:VOLT:RANG:AUTO 1')
            
    def setup_temperature(self, nplc: float = 5) -> None:
        """
        Change active channel and configure for temperature measurement.
        
        Args:
            nplc: Number of power line cycles (NPLC) from 0.01 to 50/60
        """
        self.parent.write(f':SENS:CHAN {self.channel};'
                         f':SENS:FUNC "TEMP";'
                         f':SENS:TEMP:NPLC {nplc}')
                         
    def acquire_temperature_reference(self) -> None:
        """Acquire temperature measurement and store as relative offset value."""
        self.parent.write(f':SENS:TEMP:CHAN{self.channel}:REF:ACQ')
        
    def acquire_voltage_reference(self) -> None:
        """Acquire voltage measurement and store as relative offset value."""
        self.parent.write(f':SENS:VOLT:CHAN{self.channel}:REF:ACQ')


# ENHANCED Keithley2182A with enhanced functionality while maintaining backward compatibility
class Keithley2182AEnhanced(VisaInstrument):
    """
    Enhanced QCoDeS driver for Keithley 2182A Nanovoltmeter.
    
    Enhanced driver providing high precision voltage and temperature measurements 
    for low-resistance and low-voltage applications, with support for dual channels,
    statistics, and advanced measurement capabilities.

    Args:
        name: Name of the instrument
        address: VISA resource address
        **kwargs: Additional arguments passed to VisaInstrument
    """
    
    def __init__(self, name: str, address: str, **kwargs):
        """Initialize enhanced Keithley 2182A nanovoltmeter."""
        super().__init__(name, address, terminator='\r', **kwargs)
        
        # Create channel objects
        self.ch_1 = Keithley2182AChannel(self, 1)
        self.ch_2 = Keithley2182AChannel(self, 2)
        
        # CONFIGURATION PARAMETERS
        self.add_parameter(
            'auto_zero_enabled',
            get_cmd=':SYST:AZER:STAT?',
            set_cmd=':SYST:AZER:STAT {}',
            val_mapping={True: 1, False: 0},
            docstring='Control the auto zero option'
        )
        
        self.add_parameter(
            'display_enabled',
            get_cmd=':DISP:ENAB?',
            set_cmd=':DISP:ENAB {}',
            val_mapping={True: 1, False: 0},
            docstring='Control whether the front display is enabled'
        )
        
        self.add_parameter(
            'active_channel',
            get_cmd=':SENS:CHAN?',
            set_cmd=':SENS:CHAN {}',
            vals=vals.Ints(0, 2),
            docstring='Control which channel is active for measurement (0=internal, 1, 2)'
        )
        
        # Backward compatibility alias
        self.add_parameter(
            'channel',
            get_cmd='SENS:CHAN?',
            set_cmd='SENS:CHAN {}',
            vals=vals.Ints(1, 2),
            docstring='Input channel selection (backward compatibility)'
        )
        
        self.add_parameter(
            'channel_function',
            get_cmd=':SENS:FUNC?',
            set_cmd=':SENS:FUNC {}',
            val_mapping={'voltage': '"VOLT:DC"', 'temperature': '"TEMP"'},
            docstring='Measurement mode of the active channel'
        )
        
        # VOLTAGE PARAMETERS
        self.add_parameter(
            'voltage',
            get_cmd=':READ?',
            unit='V',
            docstring='Measure voltage if active channel is configured for this reading'
        )
        
        self.add_parameter(
            'voltage_nplc',
            get_cmd=':SENS:VOLT:NPLC?',
            set_cmd=':SENS:VOLT:NPLC {:.3f}',
            vals=vals.Numbers(0.01, 60),
            docstring='Number of power line cycles (NPLC) for voltage measurements'
        )
        
        # Backward compatibility aliases
        self.add_parameter(
            'nplc',
            get_cmd='SENS:VOLT:NPLC?',
            set_cmd='SENS:VOLT:NPLC {:.3f}',
            vals=vals.Numbers(0.01, 50),
            docstring='Integration time in number of power line cycles (backward compatibility)'
        )
        
        self.add_parameter(
            'voltage_range',
            get_cmd='SENS:VOLT:RANG?',
            set_cmd='SENS:VOLT:RANG {:.6f}',
            unit='V',
            vals=vals.Numbers(10e-9, 100),
            docstring='Voltage measurement range (backward compatibility)'
        )
        
        self.add_parameter(
            'auto_range',
            get_cmd='SENS:VOLT:RANG:AUTO?',
            set_cmd='SENS:VOLT:RANG:AUTO {}',
            val_mapping={'ON': 1, 'OFF': 0},
            docstring='Auto range state (backward compatibility)'
        )
        
        # TEMPERATURE PARAMETERS
        self.add_parameter(
            'temperature',
            get_cmd=':READ?',
            unit='C',
            docstring='Measure temperature if active channel is configured for this reading'
        )
        
        self.add_parameter(
            'thermocouple',
            get_cmd=':SENS:TEMP:TC?',
            set_cmd=':SENS:TEMP:TC {}',
            vals=vals.Enum('B', 'E', 'J', 'K', 'N', 'R', 'S', 'T'),
            docstring='Thermocouple type for temperature measurements'
        )
        
        self.add_parameter(
            'temperature_nplc',
            get_cmd=':SENS:TEMP:NPLC?',
            set_cmd=':SENS:TEMP:NPLC {:.3f}',
            vals=vals.Numbers(0.01, 60),
            docstring='Number of power line cycles (NPLC) for temperature measurements'
        )
        
        self.add_parameter(
            'temperature_reference_junction',
            get_cmd=':SENS:TEMP:RJUN:RSEL?',
            set_cmd=':SENS:TEMP:RJUN:RSEL {}',
            vals=vals.Enum('SIM', 'INT'),
            docstring='Whether thermocouple reference junction is internal or simulated'
        )
        
        self.add_parameter(
            'temperature_simulated_reference',
            get_cmd=':SENS:TEMP:RJUN:SIM?',
            set_cmd=':SENS:TEMP:RJUN:SIM {:.3f}',
            unit='C',
            vals=vals.Numbers(0, 60),
            docstring='Value of simulated thermocouple reference junction'
        )
        
        # TRIGGER PARAMETERS
        self.add_parameter(
            'trigger_count',
            get_cmd=':TRIG:COUN?',
            set_cmd=':TRIG:COUN {}',
            vals=vals.Ints(1, 9999),
            docstring='Trigger count'
        )
        
        self.add_parameter(
            'trigger_delay',
            get_cmd=':TRIG:DEL?',
            set_cmd=':TRIG:DEL {:.6f}',
            unit='s',
            vals=vals.Numbers(0, 999999.999),
            docstring='Trigger delay in seconds'
        )
        
        self.connect_message()
        
    # MEASUREMENT METHODS
    def line_frequency(self) -> float:
        """Get the line frequency in Hertz (50 or 60 Hz)."""
        return float(self.ask(':SYST:LFR?'))
        
    def internal_temperature(self) -> float:
        """Measure the internal temperature in Celsius."""
        return float(self.ask(':SENS:TEMP:RTEM?'))
        
    # STATISTICS METHODS  
    def mean(self) -> float:
        """Get calculated mean (average) from buffer data."""
        return float(self.ask(':CALC2:FORM MEAN;:CALC2:STAT ON;:CALC2:IMM?;'))
        
    def maximum(self) -> float:
        """Get calculated maximum from buffer data.""" 
        return float(self.ask(':CALC2:FORM MAX;:CALC2:STAT ON;:CALC2:IMM?;'))
        
    def minimum(self) -> float:
        """Get calculated minimum from buffer data."""
        return float(self.ask(':CALC2:FORM MIN;:CALC2:STAT ON;:CALC2:IMM?;'))
        
    def standard_dev(self) -> float:
        """Get calculated standard deviation from buffer data."""
        return float(self.ask(':CALC2:FORM SDEV;:CALC2:STAT ON;:CALC2:IMM?;'))
        
    # TRIGGER METHODS
    def trigger(self) -> None:
        """Execute a bus trigger."""
        self.write('*TRG')
        
    def trigger_immediately(self) -> None:
        """Configure measurements with internal trigger at maximum sampling rate."""
        self.write(':TRIG:SOUR IMM;')
        
    def trigger_on_bus(self) -> None:
        """Configure trigger to detect events based on bus trigger."""
        self.write(':TRIG:SOUR BUS')
        
    def sample_continuously(self) -> None:
        """Configure instrument to continuously read samples."""
        # This method would need buffer management which isn't fully implemented
        warnings.warn("sample_continuously requires buffer management - not fully implemented", 
                     UserWarning, stacklevel=2)
        self.trigger_immediately()
        
    def auto_line_frequency(self) -> None:
        """Set appropriate limits for NPLC voltage and temperature readings."""
        freq = self.line_frequency()
        max_nplc = 50 if freq == 50 else 60
        
        # Update validator limits dynamically 
        # (This is a simplified approach - in a full implementation, 
        # we would update the parameter validators)
        self._max_nplc = max_nplc
        
    def reset(self) -> None:
        """Reset the instrument and clear the queue."""
        self.write('status:queue:clear;*RST;:stat:pres;:*CLS;')
        
    def configure_delta_mode(self) -> None:
        """Configure for delta mode measurements with K6221 (backward compatibility)."""
        warnings.warn("configure_delta_mode is deprecated. Use manual SCPI commands if needed.", 
                     DeprecationWarning, stacklevel=2)
        self.write('SENS:VOLT:DFIL:STAT ON')  # Enable delta filter
        self.write('SENS:VOLT:LPAS:STAT OFF') # Disable low pass filter
        
    def take_measurement(self, average_count: int = 1) -> float:
        """
        Take voltage measurement with optional averaging (backward compatibility).
        
        Args:
            average_count: Number of measurements to average
            
        Returns:
            Averaged voltage measurement
        """
        if average_count == 1:
            return float(self.ask('read?'))
        
        measurements = []
        for _ in range(average_count):
            measurements.append(float(self.ask('read?')))
            
        return sum(measurements) / len(measurements)

    
# Alias enhanced version to the original name for backward compatibility 
# (This will replace the original implementation)
Keithley2182A = Keithley2182AEnhanced


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