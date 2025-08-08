"""
LabVIEW to Python/QCoDeS Migration Documentation

This file documents the mapping between LabVIEW VIs and Python implementations.
"""

# LabVIEW VI to Python Class Mapping

LABVIEW_TO_PYTHON_MAPPING = {
    
    # Current-Voltage Measurements
    "I(V)_K6221-K2182a_PK.vi": {
        "python_class": "bluefors_dc.measurements.IVMeasurement",
        "description": "Basic I-V measurement using K6221 current source and K2182A nanovoltmeter",
        "key_features": [
            "Delta mode current sourcing",
            "High precision voltage measurement", 
            "Bidirectional current sweep",
            "Compliance voltage protection"
        ],
        "equivalent_method": "run_sweep()",
        "parameters": "IVSweepParameters"
    },
    
    "I(V)_K2636B_PK.vi": {
        "python_class": "bluefors_dc.measurements.IVMeasurement2636B", 
        "description": "I-V measurement using K2636B dual SMU",
        "key_features": [
            "Single instrument current sourcing and voltage measurement",
            "Built-in compliance limiting",
            "Dual channel capability"
        ],
        "equivalent_method": "run_sweep()",
        "parameters": "IVSweepParameters"
    },
    
    "I(V) at various fields_K6221-K2182A_PK.vi": {
        "python_class": "bluefors_dc.measurements.IVFieldSweep",
        "description": "I-V measurements at multiple magnetic field points",
        "key_features": [
            "Automated field stepping",
            "Field stabilization waiting",
            "Multi-field I-V data collection"
        ],
        "equivalent_method": "run_field_sweep()",
        "parameters": "IVSweepParameters + field_points list"
    },
    
    "I(V)_MFLI_PK_v4.0_measure X.vi": {
        "python_class": "bluefors_dc.measurements.IVACMeasurement",
        "description": "AC I-V measurement using MFLI lock-in amplifier",
        "key_features": [
            "Lock-in amplifier measurement",
            "AC current sourcing",
            "Phase and amplitude detection",
            "Differential resistance calculation"
        ],
        "equivalent_method": "run_sweep()",
        "parameters": "voltage_points, current_amplitude"
    },
    
    # Differential Conductance Measurements
    "dI-dV(V)_MFLI_MF-MD_K3636B_measureX_PK_V4.0_withaveraging.vi": {
        "python_class": "bluefors_dc.measurements.DifferentialConductance",
        "description": "Differential conductance measurement with lock-in detection",
        "key_features": [
            "DC bias voltage sweep with SMU",
            "AC modulation with lock-in",
            "Multi-point averaging",
            "dI/dV calculation"
        ],
        "equivalent_method": "run_sweep()",
        "parameters": "DifferentialParameters"
    },
    
    "STS at various H_MFLI_MF-MD_K3636B_PK_V4.0_withaveraging.vi": {
        "python_class": "bluefors_dc.measurements.STSMeasurement",
        "description": "Scanning tunneling spectroscopy at various magnetic fields",
        "key_features": [
            "Field-dependent dI/dV measurements",
            "Tunneling spectroscopy protocol",
            "Field stabilization between measurements"
        ],
        "equivalent_method": "run_field_sweep()",
        "parameters": "DifferentialParameters + field_points"
    },
    
    "dV-dI two devices at various H_MFLI_MF-MD_K3636B_PK_V4.0_withaveraging.vi": {
        "python_class": "bluefors_dc.measurements.TwoDeviceDifferential",
        "description": "Differential measurements on two devices simultaneously",
        "key_features": [
            "Dual device measurements",
            "Synchronized voltage biasing",
            "Comparative analysis"
        ],
        "equivalent_method": "run_synchronized_sweep()",
        "parameters": "DifferentialParameters + voltage_ratio"
    },
    
    # Transport Measurements
    "RH_BF_LD-400_MFLI_PK_v4.0_measure_voltageR_fourMFLI.vi": {
        "python_class": "bluefors_dc.measurements.HallMeasurement",
        "description": "Hall resistance measurements with magnetic field sweep",
        "key_features": [
            "Hall effect measurement",
            "Transverse resistance measurement",
            "Field sweep with AC or DC detection"
        ],
        "equivalent_method": "run_hall_sweep()",
        "parameters": "HallMeasurementParameters"
    },
    
    "RT_BF_LD-400_MFLI_PK_v4.0_measure_voltageR_fourMFLI.vi": {
        "python_class": "bluefors_dc.measurements.TemperatureResistanceSweep",
        "description": "Resistance vs temperature measurements",
        "key_features": [
            "Temperature sweep control",
            "Temperature stabilization waiting",
            "Resistance monitoring vs temperature"
        ],
        "equivalent_method": "run_temperature_sweep()",
        "parameters": "temperature_points, current_amplitude"
    },
    
    # Real-time Monitoring
    "realtime_IV_K2182A_K6221_vs_time_PK.vi": {
        "python_class": "bluefors_dc.measurements.RealTimeMonitoring",
        "description": "Real-time resistance monitoring",
        "key_features": [
            "Continuous resistance monitoring",
            "Time-stamped data collection",
            "Background measurement thread"
        ],
        "equivalent_method": "start_monitoring()",
        "parameters": "current_amplitude, measurement_interval"
    },
    
    # Instrument Control
    "AMI430_Magnet controller Interface_PK.vi": {
        "python_class": "bluefors_dc.instruments.AMI430MagnetController",
        "description": "2-axis magnet controller interface",
        "key_features": [
            "Vector field control",
            "Polar and Cartesian coordinates",
            "Ramp rate control",
            "Safety interlocks"
        ],
        "equivalent_methods": [
            "set_field_vector()",
            "set_field_polar()",
            "wait_for_ramp_completion()"
        ]
    },
    
    "T_MXC_control_PK_v1.0.vi": {
        "python_class": "bluefors_dc.instruments.Lakeshore372", 
        "description": "Temperature control interface",
        "key_features": [
            "Multi-channel temperature monitoring",
            "PID control loops",
            "Temperature ramping",
            "Scanner configuration"
        ],
        "equivalent_methods": [
            "set_temperature()",
            "wait_for_temperature()",
            "configure_control_loop()"
        ]
    },
    
    # Vector Magnet Sweeps
    "IV(H)_DC_vector_magnet_anglesweep_BF_LD-400_K6221_K2182A_PK.vi": {
        "python_class": "bluefors_dc.measurements.IVFieldSweep",
        "description": "I-V measurements with vector magnet angle sweep",
        "key_features": [
            "Fixed field magnitude",
            "Angle sweep from 0 to 360 degrees",
            "Vector field coordination"
        ],
        "equivalent_method": "run_angle_sweep()",
        "parameters": "IVSweepParameters + field_magnitude + angles"
    },
    
    # Field Mapping
    "RH vector map_two devices_BF_LD-400_MFLI_MF-MD_PK_V5.0.vi": {
        "python_class": "bluefors_dc.measurements.HallMeasurement",
        "description": "2D Hall resistance mapping",
        "key_features": [
            "2D field space mapping",
            "Multiple device measurements",
            "Vector field control"
        ],
        "equivalent_method": "run_hall_sweep()",
        "parameters": "HallMeasurementParameters with 2D field grid"
    }
}

