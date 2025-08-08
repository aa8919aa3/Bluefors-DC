"""
Differential Conductance Measurements

Implements differential conductance (dI-dV) measurement protocols equivalent to LabVIEW VIs:
- dI-dV(V)_MFLI_MF-MD_K3636B_measureX_PK_V4.0_withaveraging.vi
- STS at various H_MFLI_MF-MD_K3636B_PK_V4.0_withaveraging.vi
- dV-dI two devices at various H_MFLI_MF-MD_K3636B_PK_V4.0_withaveraging.vi
"""

import numpy as np
import time
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass
from qcodes import Measurement

from .station_setup import BlueforsStation


@dataclass
class DifferentialParameters:
    """Parameters for differential conductance measurements."""
    start_voltage: float
    stop_voltage: float
    num_points: int
    ac_amplitude: float = 0.001  # AC modulation amplitude in V
    frequency: float = 1000.0    # Modulation frequency in Hz
    time_constant: float = 0.03  # Lock-in time constant in s
    averages: int = 5           # Number of averages per point
    delay_between_points: float = 0.1
    bidirectional: bool = True


class DifferentialConductance:
    """
    Differential conductance (dI-dV) measurements using lock-in technique.
    
    Equivalent to LabVIEW VIs: dI-dV(V)_MFLI_MF-MD_K3636B_measureX_PK_V4.0_withaveraging.vi
    """
    
    def __init__(self, station: BlueforsStation, smu_channel: str = 'a'):
        """
        Initialize differential conductance measurement.
        
        Args:
            station: Configured BlueforsStation
            smu_channel: SMU channel for DC bias ('a' or 'b')
        """
        self.station = station
        self.smu_channel = smu_channel
        
        if not (station.smu_dual and station.lockin):
            raise RuntimeError("SMU and lock-in amplifier required for differential measurements")
            
        self.smu = station.smu_dual
        self.lockin = station.lockin
        
        # Configure station for differential measurements
        station.setup_differential_measurement()
        
    def run_sweep(self, params: DifferentialParameters,
                  dataset_name: str = "differential_conductance") -> Dict[str, np.ndarray]:
        """
        Run differential conductance sweep.
        
        Args:
            params: Measurement parameters
            dataset_name: Dataset name
            
        Returns:
            Dictionary with measurement data
        """
        # Generate voltage points
        voltage_points = np.linspace(params.start_voltage, params.stop_voltage, params.num_points)
        
        if params.bidirectional:
            reverse_points = voltage_points[::-1]
            voltage_points = np.concatenate([voltage_points, reverse_points])
            
        # Configure lock-in
        self.lockin.frequency(params.frequency)
        self.lockin.amplitude(params.ac_amplitude)
        self.lockin.time_constant(params.time_constant)
        
        # Configure SMU for DC bias
        dc_voltage_param = getattr(self.smu, f'voltage_{self.smu_channel}')
        dc_current_param = getattr(self.smu, f'current_{self.smu_channel}')
        output_param = getattr(self.smu, f'output_{self.smu_channel}')
        
        self.smu.configure_voltage_source(self.smu_channel)
        self.smu.set_compliance(self.smu_channel, current_limit=1e-6)
        
        # Set up measurement
        meas = Measurement()
        meas.register_parameter(dc_voltage_param)
        meas.register_parameter(dc_current_param, setpoints=(dc_voltage_param,))
        meas.register_parameter(self.lockin.amplitude_x, setpoints=(dc_voltage_param,))
        meas.register_parameter(self.lockin.amplitude_y, setpoints=(dc_voltage_param,))
        
        results = {
            'voltage': [],
            'current': [],
            'resistance': [],
            'diff_voltage_x': [],
            'diff_voltage_y': [],
            'diff_voltage_r': [],
            'diff_voltage_phase': [],
            'diff_conductance': [],
            'diff_resistance': []
        }
        
        # Enable outputs
        output_param(True)
        
        try:
            with meas.run() as datasaver:
                for voltage in voltage_points:
                    # Set DC bias voltage
                    dc_voltage_param(voltage)
                    
                    # Wait for settling
                    time.sleep(params.delay_between_points)
                    self.lockin.wait_for_settling()
                    
                    # Take averaged measurements
                    dc_current_avg = 0
                    ac_measurements = {
                        'x': [],
                        'y': [],
                        'r': [],
                        'phase': []
                    }
                    
                    for _ in range(params.averages):
                        # DC measurements
                        dc_current_avg += dc_current_param()
                        
                        # AC measurements
                        ac_data = self.lockin.measure_with_averaging(1)
                        ac_measurements['x'].append(ac_data['x'])
                        ac_measurements['y'].append(ac_data['y'])
                        ac_measurements['r'].append(ac_data['r'])
                        ac_measurements['phase'].append(ac_data['phase'])
                        
                        time.sleep(0.05)  # Brief delay between averages
                        
                    # Calculate averages
                    dc_current_avg /= params.averages
                    ac_x_avg = np.mean(ac_measurements['x'])
                    ac_y_avg = np.mean(ac_measurements['y'])
                    ac_r_avg = np.mean(ac_measurements['r'])
                    ac_phase_avg = np.mean(ac_measurements['phase'])
                    
                    # Calculate differential conductance (dI/dV)
                    # The lock-in measures dV, we want dI/dV = (dV/R)/dV = 1/R * (dI_ac/dV_ac)
                    # For small signal: dI/dV ≈ I_ac / V_ac
                    diff_conductance = params.ac_amplitude / ac_r_avg if ac_r_avg != 0 else 0
                    diff_resistance = ac_r_avg / params.ac_amplitude if params.ac_amplitude != 0 else np.inf
                    
                    # DC resistance
                    dc_resistance = voltage / dc_current_avg if dc_current_avg != 0 else np.inf
                    
                    # Save data
                    datasaver.add_result(
                        (dc_voltage_param, voltage),
                        (dc_current_param, dc_current_avg),
                        (self.lockin.amplitude_x, ac_x_avg),
                        (self.lockin.amplitude_y, ac_y_avg)
                    )
                    
                    # Store results
                    results['voltage'].append(voltage)
                    results['current'].append(dc_current_avg)
                    results['resistance'].append(dc_resistance)
                    results['diff_voltage_x'].append(ac_x_avg)
                    results['diff_voltage_y'].append(ac_y_avg)
                    results['diff_voltage_r'].append(ac_r_avg)
                    results['diff_voltage_phase'].append(ac_phase_avg)
                    results['diff_conductance'].append(diff_conductance)
                    results['diff_resistance'].append(diff_resistance)
                    
        finally:
            # Safe shutdown
            dc_voltage_param(0.0)
            output_param(False)
            
        return {key: np.array(value) for key, value in results.items()}


