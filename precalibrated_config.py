#!/usr/bin/env python3
"""
ODrive Pre-Calibrated Configuration - Generated on 2025-04-30 14:55:14
This module contains pre-calibrated values for the ODrive.
Import this module in motor_control.py to use these values.
"""

# ODrive Serial Number: 57531981246515

# Axis 0 configuration
AXIS0_CONFIG = {
    "motor": {
        "phase_resistance": 0.07072214037179947,
        "phase_inductance": 0.0004009606200270355,
        "pole_pairs": 3,
        "motor_type": 0,
        "current_lim": 40.0,
        "calibration_current": 10.0,
        "resistance_calib_max_voltage": 2.0,
    },
    "encoder": {
        "mode": 0,
        "use_index": false,
        "cpr": 4000,
