"""
Example configuration file for Bluefors DC measurement system.

This file shows how to configure the station with all instruments
and their typical settings.
"""

# Instrument addresses and settings
INSTRUMENTS = {
    'magnet_controller': {
        'address': 'TCPIP::192.168.1.100::7180::SOCKET',
        'name': 'magnet',
        'field_limit': 9.0,  # Tesla
        'default_ramp_rate': 0.1,  # T/min
    },
    
    'current_source': {
        'address': 'TCPIP::192.168.1.101::INSTR',
        'name': 'current_source',
        'default_compliance': 10.0,  # V
        'default_range': 1e-6,  # A
    },
    
    'nanovoltmeter': {
        'address': 'TCPIP::192.168.1.102::INSTR', 
        'name': 'nanovoltmeter',
        'default_nplc': 1.0,
        'auto_range': True,
    },
    
    'dual_smu': {
        'address': 'TCPIP::192.168.1.103::INSTR',
        'name': 'smu_dual',
        'voltage_limit': 200.0,  # V
        'current_limit': 1.5,    # A
    },
    
    'lock_in': {
        'device_id': 'dev1234',
        'name': 'lockin',
        'default_frequency': 1000.0,  # Hz
        'default_amplitude': 0.01,    # V
        'default_time_constant': 0.1, # s
    },
    
    'temperature_controller': {
        'address': 'TCPIP::192.168.1.104::INSTR',
        'name': 'temperature',
        'control_loops': [1, 2],
        'scanner_channels': [1, 2, 3, 4, 5, 6],
    }
}

# Safety limits
SAFETY_LIMITS = {
    'max_magnetic_field': 9.0,          # Tesla
    'max_field_ramp_rate': 1.0,         # T/min
    'max_current': 0.1,                 # A
    'max_voltage': 200.0,               # V  
    'max_temperature': 400.0,           # K
    'min_temperature': 0.01,            # K
    'max_temperature_ramp_rate': 5.0,   # K/min
}

# Default measurement parameters
DEFAULT_MEASUREMENT_PARAMS = {
    'iv_measurement': {
        'current_range': (-1e-6, 1e-6),  # A
        'num_points': 100,
        'delay_between_points': 0.1,     # s
        'compliance_voltage': 10.0,      # V
        'bidirectional': True,
    },
    
    'differential_measurement': {
        'voltage_range': (-0.01, 0.01),  # V
        'num_points': 200,
        'ac_amplitude': 0.001,           # V
        'frequency': 1000.0,             # Hz
        'time_constant': 0.03,           # s
        'averages': 5,
    },
    
    'hall_measurement': {
        'field_range': (-9.0, 9.0),     # T
        'field_points': 100,
        'current_amplitude': 1e-6,       # A
        'measurement_delay': 1.0,        # s
    },
    
    'temperature_sweep': {
        'settling_time': 300.0,          # s
        'temperature_tolerance': 0.01,    # K
        'measurement_averages': 10,
    }
}

# File paths and data management
DATA_PATHS = {
    'base_directory': r'C:\Bluefors_Data',
    'raw_data_subdir': 'raw_data',
    'processed_data_subdir': 'processed_data',
    'plots_subdir': 'plots',
    'logs_subdir': 'logs',
}

# Plotting preferences
PLOTTING_DEFAULTS = {
    'figure_size': (10, 8),
    'dpi': 300,
    'font_size': 12,
    'line_width': 2,
    'marker_size': 6,
    'color_scheme': 'viridis',
    'save_format': 'png',
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_handler': True,
    'console_handler': True,
    'max_file_size': 10,  # MB
    'backup_count': 5,
}