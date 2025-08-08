"""
I-V Measurement Classes

Implements current-voltage measurement protocols equivalent to LabVIEW VIs:
- I(V)_K6221-K2182a_PK.vi
- I(V)_K2636B_PK.vi  
- I(V)_MFLI_PK_v4.0_measure X.vi
- I(V) at various fields_K6221-K2182A_PK.vi
"""

import numpy as np
import time
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass
from qcodes import Measurement, Parameter

from .station_setup import BlueforsStation


@dataclass
class IVSweepParameters:
    """Parameters for I-V sweep measurements."""
    start_current: float
    stop_current: float  
    num_points: int
    delay_between_points: float = 0.1
    bidirectional: bool = True
    compliance_voltage: float = 10.0
    current_range: Optional[float] = None


class IVMeasurement:
    """
    Basic I-V measurement using Keithley 6221 current source and 2182A nanovoltmeter.
    
    Equivalent to LabVIEW VI: I(V)_K6221-K2182a_PK.vi
    """
    
    def __init__(self, station: BlueforsStation):
        """
        Initialize I-V measurement.
        
        Args:
            station: Configured BlueforsStation with required instruments
        """
        self.station = station
        
        if not (station.current_source and station.nanovoltmeter):
            raise RuntimeError("Current source and nanovoltmeter required for I-V measurement")
            
        self.current_source = station.current_source
        self.nanovoltmeter = station.nanovoltmeter
        
        # Configure for delta mode measurements
        station.setup_dc_transport_measurement()
        
    def run_sweep(self, params: IVSweepParameters, 
                  dataset_name: str = "iv_measurement") -> Dict[str, np.ndarray]:
        """
        Run I-V sweep measurement.
        
        Args:
            params: Sweep parameters
            dataset_name: Name for the dataset
            
        Returns:
            Dictionary with current and voltage arrays
        """
        # Generate current points
        current_points = np.linspace(params.start_current, params.stop_current, params.num_points)
        
        if params.bidirectional:
            # Add reverse sweep
            reverse_points = current_points[::-1]
            current_points = np.concatenate([current_points, reverse_points])
            
        # Set up measurement - simplified without QCoDeS dataset
        # In production, would use meas.run() context for proper data management
        
        # Set compliance voltage
        self.current_source.compliance_voltage(params.compliance_voltage)
        
        # Set current range if specified
        if params.current_range:
            self.current_source.current_range(params.current_range)
            
        # Enable output
        self.current_source.output('ON')
        
        currents = []
        voltages = []
        
        try:
            for current in current_points:
                # Set current
                self.current_source.current(current)
                
                # Wait for settling
                time.sleep(params.delay_between_points)
                
                # Measure voltage
                voltage = self.nanovoltmeter.voltage()
                
                currents.append(current)
                voltages.append(voltage)
                    
        finally:
            # Safely disable output
            self.current_source.current(0.0)
            self.current_source.output('OFF')
            
        return {
            'current': np.array(currents),
            'voltage': np.array(voltages),
            'resistance': np.array(voltages) / np.array(currents)
        }


class IVMeasurement2636B:
    """
    I-V measurement using Keithley 2636B dual SMU.
    
    Equivalent to LabVIEW VI: I(V)_K2636B_PK.vi
    """
    
    def __init__(self, station: BlueforsStation, channel: str = 'a'):
        """
        Initialize I-V measurement with 2636B SMU.
        
        Args:
            station: Configured BlueforsStation
            channel: SMU channel ('a' or 'b')
        """
        self.station = station
        self.channel = channel
        
        if not station.smu_dual:
            raise RuntimeError("Keithley 2636B SMU required")
            
        self.smu = station.smu_dual
        
        # Configure as current source
        self.smu.configure_current_source(channel)
        
    def run_sweep(self, params: IVSweepParameters,
                  dataset_name: str = "iv_2636b") -> Dict[str, np.ndarray]:
        """
        Run I-V sweep using SMU current sourcing.
        
        Args:
            params: Sweep parameters
            dataset_name: Dataset name
            
        Returns:
            Dictionary with measurement arrays
        """
        current_points = np.linspace(params.start_current, params.stop_current, params.num_points)
        
        if params.bidirectional:
            reverse_points = current_points[::-1]
            current_points = np.concatenate([current_points, reverse_points])
            
        # Get parameter references for this channel
        current_param = getattr(self.smu, f'current_{self.channel}')
        voltage_param = getattr(self.smu, f'voltage_{self.channel}')
        output_param = getattr(self.smu, f'output_{self.channel}')
        
        # Set compliance
        self.smu.set_compliance(self.channel, voltage_limit=params.compliance_voltage)
        
        # Set up measurement
        meas = Measurement()
        meas.register_parameter(current_param)
        meas.register_parameter(voltage_param, setpoints=(current_param,))
        
        # Enable output
        output_param(True)
        
        try:
            with meas.run() as datasaver:
                currents = []
                voltages = []
                
                for current in current_points:
                    # Set current
                    current_param(current)
                    
                    # Wait for settling
                    time.sleep(params.delay_between_points)
                    
                    # Measure voltage
                    voltage = voltage_param()
                    
                    datasaver.add_result(
                        (current_param, current),
                        (voltage_param, voltage)
                    )
                    
                    currents.append(current)
                    voltages.append(voltage)
                    
        finally:
            # Safe shutdown
            current_param(0.0)
            output_param(False)
            
        return {
            'current': np.array(currents),
            'voltage': np.array(voltages),
            'resistance': np.array(voltages) / np.array(currents)
        }


