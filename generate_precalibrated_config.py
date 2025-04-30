#!/usr/bin/env python3
"""
ODrive Pre-Calibrated Configuration Generator.
This script pulls the current configuration from the ODrive and generates
a Python module with pre-calibrated values that can be imported in motor_control.py.
"""
import odrive
import time
import sys
import os
import datetime

def connect_to_odrive():
    """Connect to the ODrive."""
    print("Connecting to ODrive...")
    try:
        odrv = odrive.find_any()
        print(f"Found ODrive: {str(odrv.serial_number)}")
        return odrv
    except:
        print("Failed to find ODrive. Make sure it's connected and powered on.")
        sys.exit(1)

def generate_precalibrated_module(odrv, output_file="precalibrated_config.py"):
    """
    Generate a Python module with pre-calibrated values from the current ODrive configuration.
    
    Args:
        odrv: ODrive object
        output_file: Output Python file
    """
    print(f"Generating pre-calibrated configuration module: {output_file}")
    
    # Create timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(output_file, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""\n')
        f.write(f'ODrive Pre-Calibrated Configuration - Generated on {timestamp}\n')
        f.write('This module contains pre-calibrated values for the ODrive.\n')
        f.write('Import this module in motor_control.py to use these values.\n')
        f.write('"""\n\n')
        
        f.write(f'# ODrive Serial Number: {odrv.serial_number}\n\n')
        
        # Axis 0 configuration
        f.write('# Axis 0 configuration\n')
        f.write('AXIS0_CONFIG = {\n')
        
        # Motor configuration
        f.write('    "motor": {\n')
        f.write(f'        "phase_resistance": {odrv.axis0.motor.config.phase_resistance},\n')
        f.write(f'        "phase_inductance": {odrv.axis0.motor.config.phase_inductance},\n')
        f.write(f'        "pole_pairs": {odrv.axis0.motor.config.pole_pairs},\n')
        f.write(f'        "motor_type": {odrv.axis0.motor.config.motor_type},\n')
        f.write(f'        "current_lim": {odrv.axis0.motor.config.current_lim},\n')
        f.write(f'        "calibration_current": {odrv.axis0.motor.config.calibration_current},\n')
        f.write(f'        "resistance_calib_max_voltage": {odrv.axis0.motor.config.resistance_calib_max_voltage},\n')
        f.write('    },\n')
        
        # Encoder configuration
        f.write('    "encoder": {\n')
        f.write(f'        "mode": {odrv.axis0.encoder.config.mode},\n')
        f.write(f'        "use_index": {str(odrv.axis0.encoder.config.use_index).lower()},\n')
        f.write(f'        "cpr": {odrv.axis0.encoder.config.cpr},\n')
        f.write(f'        "offset": {odrv.axis0.encoder.config.offset},\n')
        f.write(f'        "offset_float": {odrv.axis0.encoder.config.offset_float},\n')
        f.write(f'        "bandwidth": {odrv.axis0.encoder.config.bandwidth},\n')
        f.write(f'        "calib_scan_distance": {odrv.axis0.encoder.config.calib_scan_distance},\n')
        f.write('    },\n')
        
        # Controller configuration
        f.write('    "controller": {\n')
        f.write(f'        "control_mode": {odrv.axis0.controller.config.control_mode},\n')
        f.write(f'        "pos_gain": {odrv.axis0.controller.config.pos_gain},\n')
        f.write(f'        "vel_gain": {odrv.axis0.controller.config.vel_gain},\n')
        f.write(f'        "vel_integrator_gain": {odrv.axis0.controller.config.vel_integrator_gain},\n')
        f.write(f'        "vel_limit": {odrv.axis0.controller.config.vel_limit},\n')
        f.write(f'        "vel_ramp_rate": {odrv.axis0.controller.config.vel_ramp_rate},\n')
        f.write('    },\n')
        
        f.write('}\n\n')
        
        # Axis 1 configuration
        f.write('# Axis 1 configuration\n')
        f.write('AXIS1_CONFIG = {\n')
        
        # Motor configuration
        f.write('    "motor": {\n')
        f.write(f'        "phase_resistance": {odrv.axis1.motor.config.phase_resistance},\n')
        f.write(f'        "phase_inductance": {odrv.axis1.motor.config.phase_inductance},\n')
        f.write(f'        "pole_pairs": {odrv.axis1.motor.config.pole_pairs},\n')
        f.write(f'        "motor_type": {odrv.axis1.motor.config.motor_type},\n')
        f.write(f'        "current_lim": {odrv.axis1.motor.config.current_lim},\n')
        f.write(f'        "calibration_current": {odrv.axis1.motor.config.calibration_current},\n')
        f.write(f'        "resistance_calib_max_voltage": {odrv.axis1.motor.config.resistance_calib_max_voltage},\n')
        f.write('    },\n')
        
        # Encoder configuration
        f.write('    "encoder": {\n')
        f.write(f'        "mode": {odrv.axis1.encoder.config.mode},\n')
        f.write(f'        "use_index": {str(odrv.axis1.encoder.config.use_index).lower()},\n')
        f.write(f'        "cpr": {odrv.axis1.encoder.config.cpr},\n')
        f.write(f'        "offset": {odrv.axis1.encoder.config.offset},\n')
        f.write(f'        "offset_float": {odrv.axis1.encoder.config.offset_float},\n')
        f.write(f'        "bandwidth": {odrv.axis1.encoder.config.bandwidth},\n')
        f.write(f'        "calib_scan_distance": {odrv.axis1.encoder.config.calib_scan_distance},\n')
        f.write('    },\n')
        
        # Controller configuration
        f.write('    "controller": {\n')
        f.write(f'        "control_mode": {odrv.axis1.controller.config.control_mode},\n')
        f.write(f'        "pos_gain": {odrv.axis1.controller.config.pos_gain},\n')
        f.write(f'        "vel_gain": {odrv.axis1.controller.config.vel_gain},\n')
        f.write(f'        "vel_integrator_gain": {odrv.axis1.controller.config.vel_integrator_gain},\n')
        f.write(f'        "vel_limit": {odrv.axis1.controller.config.vel_limit},\n')
        f.write(f'        "vel_ramp_rate": {odrv.axis1.controller.config.vel_ramp_rate},\n')
        f.write('    },\n')
        
        f.write('}\n\n')
        
        # Function to apply pre-calibrated values
        f.write('def apply_precalibrated_config(odrv):\n')
        f.write('    """Apply pre-calibrated configuration to the ODrive."""\n')
        f.write('    print("Applying pre-calibrated configuration...")\n')
        f.write('    \n')
        f.write('    # Axis 0\n')
        f.write('    # Motor configuration\n')
        f.write('    odrv.axis0.motor.config.phase_resistance = AXIS0_CONFIG["motor"]["phase_resistance"]\n')
        f.write('    odrv.axis0.motor.config.phase_inductance = AXIS0_CONFIG["motor"]["phase_inductance"]\n')
        f.write('    odrv.axis0.motor.config.pole_pairs = AXIS0_CONFIG["motor"]["pole_pairs"]\n')
        f.write('    odrv.axis0.motor.config.motor_type = AXIS0_CONFIG["motor"]["motor_type"]\n')
        f.write('    odrv.axis0.motor.config.current_lim = AXIS0_CONFIG["motor"]["current_lim"]\n')
        f.write('    odrv.axis0.motor.config.calibration_current = AXIS0_CONFIG["motor"]["calibration_current"]\n')
        f.write('    odrv.axis0.motor.config.resistance_calib_max_voltage = AXIS0_CONFIG["motor"]["resistance_calib_max_voltage"]\n')
        f.write('    \n')
        f.write('    # Encoder configuration\n')
        f.write('    odrv.axis0.encoder.config.mode = AXIS0_CONFIG["encoder"]["mode"]\n')
        f.write('    odrv.axis0.encoder.config.use_index = AXIS0_CONFIG["encoder"]["use_index"]\n')
        f.write('    odrv.axis0.encoder.config.cpr = AXIS0_CONFIG["encoder"]["cpr"]\n')
        f.write('    odrv.axis0.encoder.config.offset = AXIS0_CONFIG["encoder"]["offset"]\n')
        f.write('    odrv.axis0.encoder.config.offset_float = AXIS0_CONFIG["encoder"]["offset_float"]\n')
        f.write('    odrv.axis0.encoder.config.bandwidth = AXIS0_CONFIG["encoder"]["bandwidth"]\n')
        f.write('    odrv.axis0.encoder.config.calib_scan_distance = AXIS0_CONFIG["encoder"]["calib_scan_distance"]\n')
        f.write('    \n')
        f.write('    # Controller configuration\n')
        f.write('    odrv.axis0.controller.config.control_mode = AXIS0_CONFIG["controller"]["control_mode"]\n')
        f.write('    odrv.axis0.controller.config.pos_gain = AXIS0_CONFIG["controller"]["pos_gain"]\n')
        f.write('    odrv.axis0.controller.config.vel_gain = AXIS0_CONFIG["controller"]["vel_gain"]\n')
        f.write('    odrv.axis0.controller.config.vel_integrator_gain = AXIS0_CONFIG["controller"]["vel_integrator_gain"]\n')
        f.write('    odrv.axis0.controller.config.vel_limit = AXIS0_CONFIG["controller"]["vel_limit"]\n')
        f.write('    odrv.axis0.controller.config.vel_ramp_rate = AXIS0_CONFIG["controller"]["vel_ramp_rate"]\n')
        f.write('    \n')
        f.write('    # Axis 1\n')
        f.write('    # Motor configuration\n')
        f.write('    odrv.axis1.motor.config.phase_resistance = AXIS1_CONFIG["motor"]["phase_resistance"]\n')
        f.write('    odrv.axis1.motor.config.phase_inductance = AXIS1_CONFIG["motor"]["phase_inductance"]\n')
        f.write('    odrv.axis1.motor.config.pole_pairs = AXIS1_CONFIG["motor"]["pole_pairs"]\n')
        f.write('    odrv.axis1.motor.config.motor_type = AXIS1_CONFIG["motor"]["motor_type"]\n')
        f.write('    odrv.axis1.motor.config.current_lim = AXIS1_CONFIG["motor"]["current_lim"]\n')
        f.write('    odrv.axis1.motor.config.calibration_current = AXIS1_CONFIG["motor"]["calibration_current"]\n')
        f.write('    odrv.axis1.motor.config.resistance_calib_max_voltage = AXIS1_CONFIG["motor"]["resistance_calib_max_voltage"]\n')
        f.write('    \n')
        f.write('    # Encoder configuration\n')
        f.write('    odrv.axis1.encoder.config.mode = AXIS1_CONFIG["encoder"]["mode"]\n')
        f.write('    odrv.axis1.encoder.config.use_index = AXIS1_CONFIG["encoder"]["use_index"]\n')
        f.write('    odrv.axis1.encoder.config.cpr = AXIS1_CONFIG["encoder"]["cpr"]\n')
        f.write('    odrv.axis1.encoder.config.offset = AXIS1_CONFIG["encoder"]["offset"]\n')
        f.write('    odrv.axis1.encoder.config.offset_float = AXIS1_CONFIG["encoder"]["offset_float"]\n')
        f.write('    odrv.axis1.encoder.config.bandwidth = AXIS1_CONFIG["encoder"]["bandwidth"]\n')
        f.write('    odrv.axis1.encoder.config.calib_scan_distance = AXIS1_CONFIG["encoder"]["calib_scan_distance"]\n')
        f.write('    \n')
        f.write('    # Controller configuration\n')
        f.write('    odrv.axis1.controller.config.control_mode = AXIS1_CONFIG["controller"]["control_mode"]\n')
        f.write('    odrv.axis1.controller.config.pos_gain = AXIS1_CONFIG["controller"]["pos_gain"]\n')
        f.write('    odrv.axis1.controller.config.vel_gain = AXIS1_CONFIG["controller"]["vel_gain"]\n')
        f.write('    odrv.axis1.controller.config.vel_integrator_gain = AXIS1_CONFIG["controller"]["vel_integrator_gain"]\n')
        f.write('    odrv.axis1.controller.config.vel_limit = AXIS1_CONFIG["controller"]["vel_limit"]\n')
        f.write('    odrv.axis1.controller.config.vel_ramp_rate = AXIS1_CONFIG["controller"]["vel_ramp_rate"]\n')
        f.write('    \n')
        f.write('    # Set pre-calibrated flags\n')
        f.write('    odrv.axis0.motor.config.pre_calibrated = True\n')
        f.write('    odrv.axis0.encoder.config.pre_calibrated = True\n')
        f.write('    odrv.axis1.motor.config.pre_calibrated = True\n')
        f.write('    odrv.axis1.encoder.config.pre_calibrated = True\n')
        f.write('    \n')
        f.write('    print("Pre-calibrated configuration applied.")\n')
        f.write('    \n')
        f.write('    # Save configuration\n')
        f.write('    print("Saving configuration...")\n')
        f.write('    odrv.save_configuration()\n')
        f.write('    print("Configuration saved.")\n')
        f.write('    \n')
        f.write('    return True\n')
    
    print(f"Pre-calibrated configuration module generated: {output_file}")
    print("You can now import this module in motor_control.py to use these values.")

def main():
    """Main function."""
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Generate pre-calibrated module
    generate_precalibrated_module(odrv)

if __name__ == "__main__":
    main()