# Migration Notes

MIGRATION_NOTES = {
    "data_structures": {
        "labview": "Clusters, arrays, waveforms, dynamic data types",
        "python": "NumPy arrays, dictionaries, DataFrames, QCoDeS datasets",
        "conversion": "Direct mapping with type conversion utilities"
    },
    
    "control_flow": {
        "labview": "State machines, producer-consumer loops, event structures",
        "python": "Classes, threading, async/await, context managers",
        "patterns": "Object-oriented design with QCoDeS framework integration"
    },
    
    "instrument_communication": {
        "labview": "VISA drivers, property nodes, invoke methods",
        "python": "QCoDeS instrument drivers, parameters, validators",
        "benefits": "Improved error handling, automatic logging, parameter validation"
    },
    
    "data_management": {
        "labview": "TDMS files, spreadsheet files",
        "python": "SQLite databases (QCoDeS), HDF5 files, CSV exports", 
        "advantages": "Better data relationships, metadata storage, analysis integration"
    },
    
    "safety_features": {
        "labview": "Manual interlocks, limit checking in VIs",
        "python": "Centralized SafetyChecks class, parameter validators, automatic compliance",
        "improvements": "Systematic safety checking, customizable limits, interlock management"
    },
    
    "performance": {
        "considerations": [
            "Python may be slower for tight loops but offers better analysis tools",
            "NumPy operations are highly optimized for array processing",
            "QCoDeS provides efficient data storage and retrieval",
            "Matplotlib/PyQtGraph offer superior plotting capabilities"
        ]
    }
}

# Usage Examples

USAGE_EXAMPLES = {
    "basic_iv": """
from bluefors_dc.measurements import BlueforsStation, IVMeasurement, IVSweepParameters

station = BlueforsStation()
station.add_current_source('TCPIP::192.168.1.101::INSTR')
station.add_nanovoltmeter('TCPIP::192.168.1.102::INSTR')

iv_measurement = IVMeasurement(station)
params = IVSweepParameters(start_current=-1e-6, stop_current=1e-6, num_points=101)
data = iv_measurement.run_sweep(params)
""",
    
    "differential_conductance": """
from bluefors_dc.measurements import DifferentialConductance, DifferentialParameters

station.add_dual_smu('TCPIP::192.168.1.103::INSTR')
station.add_lock_in('dev1234')

diff_measurement = DifferentialConductance(station)
params = DifferentialParameters(
    start_voltage=-0.01, stop_voltage=0.01, num_points=201,
    ac_amplitude=0.001, frequency=1000.0
)
data = diff_measurement.run_sweep(params)
""",
    
    "field_dependent_measurement": """
from bluefors_dc.measurements import IVFieldSweep
import numpy as np

station.add_magnet_controller('TCPIP::192.168.1.100::7180::SOCKET')

iv_field = IVFieldSweep(station)
field_points = [(0, 0), (1, 0), (0, 1), (1, 1)]  # (Bx, By) in Tesla
data = iv_field.run_field_sweep(iv_params, field_points)
"""
}

# API Reference

API_REFERENCE = {
    "station_setup": {
        "BlueforsStation": "Central station class managing all instruments",
        "add_*_methods": "Methods to add instruments with automatic configuration",
        "setup_*_measurement": "Configure station for specific measurement types"
    },
    
    "measurement_classes": {
        "IVMeasurement": "Basic current-voltage measurements",
        "DifferentialConductance": "dI/dV measurements with lock-in detection",
        "HallMeasurement": "Hall resistance measurements",
        "TransportMeasurement": "General transport measurement base class"
    },
    
    "instrument_drivers": {
        "AMI430MagnetController": "2-axis vector magnet control",
        "Keithley6221/2182A/2636B": "Current sources and voltage measurement",
        "ZurichMFLI": "Lock-in amplifier with harmonic detection",
        "Lakeshore372": "Temperature controller with multi-channel monitoring"
    },
    
    "utility_classes": {
        "SafetyChecks": "Parameter validation and safety interlocks",
        "DataAnalysisTools": "Analysis utilities for measurement data",
        "PlottingTools": "Visualization utilities"
    }
}