class IVFieldSweep:
    """
    I-V measurements at various magnetic fields.
    
    Equivalent to LabVIEW VI: I(V) at various fields_K6221-K2182A_PK.vi
    """
    
    def __init__(self, station: BlueforsStation):
        """
        Initialize I-V field sweep measurement.
        
        Args:
            station: Configured BlueforsStation with magnet controller
        """
        self.station = station
        self.iv_measurement = IVMeasurement(station)
        
        if not station.magnet:
            raise RuntimeError("Magnet controller required for field sweep")
            
        self.magnet = station.magnet
        
    def run_field_sweep(self, iv_params: IVSweepParameters,
                       field_points: List[Tuple[float, float]],
                       dataset_name: str = "iv_field_sweep") -> Dict[str, np.ndarray]:
        """
        Run I-V measurements at multiple field points.
        
        Args:
            iv_params: I-V sweep parameters
            field_points: List of (field_x, field_y) tuples in Tesla
            dataset_name: Dataset name
            
        Returns:
            Dictionary with field-dependent I-V data
        """
        all_data = {
            'field_x': [],
            'field_y': [],
            'field_magnitude': [],
            'field_angle': [], 
            'current_arrays': [],
            'voltage_arrays': [],
            'resistance_arrays': []
        }
        
        for field_x, field_y in field_points:
            print(f"Setting field to ({field_x:.3f}, {field_y:.3f}) T")
            
            # Set magnetic field
            self.magnet.set_field_vector(field_x, field_y, wait_for_completion=True)
            
            # Wait additional settling time
            time.sleep(2.0)
            
            # Run I-V measurement
            iv_data = self.iv_measurement.run_sweep(iv_params, 
                                                   f"{dataset_name}_field_{len(all_data['field_x'])}")
            
            # Store data
            field_mag = np.sqrt(field_x**2 + field_y**2)
            field_angle = np.degrees(np.arctan2(field_y, field_x))
            
            all_data['field_x'].append(field_x)
            all_data['field_y'].append(field_y)
            all_data['field_magnitude'].append(field_mag)
            all_data['field_angle'].append(field_angle)
            all_data['current_arrays'].append(iv_data['current'])
            all_data['voltage_arrays'].append(iv_data['voltage'])
            all_data['resistance_arrays'].append(iv_data['resistance'])
            
        return all_data
        
    def run_angle_sweep(self, iv_params: IVSweepParameters,
                       field_magnitude: float, angles_deg: np.ndarray,
                       dataset_name: str = "iv_angle_sweep") -> Dict[str, np.ndarray]:
        """
        Run I-V measurements sweeping magnetic field angle at fixed magnitude.
        
        Args:
            iv_params: I-V sweep parameters
            field_magnitude: Fixed field magnitude in Tesla
            angles_deg: Array of angles in degrees
            dataset_name: Dataset name
            
        Returns:
            Dictionary with angle-dependent I-V data
        """
        # Convert angles to field components
        field_points = []
        for angle in angles_deg:
            angle_rad = np.radians(angle)
            field_x = field_magnitude * np.cos(angle_rad)
            field_y = field_magnitude * np.sin(angle_rad)
            field_points.append((field_x, field_y))
            
        return self.run_field_sweep(iv_params, field_points, dataset_name)


