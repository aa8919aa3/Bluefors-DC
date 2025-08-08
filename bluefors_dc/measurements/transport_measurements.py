"""
Transport Measurements

Implements transport measurement protocols equivalent to LabVIEW VIs:
- RH measurements (Hall resistance)
- RT measurements (Resistance vs Temperature)
- Vector magnet sweeps
- Real-time monitoring
"""

import numpy as np
import time
from typing import List, Dict, Union, Optional, Tuple, Callable
from dataclasses import dataclass
from qcodes import Measurement
import threading
import queue

from .station_setup import BlueforsStation
from .iv_measurements import IVMeasurement


@dataclass 
class HallMeasurementParameters:
    """Parameters for Hall resistance measurements."""
    field_range: Tuple[float, float]  # (min_field, max_field) in Tesla
    field_points: int
    current_amplitude: float = 1e-6   # Current amplitude in A
    measurement_delay: float = 1.0    # Delay between field points
    bidirectional_field: bool = True  # Sweep field in both directions
    field_axis: str = 'z'            # Field axis ('x', 'y', or 'z' if available)


class HallMeasurement:
    """
    Hall resistance measurements with magnetic field sweep.
    
    Equivalent to LabVIEW VIs: RH_BF_LD-400_MFLI_PK_v4.0_measure_voltageR_fourMFLI.vi
    """
    
    def __init__(self, station: BlueforsStation):
        """
        Initialize Hall measurement.
        
        Args:
            station: Configured BlueforsStation
        """
        self.station = station
        
        if not (station.magnet and (station.current_source and station.nanovoltmeter) or station.lockin):
            raise RuntimeError("Magnet controller and measurement instruments required")
            
        self.magnet = station.magnet
        self.use_lockin = station.lockin is not None
        
        if self.use_lockin:
            self.lockin = station.lockin
            station.setup_ac_transport_measurement()
        else:
            self.current_source = station.current_source
            self.nanovoltmeter = station.nanovoltmeter
            station.setup_dc_transport_measurement()
            
    def run_hall_sweep(self, params: HallMeasurementParameters,
                      dataset_name: str = "hall_measurement") -> Dict[str, np.ndarray]:
        """
        Run Hall resistance measurement with field sweep.
        
        Args:
            params: Hall measurement parameters
            dataset_name: Dataset name
            
        Returns:
            Dictionary with Hall measurement data
        """
        # Generate field points
        field_min, field_max = params.field_range
        field_points = np.linspace(field_min, field_max, params.field_points)
        
        if params.bidirectional_field:
            reverse_points = field_points[::-1]
            field_points = np.concatenate([field_points, reverse_points])
            
        results = {
            'magnetic_field': [],
            'resistance_xx': [],
            'resistance_xy': [],  # Hall resistance
            'voltage_xx': [],
            'voltage_xy': [],
            'current': []
        }
        
        if self.use_lockin:
            # AC Hall measurement
            self.lockin.amplitude(0.01)  # 10 mV amplitude
            self.lockin.frequency(1000.0)
            results.update({
                'phase_xx': [],
                'phase_xy': []
            })
        else:
            # DC Hall measurement
            self.current_source.current(params.current_amplitude)
            self.current_source.output('ON')
            
        try:
            for field in field_points:
                print(f"Measuring at field {field:.3f} T")
                
                # Set magnetic field (assuming perpendicular field for Hall effect)
                if params.field_axis.lower() == 'x':
                    self.magnet.set_field_vector(field, 0, wait_for_completion=True)
                elif params.field_axis.lower() == 'y':
                    self.magnet.set_field_vector(0, field, wait_for_completion=True)
                else:
                    # For z-axis, need 3D magnet or set to maximum available field
                    field_magnitude = abs(field)
                    self.magnet.set_field_polar(field_magnitude, 0, wait_for_completion=True)
                    
                # Wait for field stabilization
                time.sleep(params.measurement_delay)
                
                if self.use_lockin:
                    # AC measurement - would need multiple lock-in channels for xy measurement
                    # For now, measure R_xx (longitudinal resistance)
                    self.lockin.wait_for_settling()
                    
                    # Take measurement
                    amplitude_data = self.lockin.measure_with_averaging(5)
                    voltage_x = amplitude_data['x']
                    voltage_y = amplitude_data['y']
                    voltage_r = amplitude_data['r']
                    phase = amplitude_data['phase']
                    
                    # Calculate resistance (V/I)
                    current_eff = params.current_amplitude / np.sqrt(2)  # RMS current
                    resistance = voltage_r / current_eff
                    
                    results['voltage_xx'].append(voltage_r)
                    results['voltage_xy'].append(0)  # Would need separate channel
                    results['resistance_xx'].append(resistance)
                    results['resistance_xy'].append(0)  # Would need separate measurement
                    results['phase_xx'].append(phase)
                    results['phase_xy'].append(0)
                    results['current'].append(current_eff)
                    
                else:
                    # DC measurement
                    voltage = self.nanovoltmeter.take_measurement(5)  # 5-point average
                    current = self.current_source.current()
                    resistance = voltage / current if current != 0 else np.inf
                    
                    results['voltage_xx'].append(voltage)
                    results['voltage_xy'].append(0)  # Would need separate voltage measurement
                    results['resistance_xx'].append(resistance)
                    results['resistance_xy'].append(0)  # Would need xy geometry measurement
                    results['current'].append(current)
                    
                results['magnetic_field'].append(field)
                
        finally:
            if not self.use_lockin:
                self.current_source.output('OFF')
                self.current_source.current(0.0)
                
        return {key: np.array(value) for key, value in results.items()}


