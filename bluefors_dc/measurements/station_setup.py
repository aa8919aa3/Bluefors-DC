"""
Station Setup for Bluefors DC Measurement System

Provides QCoDeS Station configuration for the complete measurement setup
including all instruments and their typical connections.
"""

from typing import Dict, Optional, Any
from qcodes import Station
import numpy as np

from ..instruments import (
    AMI430MagnetController,
    Keithley6221, 
    Keithley2182A,
    Keithley2636B,
    ZurichMFLI,
    Lakeshore372
)


class BlueforsStation(Station):
    """
    QCoDeS Station for Bluefors LD-400 measurement system.
    
    Configures and manages all instruments in the measurement setup
    with standard naming conventions and typical parameter settings.
    """
    
    def __init__(self, config_file: str = None, **kwargs):
        """
        Initialize Bluefors measurement station.
        
        Args:
            config_file: Optional configuration file path
            **kwargs: Additional Station arguments
        """
        super().__init__(**kwargs)
        
        # Store instrument instances
        self.magnet: Optional[AMI430MagnetController] = None
        self.current_source: Optional[Keithley6221] = None
        self.nanovoltmeter: Optional[Keithley2182A] = None
        self.smu_dual: Optional[Keithley2636B] = None
        self.lockin: Optional[ZurichMFLI] = None
        self.temperature_controller: Optional[Lakeshore372] = None
        
        # Load configuration if provided
        if config_file:
            self.load_config(config_file)
            
    def add_magnet_controller(self, address: str, name: str = 'magnet',
                             field_limit: float = 9.0, **kwargs) -> AMI430MagnetController:
        """
        Add AMI430 magnet controller to station.
        
        Args:
            address: VISA address
            name: Instrument name in station
            field_limit: Maximum field magnitude in Tesla
            **kwargs: Additional instrument parameters
            
        Returns:
            Configured magnet controller instance
        """
        self.magnet = AMI430MagnetController(name, address, **kwargs)
        self.magnet.field_limit = field_limit
        self.add_component(self.magnet)
        
        # Set safe default ramp rates (0.1 T/min)
        self.magnet.ramp_rate_x(0.1)
        self.magnet.ramp_rate_y(0.1)
        
        return self.magnet
        
    def add_current_source(self, address: str, name: str = 'current_source',
                          **kwargs) -> Keithley6221:
        """
        Add Keithley 6221 current source to station.
        
        Args:
            address: VISA address
            name: Instrument name in station
            **kwargs: Additional instrument parameters
            
        Returns:
            Configured current source instance
        """
        self.current_source = Keithley6221(name, address, **kwargs)
        self.add_component(self.current_source)
        
        # Set safe defaults
        self.current_source.current(0.0)
        self.current_source.compliance_voltage(10.0)
        self.current_source.output('OFF')
        
        return self.current_source
        
    def add_nanovoltmeter(self, address: str, name: str = 'nanovoltmeter',
                         **kwargs) -> Keithley2182A:
        """
        Add Keithley 2182A nanovoltmeter to station.
        
        Args:
            address: VISA address  
            name: Instrument name in station
            **kwargs: Additional instrument parameters
            
        Returns:
            Configured nanovoltmeter instance
        """
        self.nanovoltmeter = Keithley2182A(name, address, **kwargs)
        self.add_component(self.nanovoltmeter)
        
        # Set typical measurement parameters
        self.nanovoltmeter.nplc(1.0)  # 1 PLC integration time
        self.nanovoltmeter.auto_range('ON')
        
        return self.nanovoltmeter
        
    def add_dual_smu(self, address: str, name: str = 'smu_dual',
                     **kwargs) -> Keithley2636B:
        """
        Add Keithley 2636B dual SMU to station.
        
        Args:
            address: VISA address
            name: Instrument name in station
            **kwargs: Additional instrument parameters
            
        Returns:
            Configured dual SMU instance
        """
        self.smu_dual = Keithley2636B(name, address, **kwargs)
        self.add_component(self.smu_dual)
        
        # Set safe defaults
        self.smu_dual.voltage_a(0.0)
        self.smu_dual.voltage_b(0.0)
        self.smu_dual.output_a(False)
        self.smu_dual.output_b(False)
        
        return self.smu_dual
        
    def add_lock_in(self, device_id: str, name: str = 'lockin',
                   **kwargs) -> ZurichMFLI:
        """
        Add Zurich MFLI lock-in amplifier to station.
        
        Args:
            device_id: Device ID for Zurich instrument
            name: Instrument name in station
            **kwargs: Additional instrument parameters
            
        Returns:
            Configured lock-in amplifier instance
        """
        self.lockin = ZurichMFLI(name, device_id, **kwargs)
        self.add_component(self.lockin)
        
        # Set typical AC measurement parameters
        self.lockin.frequency(1000.0)  # 1 kHz
        self.lockin.amplitude(0.01)    # 10 mV
        self.lockin.time_constant(0.1) # 100 ms
        
        return self.lockin
        
    def add_temperature_controller(self, address: str, name: str = 'temperature',
                                  **kwargs) -> Lakeshore372:
        """
        Add Lakeshore 372 temperature controller to station.
        
        Args:
            address: VISA address
            name: Instrument name in station
            **kwargs: Additional instrument parameters
            
        Returns:
            Configured temperature controller instance
        """
        self.temperature_controller = Lakeshore372(name, address, **kwargs)
        self.add_component(self.temperature_controller)
        
        # Configure control loops with safe defaults
        self.temperature_controller.configure_control_loop(
            loop=1, input_channel=1, units='K', powerup_enable=False
        )
        
        return self.temperature_controller
        
    def setup_dc_transport_measurement(self) -> Dict[str, Any]:
        """
        Configure station for DC transport measurements.
        
        Sets up current source + nanovoltmeter configuration for
        high-precision resistance measurements.
        
        Returns:
            Dictionary with configured measurement parameters
        """
        if not (self.current_source and self.nanovoltmeter):
            raise RuntimeError("Current source and nanovoltmeter required for DC transport")
            
        # Configure current source for delta mode
        self.current_source.configure_delta_mode(1e-6, -1e-6, 0.001)
        
        # Configure nanovoltmeter for delta measurements
        self.nanovoltmeter.configure_delta_mode()
        self.nanovoltmeter.nplc(1.0)
        
        return {
            'measurement_type': 'dc_transport',
            'current_range': 1e-6,
            'voltage_range': 'auto',
            'integration_time': 1.0
        }
        
    def setup_ac_transport_measurement(self, frequency: float = 1000.0,
                                     amplitude: float = 0.01) -> Dict[str, Any]:
        """
        Configure station for AC transport measurements.
        
        Args:
            frequency: AC excitation frequency in Hz
            amplitude: AC excitation amplitude in V
            
        Returns:
            Dictionary with configured measurement parameters
        """
        if not self.lockin:
            raise RuntimeError("Lock-in amplifier required for AC transport")
            
        # Configure lock-in for AC measurements
        self.lockin.frequency(frequency)
        self.lockin.amplitude(amplitude)
        self.lockin.time_constant(0.1)
        
        # Configure for harmonic measurements if needed
        self.lockin.configure_harmonic_measurement([1, 2, 3])
        
        return {
            'measurement_type': 'ac_transport',
            'frequency': frequency,
            'amplitude': amplitude,
            'time_constant': 0.1
        }
        
    def setup_differential_measurement(self, dc_bias_range: tuple = (-0.01, 0.01),
                                     ac_amplitude: float = 0.001) -> Dict[str, Any]:
        """
        Configure station for differential conductance measurements.
        
        Args:
            dc_bias_range: DC bias voltage range (min, max) in V
            ac_amplitude: AC modulation amplitude in V
            
        Returns:
            Dictionary with configured measurement parameters
        """
        if not (self.smu_dual and self.lockin):
            raise RuntimeError("SMU and lock-in required for differential measurements")
            
        # Configure SMU for DC bias
        self.smu_dual.configure_voltage_source('a')
        self.smu_dual.set_compliance('a', current_limit=1e-6)
        
        # Configure lock-in for AC modulation measurement
        self.lockin.amplitude(ac_amplitude)
        self.lockin.frequency(1000.0)
        self.lockin.time_constant(0.03)
        
        return {
            'measurement_type': 'differential_conductance',
            'dc_range': dc_bias_range,
            'ac_amplitude': ac_amplitude,
            'frequency': 1000.0
        }
        
    def set_magnetic_field(self, field_x: float, field_y: float,
                          wait_for_completion: bool = True) -> None:
        """
        Set magnetic field vector and optionally wait for completion.
        
        Args:
            field_x: X-axis field in Tesla
            field_y: Y-axis field in Tesla
            wait_for_completion: Whether to wait for ramp completion
        """
        if not self.magnet:
            raise RuntimeError("Magnet controller not configured")
            
        self.magnet.set_field_vector(field_x, field_y, wait_for_completion)
        
    def set_temperature(self, temperature: float, loop: int = 1,
                       wait_for_stability: bool = True) -> None:
        """
        Set temperature setpoint and optionally wait for stability.
        
        Args:
            temperature: Target temperature in K
            loop: Control loop number (1 or 2)
            wait_for_stability: Whether to wait for temperature stability
        """
        if not self.temperature_controller:
            raise RuntimeError("Temperature controller not configured")
            
        # Set temperature setpoint
        setattr(self.temperature_controller, f'setpoint_{loop}', temperature)
        
        if wait_for_stability:
            self.temperature_controller.wait_for_temperature(
                loop, temperature, tolerance=0.01, timeout=3600
            )
            
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current status of all instruments in the station.
        
        Returns:
            Dictionary with system status information
        """
        status = {}
        
        if self.magnet:
            status['magnetic_field'] = {
                'field_x': self.magnet.field_x(),
                'field_y': self.magnet.field_y(),
                'magnitude': self.magnet.field_magnitude(),
                'angle': self.magnet.field_angle(),
                'status': self.magnet.magnet_status()
            }
            
        if self.temperature_controller:
            status['temperature'] = {
                'mixing_chamber': self.temperature_controller.mixing_chamber_temp(),
                'still': self.temperature_controller.still_temp(),
                'cold_plate': self.temperature_controller.cold_plate_temp(),
                'magnet': self.temperature_controller.magnet_temp()
            }
            
        if self.current_source:
            status['current_source'] = {
                'current': self.current_source.current(),
                'output': self.current_source.output(),
                'compliance': self.current_source.compliance_voltage()
            }
            
        if self.nanovoltmeter:
            status['nanovoltmeter'] = {
                'voltage': self.nanovoltmeter.voltage(),
                'range': self.nanovoltmeter.voltage_range(),
                'nplc': self.nanovoltmeter.nplc()
            }
            
        return status
        
    def emergency_stop(self) -> None:
        """Emergency stop all instruments."""
        if self.magnet:
            self.magnet.emergency_stop()
            
        if self.current_source:
            self.current_source.output('OFF')
            self.current_source.current(0.0)
            
        if self.smu_dual:
            self.smu_dual.output_a(False)
            self.smu_dual.output_b(False)
            self.smu_dual.voltage_a(0.0)
            self.smu_dual.voltage_b(0.0)
            
        if self.lockin:
            self.lockin.amplitude(0.0)
            
    def close_all_instruments(self) -> None:
        """Safely close all instrument connections."""
        for component in self.components.values():
            try:
                if hasattr(component, 'close'):
                    component.close()
            except Exception as e:
                print(f"Error closing {component.name}: {e}")
                
    def load_config(self, config_file: str) -> None:
        """
        Load instrument configuration from file.
        
        Args:
            config_file: Path to configuration file
        """
        # Placeholder for configuration loading
        # Would implement JSON/YAML config file parsing
        pass