class IVTemperatureSweep:
    """
    I-V measurements at various temperatures.
    
    Equivalent to LabVIEW VIs: IV(H)_2devices_DC_temperature sweep_BF_LD-400_K6221_K2182A_PK.vi
    """
    
    def __init__(self, station: BlueforsStation, control_loop: int = 1):
        """
        Initialize I-V temperature sweep measurement.
        
        Args:
            station: Configured BlueforsStation with temperature controller
            control_loop: Temperature control loop to use (1 or 2)
        """
        self.station = station
        self.control_loop = control_loop
        self.iv_measurement = IVMeasurement(station)
        
        if not station.temperature_controller:
            raise RuntimeError("Temperature controller required for temperature sweep")
            
        self.temperature_controller = station.temperature_controller
        
    def run_temperature_sweep(self, iv_params: IVSweepParameters,
                            temperature_points: np.ndarray,
                            settling_time: float = 300.0,
                            temperature_tolerance: float = 0.01,
                            dataset_name: str = "iv_temperature_sweep") -> Dict[str, np.ndarray]:
        """
        Run I-V measurements at multiple temperatures.
        
        Args:
            iv_params: I-V sweep parameters
            temperature_points: Array of temperatures in K
            settling_time: Time to wait for temperature stability (seconds)
            temperature_tolerance: Temperature stability tolerance in K
            dataset_name: Dataset name
            
        Returns:
            Dictionary with temperature-dependent I-V data
        """
        all_data = {
            'temperatures': [],
            'current_arrays': [],
            'voltage_arrays': [],
            'resistance_arrays': []
        }
        
        for temperature in temperature_points:
            print(f"Setting temperature to {temperature:.3f} K")
            
            # Set temperature setpoint
            setpoint_param = getattr(self.temperature_controller, f'setpoint_{self.control_loop}')
            setpoint_param(temperature)
            
            # Wait for temperature stability
            stability_achieved = self.temperature_controller.wait_for_temperature(
                self.control_loop, temperature, 
                tolerance=temperature_tolerance,
                timeout=3600  # 1 hour maximum wait
            )
            
            if not stability_achieved:
                print(f"Warning: Temperature {temperature:.3f} K did not stabilize within timeout")
                
            # Additional settling time
            time.sleep(settling_time)
            
            # Run I-V measurement
            iv_data = self.iv_measurement.run_sweep(iv_params,
                                                   f"{dataset_name}_temp_{len(all_data['temperatures'])}")
            
            # Store data
            all_data['temperatures'].append(temperature)
            all_data['current_arrays'].append(iv_data['current'])
            all_data['voltage_arrays'].append(iv_data['voltage'])
            all_data['resistance_arrays'].append(iv_data['resistance'])
            
        return all_data


class IVACMeasurement:
    """
    AC I-V measurement using lock-in amplifier.
    
    Equivalent to LabVIEW VI: I(V)_MFLI_PK_v4.0_measure X.vi
    """
    
    def __init__(self, station: BlueforsStation):
        """
        Initialize AC I-V measurement.
        
        Args:
            station: Configured BlueforsStation with lock-in amplifier
        """
        self.station = station
        
        if not station.lockin:
            raise RuntimeError("Lock-in amplifier required for AC measurement")
            
        self.lockin = station.lockin
        
        # Configure for AC transport measurements
        station.setup_ac_transport_measurement()
        
    def run_sweep(self, voltage_points: np.ndarray, 
                  current_amplitude: float = 1e-6,
                  delay_between_points: float = 0.2,
                  dataset_name: str = "iv_ac") -> Dict[str, np.ndarray]:
        """
        Run AC I-V sweep measurement.
        
        Args:
            voltage_points: Array of DC bias voltages
            current_amplitude: AC current amplitude in A
            delay_between_points: Delay between measurements
            dataset_name: Dataset name
            
        Returns:
            Dictionary with AC measurement data
        """
        # Set up measurement parameters
        meas = Measurement()
        
        # Use SMU for DC bias if available
        if self.station.smu_dual:
            dc_voltage_param = self.station.smu_dual.voltage_a
            meas.register_parameter(dc_voltage_param)
            meas.register_parameter(self.lockin.amplitude_x, setpoints=(dc_voltage_param,))
            meas.register_parameter(self.lockin.amplitude_y, setpoints=(dc_voltage_param,))
        else:
            # Would need external DC source
            raise RuntimeError("DC bias source required for AC I-V measurement")
            
        results = {
            'dc_voltage': [],
            'ac_voltage_x': [],
            'ac_voltage_y': [],
            'ac_voltage_r': [],
            'ac_voltage_phase': [],
            'differential_resistance': []
        }
        
        # Configure SMU for DC bias
        self.station.smu_dual.configure_voltage_source('a')
        self.station.smu_dual.set_compliance('a', current_limit=1e-6)
        self.station.smu_dual.output_a(True)
        
        try:
            with meas.run() as datasaver:
                for voltage in voltage_points:
                    # Set DC bias voltage
                    dc_voltage_param(voltage)
                    
                    # Wait for settling
                    self.lockin.wait_for_settling()
                    time.sleep(delay_between_points)
                    
                    # Measure AC response
                    x = self.lockin.amplitude_x()
                    y = self.lockin.amplitude_y()
                    r = np.sqrt(x**2 + y**2)
                    phase = np.degrees(np.arctan2(y, x))
                    
                    # Calculate differential resistance (dV/dI)
                    diff_resistance = r / current_amplitude if current_amplitude != 0 else np.inf
                    
                    # Save data
                    datasaver.add_result(
                        (dc_voltage_param, voltage),
                        (self.lockin.amplitude_x, x),
                        (self.lockin.amplitude_y, y)
                    )
                    
                    results['dc_voltage'].append(voltage)
                    results['ac_voltage_x'].append(x)
                    results['ac_voltage_y'].append(y)
                    results['ac_voltage_r'].append(r)
                    results['ac_voltage_phase'].append(phase)
                    results['differential_resistance'].append(diff_resistance)
                    
        finally:
            # Safe shutdown
            self.station.smu_dual.voltage_a(0.0)
            self.station.smu_dual.output_a(False)
            
        return {key: np.array(value) for key, value in results.items()}