class STSMeasurement:
    """
    Scanning Tunneling Spectroscopy measurements at various magnetic fields.
    
    Equivalent to LabVIEW VI: STS at various H_MFLI_MF-MD_K3636B_PK_V4.0_withaveraging.vi
    """
    
    def __init__(self, station: BlueforsStation, smu_channel: str = 'a'):
        """
        Initialize STS measurement.
        
        Args:
            station: Configured BlueforsStation
            smu_channel: SMU channel for bias voltage
        """
        self.station = station
        self.diff_measurement = DifferentialConductance(station, smu_channel)
        
        if not station.magnet:
            raise RuntimeError("Magnet controller required for field-dependent STS")
            
        self.magnet = station.magnet
        
    def run_field_sweep(self, diff_params: DifferentialParameters,
                       field_points: List[Tuple[float, float]],
                       dataset_name: str = "sts_field_sweep") -> Dict[str, np.ndarray]:
        """
        Run STS measurements at multiple field points.
        
        Args:
            diff_params: Differential measurement parameters
            field_points: List of (field_x, field_y) tuples
            dataset_name: Dataset name
            
        Returns:
            Dictionary with field-dependent STS data
        """
        all_data = {
            'field_x': [],
            'field_y': [],
            'field_magnitude': [],
            'field_angle': [],
            'voltage_arrays': [],
            'diff_conductance_arrays': [],
            'diff_resistance_arrays': []
        }
        
        for field_x, field_y in field_points:
            print(f"STS measurement at field ({field_x:.3f}, {field_y:.3f}) T")
            
            # Set magnetic field
            self.magnet.set_field_vector(field_x, field_y, wait_for_completion=True)
            
            # Additional settling time for magnetic field
            time.sleep(5.0)
            
            # Run differential conductance measurement
            sts_data = self.diff_measurement.run_sweep(
                diff_params, f"{dataset_name}_field_{len(all_data['field_x'])}"
            )
            
            # Store data
            field_mag = np.sqrt(field_x**2 + field_y**2)
            field_angle = np.degrees(np.arctan2(field_y, field_x))
            
            all_data['field_x'].append(field_x)
            all_data['field_y'].append(field_y)
            all_data['field_magnitude'].append(field_mag)
            all_data['field_angle'].append(field_angle)
            all_data['voltage_arrays'].append(sts_data['voltage'])
            all_data['diff_conductance_arrays'].append(sts_data['diff_conductance'])
            all_data['diff_resistance_arrays'].append(sts_data['diff_resistance'])
            
        return all_data