class TransportMeasurement:
    """
    General transport measurements with various sweep parameters.
    
    Provides base functionality for resistance measurements vs external parameters.
    """
    
    def __init__(self, station: BlueforsStation):
        """
        Initialize transport measurement.
        
        Args:
            station: Configured BlueforsStation
        """
        self.station = station
        
        # Choose measurement method based on available instruments
        self.use_lockin = station.lockin is not None
        
        if self.use_lockin:
            self.lockin = station.lockin
        elif station.current_source and station.nanovoltmeter:
            self.current_source = station.current_source
            self.nanovoltmeter = station.nanovoltmeter
        elif station.smu_dual:
            self.smu = station.smu_dual
        else:
            raise RuntimeError("No suitable measurement instruments found")
            
    def measure_resistance(self, current_amplitude: float = 1e-6,
                         averages: int = 5) -> Tuple[float, float, float]:
        """
        Measure resistance using available instruments.
        
        Args:
            current_amplitude: Current for measurement
            averages: Number of averages
            
        Returns:
            Tuple of (resistance, voltage, current)
        """
        if self.use_lockin:
            # AC resistance measurement
            resistance = self.lockin.measure_resistance(current_amplitude / np.sqrt(2))
            voltage_data = self.lockin.measure_with_averaging(averages)
            return resistance, voltage_data['r'], current_amplitude / np.sqrt(2)
            
        elif hasattr(self, 'current_source'):
            # DC measurement with separate instruments
            voltage = self.nanovoltmeter.take_measurement(averages)
            current = self.current_source.current()
            resistance = voltage / current if current != 0 else np.inf
            return resistance, voltage, current
            
        else:
            # SMU measurement
            self.smu.current_a(current_amplitude)
            time.sleep(0.1)  # Settling time
            
            voltage_sum = 0
            current_sum = 0
            
            for _ in range(averages):
                current_meas, voltage_meas = self.smu.measure_iv('a')
                voltage_sum += voltage_meas
                current_sum += current_meas
                time.sleep(0.05)
                
            avg_voltage = voltage_sum / averages
            avg_current = current_sum / averages
            resistance = avg_voltage / avg_current if avg_current != 0 else np.inf
            
            return resistance, avg_voltage, avg_current


class TemperatureResistanceSweep:
    """
    Resistance measurements vs temperature.
    
    Equivalent to LabVIEW VI: RT_BF_LD-400_MFLI_PK_v4.0_measure_voltageR_fourMFLI.vi
    """
    
    def __init__(self, station: BlueforsStation, control_loop: int = 1):
        """
        Initialize temperature-resistance measurement.
        
        Args:
            station: Configured BlueforsStation
            control_loop: Temperature control loop number
        """
        self.station = station
        self.control_loop = control_loop
        self.transport = TransportMeasurement(station)
        
        if not station.temperature_controller:
            raise RuntimeError("Temperature controller required")
            
        self.temperature_controller = station.temperature_controller
        
    def run_temperature_sweep(self, temperature_points: np.ndarray,
                            current_amplitude: float = 1e-6,
                            settling_time: float = 300.0,
                            temperature_tolerance: float = 0.01,
                            dataset_name: str = "rt_measurement") -> Dict[str, np.ndarray]:
        """
        Run resistance vs temperature measurement.
        
        Args:
            temperature_points: Array of temperatures in K
            current_amplitude: Measurement current
            settling_time: Temperature settling time
            temperature_tolerance: Temperature stability tolerance
            dataset_name: Dataset name
            
        Returns:
            Dictionary with temperature-dependent resistance data
        """
        results = {
            'temperature_setpoint': [],
            'temperature_actual': [],
            'resistance': [],
            'voltage': [],
            'current': []
        }
        
        # Set up measurement instruments
        if hasattr(self.transport, 'current_source'):
            self.transport.current_source.current(current_amplitude)
            self.transport.current_source.output('ON')
            
        try:
            for temp_setpoint in temperature_points:
                print(f"Setting temperature to {temp_setpoint:.3f} K")
                
                # Set temperature
                setpoint_param = getattr(self.temperature_controller, f'setpoint_{self.control_loop}')
                setpoint_param(temp_setpoint)
                
                # Wait for temperature stability
                stability_achieved = self.temperature_controller.wait_for_temperature(
                    self.control_loop, temp_setpoint, 
                    tolerance=temperature_tolerance,
                    timeout=3600
                )
                
                if not stability_achieved:
                    print(f"Warning: Temperature {temp_setpoint:.3f} K not stable")
                    
                # Additional settling time
                time.sleep(settling_time)
                
                # Measure actual temperature
                temp_actual = self.temperature_controller.mixing_chamber_temp()
                
                # Measure resistance
                resistance, voltage, current = self.transport.measure_resistance(
                    current_amplitude, averages=10
                )
                
                # Store results
                results['temperature_setpoint'].append(temp_setpoint)
                results['temperature_actual'].append(temp_actual)
                results['resistance'].append(resistance)
                results['voltage'].append(voltage)
                results['current'].append(current)
                
                print(f"T = {temp_actual:.3f} K, R = {resistance:.3e} Ω")
                
        finally:
            if hasattr(self.transport, 'current_source'):
                self.transport.current_source.output('OFF')
                self.transport.current_source.current(0.0)
                
        return {key: np.array(value) for key, value in results.items()}


