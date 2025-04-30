#!/usr/bin/env python3
"""
ODrive Calibration Loader.
This script loads pre-calibrated values from a file and applies them to the ODrive.
This allows "calibration" without moving the robot in production environments.
"""
import odrive
import time
import sys
import json
import os
import argparse

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

def save_calibration_values(odrv, filename):
    """
    Save current calibration values to a file.
    This should be done after a successful calibration in a controlled environment.
    """
    print(f"Saving calibration values to {filename}...")
    
    # Create calibration data structure
    calibration_data = {
        "serial_number": str(odrv.serial_number),
        "axis0": {
            "motor": {
                "phase_resistance": odrv.axis0.motor.config.phase_resistance,
                "phase_inductance": odrv.axis0.motor.config.phase_inductance,
                "pole_pairs": odrv.axis0.motor.config.pole_pairs,
                "direction": odrv.axis0.motor.config.direction,
                "motor_type": odrv.axis0.motor.config.motor_type,
                "current_lim": odrv.axis0.motor.config.current_lim,
                "calibration_current": odrv.axis0.motor.config.calibration_current,
                "resistance_calib_max_voltage": odrv.axis0.motor.config.resistance_calib_max_voltage,
            },
            "encoder": {
                "mode": odrv.axis0.encoder.config.mode,
                "use_index": odrv.axis0.encoder.config.use_index,
                "cpr": odrv.axis0.encoder.config.cpr,
                "offset": odrv.axis0.encoder.config.offset,
                "offset_float": odrv.axis0.encoder.config.offset_float,
                "bandwidth": odrv.axis0.encoder.config.bandwidth,
                "calib_scan_distance": odrv.axis0.encoder.config.calib_scan_distance,
            },
            "controller": {
                "control_mode": odrv.axis0.controller.config.control_mode,
                "pos_gain": odrv.axis0.controller.config.pos_gain,
                "vel_gain": odrv.axis0.controller.config.vel_gain,
                "vel_integrator_gain": odrv.axis0.controller.config.vel_integrator_gain,
                "vel_limit": odrv.axis0.controller.config.vel_limit,
                "vel_ramp_rate": odrv.axis0.controller.config.vel_ramp_rate,
            }
        },
        "axis1": {
            "motor": {
                "phase_resistance": odrv.axis1.motor.config.phase_resistance,
                "phase_inductance": odrv.axis1.motor.config.phase_inductance,
                "pole_pairs": odrv.axis1.motor.config.pole_pairs,
                "direction": odrv.axis1.motor.config.direction,
                "motor_type": odrv.axis1.motor.config.motor_type,
                "current_lim": odrv.axis1.motor.config.current_lim,
                "calibration_current": odrv.axis1.motor.config.calibration_current,
                "resistance_calib_max_voltage": odrv.axis1.motor.config.resistance_calib_max_voltage,
            },
            "encoder": {
                "mode": odrv.axis1.encoder.config.mode,
                "use_index": odrv.axis1.encoder.config.use_index,
                "cpr": odrv.axis1.encoder.config.cpr,
                "offset": odrv.axis1.encoder.config.offset,
                "offset_float": odrv.axis1.encoder.config.offset_float,
                "bandwidth": odrv.axis1.encoder.config.bandwidth,
                "calib_scan_distance": odrv.axis1.encoder.config.calib_scan_distance,
            },
            "controller": {
                "control_mode": odrv.axis1.controller.config.control_mode,
                "pos_gain": odrv.axis1.controller.config.pos_gain,
                "vel_gain": odrv.axis1.controller.config.vel_gain,
                "vel_integrator_gain": odrv.axis1.controller.config.vel_integrator_gain,
                "vel_limit": odrv.axis1.controller.config.vel_limit,
                "vel_ramp_rate": odrv.axis1.controller.config.vel_ramp_rate,
            }
        }
    }
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(calibration_data, f, indent=4)
    
    print(f"Calibration values saved to {filename}")