class TwoDeviceDifferential:
    """
    Differential measurements on two devices simultaneously.
    
    Equivalent to LabVIEW VI: dV-dI two devices at various H_MFLI_MF-MD_K3636B_PK_V4.0_withaveraging.vi
    """
    
    def __init__(self, station: BlueforsStation):
        """
        Initialize two-device differential measurement.
        
        Args:
            station: Configured BlueforsStation with dual SMU
        """
        self.station = station
        
        if not (station.smu_dual and station.lockin):
            raise RuntimeError("Dual SMU and lock-in required for two-device measurements")
            
        self.smu = station.smu_dual
        self.lockin = station.lockin
        
        # Configure both SMU channels
        self.smu.configure_voltage_source('a')
        self.smu.configure_voltage_source('b')
        self.smu.set_compliance('a', current_limit=1e-6)
        self.smu.set_compliance('b', current_limit=1e-6)
        
    def run_synchronized_sweep(self, params: DifferentialParameters,
                              voltage_ratio: float = 1.0,
                              dataset_name: str = "two_device_differential") -> Dict[str, np.ndarray]:
        """
        Run synchronized differential measurements on both devices.
        
        Args:
            params: Measurement parameters
            voltage_ratio: Voltage ratio between device B and device A
            dataset_name: Dataset name
            
        Returns:
            Dictionary with two-device measurement data
        """
        voltage_points = np.linspace(params.start_voltage, params.stop_voltage, params.num_points)
        
        if params.bidirectional:
            reverse_points = voltage_points[::-1]
            voltage_points = np.concatenate([voltage_points, reverse_points])
            
        # Configure lock-in
        self.lockin.frequency(params.frequency)
        self.lockin.amplitude(params.ac_amplitude)
        self.lockin.time_constant(params.time_constant)
        
        # Set up measurement parameters
        meas = Measurement()
        meas.register_parameter(self.smu.voltage_a)
        meas.register_parameter(self.smu.voltage_b)
        meas.register_parameter(self.smu.current_a, setpoints=(self.smu.voltage_a,))
        meas.register_parameter(self.smu.current_b, setpoints=(self.smu.voltage_b,))
        meas.register_parameter(self.lockin.amplitude_x, setpoints=(self.smu.voltage_a, self.smu.voltage_b))
        meas.register_parameter(self.lockin.amplitude_y, setpoints=(self.smu.voltage_a, self.smu.voltage_b))
        
        results = {
            'voltage_a': [],
            'voltage_b': [],
            'current_a': [],
            'current_b': [],
            'resistance_a': [],
            'resistance_b': [],
            'diff_voltage_x': [],
            'diff_voltage_y': [],
            'diff_conductance_a': [],
            'diff_conductance_b': []
        }
        
        # Enable outputs
        self.smu.output_a(True)
        self.smu.output_b(True)
        
        try:
            with meas.run() as datasaver:
                for voltage_a in voltage_points:
                    voltage_b = voltage_a * voltage_ratio
                    
                    # Set DC bias voltages
                    self.smu.voltage_a(voltage_a)
                    self.smu.voltage_b(voltage_b)
                    
                    # Wait for settling
                    time.sleep(params.delay_between_points)
                    self.lockin.wait_for_settling()
                    
                    # Take averaged measurements
                    current_a_measurements = []
                    current_b_measurements = []
                    ac_measurements = []
                    
                    for _ in range(params.averages):
                        current_a_measurements.append(self.smu.current_a())
                        current_b_measurements.append(self.smu.current_b())
                        ac_measurements.append(self.lockin.measure_with_averaging(1))
                        time.sleep(0.05)
                        
                    # Calculate averages
                    current_a_avg = np.mean(current_a_measurements)
                    current_b_avg = np.mean(current_b_measurements)
                    
                    ac_x_avg = np.mean([m['x'] for m in ac_measurements])
                    ac_y_avg = np.mean([m['y'] for m in ac_measurements])
                    
                    # Calculate resistances
                    resistance_a = voltage_a / current_a_avg if current_a_avg != 0 else np.inf
                    resistance_b = voltage_b / current_b_avg if current_b_avg != 0 else np.inf
                    
                    # Estimate differential conductances
                    # This is simplified - in practice would need separate lock-in channels
                    diff_cond_a = params.ac_amplitude / np.sqrt(ac_x_avg**2 + ac_y_avg**2) if ac_x_avg != 0 or ac_y_avg != 0 else 0
                    diff_cond_b = diff_cond_a * (resistance_a / resistance_b) if resistance_b != 0 else 0
                    
                    # Save data
                    datasaver.add_result(
                        (self.smu.voltage_a, voltage_a),
                        (self.smu.voltage_b, voltage_b),
                        (self.smu.current_a, current_a_avg),
                        (self.smu.current_b, current_b_avg),
                        (self.lockin.amplitude_x, ac_x_avg),
                        (self.lockin.amplitude_y, ac_y_avg)
                    )
                    
                    # Store results
                    results['voltage_a'].append(voltage_a)
                    results['voltage_b'].append(voltage_b)
                    results['current_a'].append(current_a_avg)
                    results['current_b'].append(current_b_avg)
                    results['resistance_a'].append(resistance_a)
                    results['resistance_b'].append(resistance_b)
                    results['diff_voltage_x'].append(ac_x_avg)
                    results['diff_voltage_y'].append(ac_y_avg)
                    results['diff_conductance_a'].append(diff_cond_a)
                    results['diff_conductance_b'].append(diff_cond_b)
                    
        finally:
            # Safe shutdown
            self.smu.voltage_a(0.0)
            self.smu.voltage_b(0.0)
            self.smu.output_a(False)
            self.smu.output_b(False)
            
        return {key: np.array(value) for key, value in results.items()}