class RealTimeMonitoring:
    """
    Real-time monitoring of transport properties.
    
    Equivalent to LabVIEW VIs: realtime_IV_K2182A_K6221_vs_time_PK.vi
    """
    
    def __init__(self, station: BlueforsStation):
        """
        Initialize real-time monitoring.
        
        Args:
            station: Configured BlueforsStation
        """
        self.station = station
        self.transport = TransportMeasurement(station)
        
        self.monitoring = False
        self.data_queue = queue.Queue()
        self.monitor_thread = None
        
    def start_monitoring(self, current_amplitude: float = 1e-6,
                        measurement_interval: float = 1.0,
                        callback: Optional[Callable] = None) -> None:
        """
        Start real-time resistance monitoring.
        
        Args:
            current_amplitude: Measurement current
            measurement_interval: Time between measurements in seconds
            callback: Optional callback function for data processing
        """
        if self.monitoring:
            print("Monitoring already running")
            return
            
        self.monitoring = True
        
        # Configure instruments
        if hasattr(self.transport, 'current_source'):
            self.transport.current_source.current(current_amplitude)
            self.transport.current_source.output('ON')
            
        def monitor_loop():
            """Monitor loop running in separate thread."""
            start_time = time.time()
            
            while self.monitoring:
                try:
                    # Measure resistance
                    resistance, voltage, current = self.transport.measure_resistance(current_amplitude)
                    
                    # Get temperature if available
                    temperature = None
                    if self.station.temperature_controller:
                        temperature = self.station.temperature_controller.mixing_chamber_temp()
                        
                    # Get magnetic field if available  
                    field_x = field_y = None
                    if self.station.magnet:
                        field_x = self.station.magnet.field_x()
                        field_y = self.station.magnet.field_y()
                        
                    # Create data point
                    data_point = {
                        'timestamp': time.time(),
                        'elapsed_time': time.time() - start_time,
                        'resistance': resistance,
                        'voltage': voltage,
                        'current': current,
                        'temperature': temperature,
                        'field_x': field_x,
                        'field_y': field_y
                    }
                    
                    # Add to queue
                    self.data_queue.put(data_point)
                    
                    # Call callback if provided
                    if callback:
                        callback(data_point)
                        
                    # Print status
                    print(f"Time: {data_point['elapsed_time']:.1f} s, "
                          f"R: {resistance:.3e} Ω, "
                          f"T: {temperature:.3f} K" if temperature else "")
                          
                    time.sleep(measurement_interval)
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(measurement_interval)
                    
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("Real-time monitoring started")
        
    def stop_monitoring(self) -> List[Dict]:
        """
        Stop monitoring and return collected data.
        
        Returns:
            List of data points collected during monitoring
        """
        if not self.monitoring:
            print("Monitoring not running")
            return []
            
        self.monitoring = False
        
        # Wait for thread to finish
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
            
        # Clean up instruments
        if hasattr(self.transport, 'current_source'):
            self.transport.current_source.output('OFF')
            self.transport.current_source.current(0.0)
            
        # Collect all data from queue
        data_points = []
        while not self.data_queue.empty():
            try:
                data_points.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
                
        print(f"Monitoring stopped. Collected {len(data_points)} data points")
        return data_points
        
    def get_current_data(self) -> List[Dict]:
        """
        Get currently available data without stopping monitoring.
        
        Returns:
            List of data points currently in queue
        """
        data_points = []
        temp_queue = queue.Queue()
        
        # Move data from main queue to temp queue while collecting
        while not self.data_queue.empty():
            try:
                point = self.data_queue.get_nowait()
                data_points.append(point)
                temp_queue.put(point)
            except queue.Empty:
                break
                
        # Put data back in main queue
        while not temp_queue.empty():
            self.data_queue.put(temp_queue.get())
            
        return data_points