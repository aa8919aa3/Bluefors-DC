"""
Zurich Instruments MFLI Lock-in Amplifier Driver

QCoDeS driver for the Zurich Instruments MFLI lock-in amplifier
used for AC transport measurements and harmonic analysis.
"""

import numpy as np
from typing import Union, List, Dict
from qcodes import Instrument, validators as vals
from qcodes.parameters import Parameter
import time


class ZurichMFLI(Instrument):
    """
    QCoDeS driver for Zurich Instruments MFLI Lock-in Amplifier.
    
    Provides AC voltage/current measurements with harmonic detection
    capabilities for transport measurements.
    """
    
    def __init__(self, name: str, device_id: str = None, **kwargs):
        """
        Initialize MFLI lock-in amplifier.
        
        Args:
            name: Name of the instrument
            device_id: Device ID (e.g., 'dev1234')
        """
        super().__init__(name, **kwargs)
        
        # Store device ID for API calls
        self.device_id = device_id or 'dev1234'
        
        # Initialize Zurich Instruments API (would need actual ziPython)
        # For now, create placeholder for the connection
        self._daq = None  # Placeholder for actual DAQ module
        
        # AC voltage measurement parameters
        self.add_parameter(
            'amplitude_x',
            get_cmd=self._get_amplitude_x,
            unit='V',
            docstring='Lock-in X amplitude (in-phase)'
        )
        
        self.add_parameter(
            'amplitude_y', 
            get_cmd=self._get_amplitude_y,
            unit='V',
            docstring='Lock-in Y amplitude (quadrature)'
        )
        
        self.add_parameter(
            'phase',
            get_cmd=self._get_phase,
            set_cmd=self._set_phase,
            unit='deg',
            vals=vals.Numbers(-180, 180),
            docstring='Lock-in phase'
        )
        
        self.add_parameter(
            'frequency',
            get_cmd=self._get_frequency,
            set_cmd=self._set_frequency,
            unit='Hz',
            vals=vals.Numbers(1e-3, 5e6),
            docstring='Oscillator frequency'
        )
        
        self.add_parameter(
            'amplitude',
            get_cmd=self._get_amplitude,
            set_cmd=self._set_amplitude,
            unit='V',
            vals=vals.Numbers(0, 1.5),
            docstring='Output amplitude'
        )
        
        # Time constant
        self.add_parameter(
            'time_constant',
            get_cmd=self._get_time_constant,
            set_cmd=self._set_time_constant,
            unit='s',
            vals=vals.Numbers(1e-6, 30),
            docstring='Lock-in time constant'
        )
        
        # Input range
        self.add_parameter(
            'input_range',
            get_cmd=self._get_input_range,
            set_cmd=self._set_input_range,
            unit='V',
            docstring='Input voltage range'
        )
        
        # Harmonic measurement parameters
        self.add_parameter(
            'harmonic_2w_x',
            get_cmd=lambda: self._get_harmonic_amplitude(2, 'x'),
            unit='V',
            docstring='2nd harmonic X amplitude'
        )
        
        self.add_parameter(
            'harmonic_2w_y',
            get_cmd=lambda: self._get_harmonic_amplitude(2, 'y'), 
            unit='V',
            docstring='2nd harmonic Y amplitude'
        )
        
        self.add_parameter(
            'harmonic_3w_x',
            get_cmd=lambda: self._get_harmonic_amplitude(3, 'x'),
            unit='V',
            docstring='3rd harmonic X amplitude'
        )
        
        self.add_parameter(
            'harmonic_3w_y',
            get_cmd=lambda: self._get_harmonic_amplitude(3, 'y'),
            unit='V', 
            docstring='3rd harmonic Y amplitude'
        )
        
        self.connect_message()
        
    def _get_amplitude_x(self) -> float:
        """Get X amplitude from demodulator."""
        # Placeholder - would use actual Zurich API
        return 0.0
        
    def _get_amplitude_y(self) -> float:
        """Get Y amplitude from demodulator."""
        # Placeholder - would use actual Zurich API
        return 0.0
        
    def _get_phase(self) -> float:
        """Get phase from demodulator."""
        # Placeholder - would use actual Zurich API
        return 0.0
        
    def _set_phase(self, phase: float) -> None:
        """Set phase of demodulator."""
        # Placeholder - would use actual Zurich API
        pass
        
    def _get_frequency(self) -> float:
        """Get oscillator frequency."""
        # Placeholder - would use actual Zurich API
        return 1000.0
        
    def _set_frequency(self, frequency: float) -> None:
        """Set oscillator frequency.""" 
        # Placeholder - would use actual Zurich API
        pass
        
    def _get_amplitude(self) -> float:
        """Get output amplitude."""
        # Placeholder - would use actual Zurich API
        return 0.1
        
    def _set_amplitude(self, amplitude: float) -> None:
        """Set output amplitude."""
        # Placeholder - would use actual Zurich API
        pass
        
    def _get_time_constant(self) -> float:
        """Get time constant."""
        # Placeholder - would use actual Zurich API
        return 0.01
        
    def _set_time_constant(self, tc: float) -> None:
        """Set time constant."""
        # Placeholder - would use actual Zurich API
        pass
        
    def _get_input_range(self) -> float:
        """Get input range."""
        # Placeholder - would use actual Zurich API
        return 1.0
        
    def _set_input_range(self, range_val: float) -> None:
        """Set input range."""
        # Placeholder - would use actual Zurich API
        pass
        
    def _get_harmonic_amplitude(self, harmonic: int, component: str) -> float:
        """
        Get harmonic amplitude for specified harmonic and component.
        
        Args:
            harmonic: Harmonic number (2, 3, etc.)
            component: 'x' or 'y' for in-phase or quadrature
            
        Returns:
            Harmonic amplitude
        """
        # Placeholder - would use actual Zurich API with multiple demodulators
        return 0.0
        
    def get_amplitude_phase(self) -> tuple:
        """
        Get amplitude and phase from lock-in measurement.
        
        Returns:
            Tuple of (amplitude, phase) where amplitude is R = sqrt(X² + Y²)
            and phase is in degrees
        """
        x = self.amplitude_x()
        y = self.amplitude_y()
        
        amplitude = np.sqrt(x**2 + y**2)
        phase = np.degrees(np.arctan2(y, x))
        
        return amplitude, phase
        
    def measure_resistance(self, current_amplitude: float) -> float:
        """
        Calculate resistance from voltage and current amplitudes.
        
        Args:
            current_amplitude: Applied current amplitude in A
            
        Returns:
            Resistance in Ohms
        """
        voltage_amplitude, _ = self.get_amplitude_phase()
        return voltage_amplitude / current_amplitude if current_amplitude != 0 else np.inf
        
    def configure_harmonic_measurement(self, harmonics: List[int] = [1, 2, 3]) -> None:
        """
        Configure lock-in for harmonic measurements.
        
        Args:
            harmonics: List of harmonic numbers to measure
        """
        # Placeholder - would configure multiple demodulators
        # for different harmonics in actual implementation
        pass
        
    def wait_for_settling(self, settling_factor: float = 5.0) -> None:
        """
        Wait for lock-in to settle based on time constant.
        
        Args:
            settling_factor: Multiplier for time constant to determine settling time
        """
        tc = self.time_constant()
        settling_time = tc * settling_factor
        time.sleep(settling_time)
        
    def auto_phase(self) -> float:
        """
        Perform automatic phase adjustment to maximize X component.
        
        Returns:
            Optimized phase in degrees
        """
        # Simple auto-phase implementation
        # In practice, would use built-in auto-phase functionality
        best_phase = 0
        best_x = 0
        
        for phase in np.linspace(-180, 180, 361):
            self.phase(phase)
            time.sleep(0.1)  # Brief settling
            x = self.amplitude_x()
            if abs(x) > abs(best_x):
                best_x = x
                best_phase = phase
                
        self.phase(best_phase)
        return best_phase
        
    def measure_with_averaging(self, averages: int = 10, 
                              delay: float = None) -> Dict[str, float]:
        """
        Take averaged measurement.
        
        Args:
            averages: Number of measurements to average
            delay: Delay between measurements (default: 2 * time_constant)
            
        Returns:
            Dictionary with averaged X, Y, R, and phase values
        """
        if delay is None:
            delay = 2 * self.time_constant()
            
        x_values = []
        y_values = []
        
        for _ in range(averages):
            x_values.append(self.amplitude_x())
            y_values.append(self.amplitude_y())
            if averages > 1:
                time.sleep(delay)
                
        x_avg = np.mean(x_values)
        y_avg = np.mean(y_values)
        r_avg = np.sqrt(x_avg**2 + y_avg**2)
        phase_avg = np.degrees(np.arctan2(y_avg, x_avg))
        
        return {
            'x': x_avg,
            'y': y_avg, 
            'r': r_avg,
            'phase': phase_avg,
            'x_std': np.std(x_values),
            'y_std': np.std(y_values)
        }
        
    def get_idn(self) -> dict:
        """Get instrument identification."""
        # Placeholder - would query actual device info
        return {
            'vendor': 'Zurich Instruments',
            'model': 'MFLI',
            'serial': self.device_id,
            'firmware': '1.0.0'
        }