def load_calibration_values(odrv, filename, axis_num=None):
    """
    Load calibration values from a file and apply them to the ODrive.
    This allows "calibration" without moving the robot.
    """
    print(f"Loading calibration values from {filename}...")
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: Calibration file {filename} not found.")
        return False
    
    # Load calibration data
    try:
        with open(filename, 'r') as f:
            calibration_data = json.load(f)
    except Exception as e:
        print(f"Error loading calibration file: {e}")
        return False
    
    # Check serial number
    if str(odrv.serial_number) != calibration_data.get("serial_number"):
        print("Warning: Serial number mismatch between ODrive and calibration file.")
        print(f"ODrive: {odrv.serial_number}, Calibration file: {calibration_data.get('serial_number')}")
        confirmation = input("Continue anyway? (y/n): ").strip().lower()
        if confirmation != 'y':
            print("Calibration loading aborted.")
            return False
    
    # Apply calibration values
    axes = []
    if axis_num is None:
        axes = [(0, odrv.axis0, calibration_data["axis0"]), 
                (1, odrv.axis1, calibration_data["axis1"])]
    elif axis_num == 0:
        axes = [(0, odrv.axis0, calibration_data["axis0"])]
    elif axis_num == 1:
        axes = [(1, odrv.axis1, calibration_data["axis1"])]
    
    for i, axis, axis_data in axes:
        print(f"Applying calibration values to axis{i}...")
        
        # Set motor to idle state
        axis.requested_state = 1  # AXIS_STATE_IDLE
        time.sleep(0.5)
        
        # Apply motor calibration values
        motor_data = axis_data["motor"]
        axis.motor.config.phase_resistance = motor_data["phase_resistance"]
        axis.motor.config.phase_inductance = motor_data["phase_inductance"]
        axis.motor.config.pole_pairs = motor_data["pole_pairs"]
        axis.motor.config.direction = motor_data["direction"]
        axis.motor.config.motor_type = motor_data["motor_type"]
        axis.motor.config.current_lim = motor_data["current_lim"]
        axis.motor.config.calibration_current = motor_data["calibration_current"]
        axis.motor.config.resistance_calib_max_voltage = motor_data["resistance_calib_max_voltage"]
        
        # Apply encoder calibration values
        encoder_data = axis_data["encoder"]
        axis.encoder.config.mode = encoder_data["mode"]
        axis.encoder.config.use_index = encoder_data["use_index"]
        axis.encoder.config.cpr = encoder_data["cpr"]
        axis.encoder.config.offset = encoder_data["offset"]
        axis.encoder.config.offset_float = encoder_data["offset_float"]
        axis.encoder.config.bandwidth = encoder_data["bandwidth"]
        axis.encoder.config.calib_scan_distance = encoder_data["calib_scan_distance"]
        
        # Apply controller calibration values
        controller_data = axis_data["controller"]
        axis.controller.config.control_mode = controller_data["control_mode"]
        axis.controller.config.pos_gain = controller_data["pos_gain"]
        axis.controller.config.vel_gain = controller_data["vel_gain"]
        axis.controller.config.vel_integrator_gain = controller_data["vel_integrator_gain"]
        axis.controller.config.vel_limit = controller_data["vel_limit"]
        axis.controller.config.vel_ramp_rate = controller_data["vel_ramp_rate"]
        
        # Set pre-calibrated flags
        axis.motor.config.pre_calibrated = True
        axis.encoder.config.pre_calibrated = True
    
    # Save configuration
    print("Saving configuration...")
    try:
        odrv.save_configuration()
        print("Configuration saved. ODrive will reboot.")
        # Wait for ODrive to come back online
        wait_for_odrive()
    except Exception as e:
        print(f"Exception during save: {e}")
        print("ODrive disconnected during save as expected.")
        # Wait for ODrive to come back online
        wait_for_odrive()
    
    print("Calibration values loaded successfully.")
    return True

def wait_for_odrive():
    """Wait for ODrive to come back online after reboot."""
    print("Waiting for ODrive to come back online...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            time.sleep(1.0)
            odrv = odrive.find_any()
            print(f"Reconnected to ODrive: {str(odrv.serial_number)}")
            return odrv
        except:
            print(".", end="", flush=True)
    
    print("\nFailed to reconnect to ODrive after multiple attempts.")
    print("Please check the connection and restart the program.")
    sys.exit(1)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="ODrive Calibration Loader")
    parser.add_argument("action", choices=["save", "load"], help="Action to perform")
    parser.add_argument("--file", default="odrive_calibration.json", help="Calibration file")
    parser.add_argument("--axis", type=int, choices=[0, 1], help="Specify which axis to operate on (0 or 1)")
    
    args = parser.parse_args()
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Execute command
    if args.action == "save":
        save_calibration_values(odrv, args.file)
    elif args.action == "load":
        load_calibration_values(odrv, args.file, args.axis)

if __name__ == "__main__":
    main()