class HarmonicDifferentialMeasurement:
    """
    Differential measurements with harmonic analysis (w, 2w, 3w).
    
    Equivalent to LabVIEW VIs with harmonic content analysis.
    """
    
    def __init__(self, station: BlueforsStation, smu_channel: str = 'a'):
        """
        Initialize harmonic differential measurement.
        
        Args:
            station: Configured BlueforsStation
            smu_channel: SMU channel for DC bias
        """
        self.station = station
        self.smu_channel = smu_channel
        
        if not (station.smu_dual and station.lockin):
            raise RuntimeError("SMU and lock-in required for harmonic measurements")
            
        self.smu = station.smu_dual
        self.lockin = station.lockin
        
    def run_harmonic_sweep(self, params: DifferentialParameters,
                          dataset_name: str = "harmonic_differential") -> Dict[str, np.ndarray]:
        """
        Run differential measurement with harmonic analysis.
        
        Args:
            params: Measurement parameters
            dataset_name: Dataset name
            
        Returns:
            Dictionary with harmonic measurement data
        """
        voltage_points = np.linspace(params.start_voltage, params.stop_voltage, params.num_points)
        
        if params.bidirectional:
            reverse_points = voltage_points[::-1]
            voltage_points = np.concatenate([voltage_points, reverse_points])
            
        # Configure lock-in for harmonic measurements
        self.lockin.frequency(params.frequency)
        self.lockin.amplitude(params.ac_amplitude)
        self.lockin.time_constant(params.time_constant)
        self.lockin.configure_harmonic_measurement([1, 2, 3])
        
        # Configure SMU
        dc_voltage_param = getattr(self.smu, f'voltage_{self.smu_channel}')
        output_param = getattr(self.smu, f'output_{self.smu_channel}')
        
        self.smu.configure_voltage_source(self.smu_channel)
        self.smu.set_compliance(self.smu_channel, current_limit=1e-6)
        
        results = {
            'voltage': [],
            'fundamental_x': [],
            'fundamental_y': [],
            'harmonic_2w_x': [],
            'harmonic_2w_y': [],
            'harmonic_3w_x': [],
            'harmonic_3w_y': [],
            'fundamental_conductance': [],
            'harmonic_2w_amplitude': [],
            'harmonic_3w_amplitude': []
        }
        
        output_param(True)
        
        try:
            for voltage in voltage_points:
                dc_voltage_param(voltage)
                
                # Wait for settling
                time.sleep(params.delay_between_points)
                self.lockin.wait_for_settling()
                
                # Measure all harmonics
                fund_x_avg = 0
                fund_y_avg = 0
                h2w_x_avg = 0
                h2w_y_avg = 0
                h3w_x_avg = 0
                h3w_y_avg = 0
                
                for _ in range(params.averages):
                    fund_x_avg += self.lockin.amplitude_x()
                    fund_y_avg += self.lockin.amplitude_y()
                    h2w_x_avg += self.lockin.harmonic_2w_x()
                    h2w_y_avg += self.lockin.harmonic_2w_y()
                    h3w_x_avg += self.lockin.harmonic_3w_x()
                    h3w_y_avg += self.lockin.harmonic_3w_y()
                    time.sleep(0.05)
                    
                # Calculate averages
                fund_x_avg /= params.averages
                fund_y_avg /= params.averages
                h2w_x_avg /= params.averages
                h2w_y_avg /= params.averages
                h3w_x_avg /= params.averages
                h3w_y_avg /= params.averages
                
                # Calculate conductances and amplitudes
                fund_conductance = params.ac_amplitude / np.sqrt(fund_x_avg**2 + fund_y_avg**2)
                h2w_amplitude = np.sqrt(h2w_x_avg**2 + h2w_y_avg**2)
                h3w_amplitude = np.sqrt(h3w_x_avg**2 + h3w_y_avg**2)
                
                # Store results
                results['voltage'].append(voltage)
                results['fundamental_x'].append(fund_x_avg)
                results['fundamental_y'].append(fund_y_avg)
                results['harmonic_2w_x'].append(h2w_x_avg)
                results['harmonic_2w_y'].append(h2w_y_avg)
                results['harmonic_3w_x'].append(h3w_x_avg)
                results['harmonic_3w_y'].append(h3w_y_avg)
                results['fundamental_conductance'].append(fund_conductance)
                results['harmonic_2w_amplitude'].append(h2w_amplitude)
                results['harmonic_3w_amplitude'].append(h3w_amplitude)
                
        finally:
            # Safe shutdown
            dc_voltage_param(0.0)
            output_param(False)
            
        return {key: np.array(value) for key, value in results.items()}