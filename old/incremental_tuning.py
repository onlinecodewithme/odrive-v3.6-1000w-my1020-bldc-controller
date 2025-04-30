#!/usr/bin/env python3
"""
Incremental ODrive tuning script.
This script makes one configuration change at a time and tests after each change
to identify which changes improve response time without causing errors.
"""
import odrive
import time
import json
import sys
import os

def connect_to_odrive():
    """Connect to the ODrive."""
    print("Looking for ODrive...")
    try:
        odrv = odrive.find_any()
        print(f"Found ODrive: {str(odrv.serial_number)}")
        return odrv
    except:
        print("Failed to find ODrive. Make sure it's connected and powered on.")
        sys.exit(1)

def wait_for_odrive(timeout=30):
    """Wait for ODrive to come back online after reboot."""
    print("Waiting for ODrive to reboot...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            odrv = odrive.find_any(timeout=1)
            print(f"ODrive reconnected: {str(odrv.serial_number)}")
            return odrv
        except:
            print(".", end="", flush=True)
            time.sleep(1)
    
    print("\nTimeout waiting for ODrive to reconnect.")
    sys.exit(1)

def decode_axis_error(error_code):
    """Decode axis error code into human-readable format."""
    error_descriptions = {
        0x00000001: "INVALID_STATE",
        0x00000002: "DC_BUS_UNDER_VOLTAGE",
        0x00000004: "DC_BUS_OVER_VOLTAGE",
        0x00000008: "CURRENT_MEASUREMENT_TIMEOUT",
        0x00000010: "BRAKE_RESISTOR_DISARMED",
        0x00000020: "MOTOR_DISARMED",
        0x00000040: "MOTOR_FAILED",
        0x00000080: "SENSORLESS_ESTIMATOR_FAILED",
        0x00000100: "ENCODER_FAILED",
        0x00000200: "CONTROLLER_FAILED",
        0x00000400: "POS_CTRL_DURING_SENSORLESS",
        0x00000800: "WATCHDOG_TIMER_EXPIRED",
        0x00001000: "MIN_ENDSTOP_PRESSED",
        0x00002000: "MAX_ENDSTOP_PRESSED",
        0x00004000: "ESTOP_REQUESTED",
        0x00008000: "HOMING_WITHOUT_ENDSTOP",
        0x00010000: "OVER_TEMP",
        0x00020000: "UNKNOWN_POSITION",
        0x00040000: "FAN_FAILED"
    }
    
    error_messages = []
    for bit, description in error_descriptions.items():
        if error_code & bit:
            error_messages.append(description)
    
    return error_messages if error_messages else ["UNKNOWN_ERROR"]

def clear_errors(odrv):
    """Clear all errors on the ODrive."""
    print("\nClearing all errors...")
    
    # Clear errors on axis 0
    if odrv.axis0.error != 0:
        error_codes = decode_axis_error(odrv.axis0.error)
        print(f"Clearing axis error: {odrv.axis0.error} ({', '.join(error_codes)})")
        odrv.axis0.error = 0
    
    # Clear motor errors
    if odrv.axis0.motor.error != 0:
        print(f"Clearing motor error: {odrv.axis0.motor.error}")
        odrv.axis0.motor.error = 0
    
    # Clear encoder errors
    if odrv.axis0.encoder.error != 0:
        print(f"Clearing encoder error: {odrv.axis0.encoder.error}")
        odrv.axis0.encoder.error = 0
    
    # Clear controller errors
    if odrv.axis0.controller.error != 0:
        print(f"Clearing controller error: {odrv.axis0.controller.error}")
        odrv.axis0.controller.error = 0
    
    # Clear sensorless estimator errors
    if odrv.axis0.sensorless_estimator.error != 0:
        print(f"Clearing sensorless estimator error: {odrv.axis0.sensorless_estimator.error}")
        odrv.axis0.sensorless_estimator.error = 0
    
    print("All errors cleared.")

def restore_original_config(odrv, backup_file):
    """Restore the original configuration from backup."""
    print(f"\nRestoring original configuration from {backup_file}...")
    
    try:
        with open(backup_file, 'r') as f:
            backup_config = json.load(f)
    except Exception as e:
        print(f"Error loading backup file: {e}")
        return False
    
    # Restore key parameters
    try:
        # Controller parameters
        odrv.axis0.controller.config.input_filter_bandwidth = backup_config.get("axis0.controller.config.input_filter_bandwidth", 2.0)
        odrv.axis0.controller.config.vel_ramp_rate = backup_config.get("axis0.controller.config.vel_ramp_rate", 1.0)
        odrv.axis0.controller.config.vel_gain = backup_config.get("axis0.controller.config.vel_gain", 0.2)
        odrv.axis0.controller.config.vel_integrator_gain = backup_config.get("axis0.controller.config.vel_integrator_gain", 0.1)
        odrv.axis0.controller.config.control_mode = backup_config.get("axis0.controller.config.control_mode", 2)
        odrv.axis0.controller.config.input_mode = backup_config.get("axis0.controller.config.input_mode", 1)
        
        # Encoder parameters
        odrv.axis0.encoder.config.mode = backup_config.get("axis0.encoder.config.mode", 0)
        odrv.axis0.encoder.config.cpr = backup_config.get("axis0.encoder.config.cpr", 4000)
        odrv.axis0.encoder.config.bandwidth = backup_config.get("axis0.encoder.config.bandwidth", 1000.0)
        odrv.axis0.encoder.config.calib_range = backup_config.get("axis0.encoder.config.calib_range", 0.05)
        odrv.axis0.encoder.config.calib_scan_distance = backup_config.get("axis0.encoder.config.calib_scan_distance", 150.0)
        odrv.axis0.encoder.config.calib_scan_omega = backup_config.get("axis0.encoder.config.calib_scan_omega", 12.566)
        odrv.axis0.encoder.config.use_index = backup_config.get("axis0.encoder.config.use_index", False)
        odrv.axis0.encoder.config.pre_calibrated = backup_config.get("axis0.encoder.config.pre_calibrated", False)
        
        # Motor parameters
        odrv.axis0.motor.config.current_lim = backup_config.get("axis0.motor.config.current_lim", 40.0)
        odrv.axis0.motor.config.calibration_current = backup_config.get("axis0.motor.config.calibration_current", 20.0)
        odrv.axis0.motor.config.current_control_bandwidth = backup_config.get("axis0.motor.config.current_control_bandwidth", 1000.0)
        
        # Axis parameters
        odrv.axis0.config.startup_closed_loop_control = backup_config.get("axis0.config.startup_closed_loop_control", False)
        
        print("Original configuration restored.")
        return True
    except Exception as e:
        print(f"Error restoring configuration: {e}")
        return False

def test_velocity_response(odrv, velocity=2.0, timeout=5.0):
    """Test the motor's response to a velocity command."""
    print(f"\nTesting velocity response with velocity={velocity}...")
    
    # Make sure we're in idle state first
    print("Setting to idle state...")
    odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
    time.sleep(1)
    
    # Clear any errors
    clear_errors(odrv)
    
    # Enter closed loop control
    print("Entering closed loop control...")
    odrv.axis0.requested_state = 8  # AXIS_STATE_CLOSED_LOOP_CONTROL
    time.sleep(1)
    
    # Check if we successfully entered closed loop control
    if odrv.axis0.current_state != 8:
        print(f"Failed to enter closed loop control. Current state: {odrv.axis0.current_state}")
        if odrv.axis0.error != 0:
            error_codes = decode_axis_error(odrv.axis0.error)
            print(f"Axis error: {odrv.axis0.error} ({', '.join(error_codes)})")
        return None, None
    
    # Send velocity command and measure response time
    print(f"Setting velocity to {velocity}...")
    start_time = time.time()
    odrv.axis0.controller.input_vel = velocity
    
    # Wait for motor to start moving
    vel_threshold = velocity * 0.05  # 5% of target velocity
    response_time = None
    max_velocity = 0.0
    
    # Monitor for timeout seconds
    while time.time() - start_time < timeout:
        current_vel = abs(odrv.axis0.encoder.vel_estimate)
        
        # Update max velocity
        if current_vel > max_velocity:
            max_velocity = current_vel
        
        # Check if we've reached threshold
        if response_time is None and current_vel >= vel_threshold:
            response_time = time.time() - start_time
            print(f"Response time: {response_time:.3f} seconds")
        
        time.sleep(0.001)  # Sample at 1000Hz for more accurate timing
    
    # If we never reached the threshold
    if response_time is None:
        response_time = float('inf')
        print("Motor did not reach threshold velocity within timeout period.")
    
    print(f"Maximum velocity reached: {max_velocity:.2f}")
    
    # Stop the motor
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    # Return to idle state
    print("Returning to idle state...")
    odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
    time.sleep(1)
    
    return response_time, max_velocity

def save_configuration(odrv):
    """Save the configuration and wait for reboot."""
    print("\nSaving configuration...")
    try:
        odrv.save_configuration()
        print("Configuration saved. ODrive will reboot.")
    except Exception as e:
        print(f"Exception during save: {e}")
        print("ODrive disconnected during save as expected.")
    
    # Wait for ODrive to come back online
    return wait_for_odrive()

def test_parameter_change(odrv, param_name, param_path, original_value, new_value, test_velocity=2.0):
    """Test a single parameter change and its effect on response time."""
    print(f"\n=== Testing parameter: {param_name} ===")
    print(f"Original value: {original_value}")
    print(f"New value: {new_value}")
    
    # Set the parameter to the new value
    exec(f"odrv.{param_path} = {new_value}")
    
    # Save configuration
    odrv = save_configuration(odrv)
    
    # Test velocity response
    response_time, max_velocity = test_velocity_response(odrv, test_velocity)
    
    # Record the result
    result = {
        "param_name": param_name,
        "param_path": param_path,
        "original_value": original_value,
        "new_value": new_value,
        "response_time": response_time,
        "max_velocity": max_velocity,
        "success": response_time != float('inf') and response_time < 1.0  # Consider success if response time is less than 1 second
    }
    
    # Print the result
    print(f"\nResult for {param_name}:")
    print(f"  Response time: {response_time if response_time != float('inf') else 'No response'}")
    print(f"  Max velocity: {max_velocity}")
    print(f"  Success: {'Yes' if result['success'] else 'No'}")
    
    # Reset to original value if the change didn't improve response time
    if not result['success']:
        print(f"Resetting {param_name} to original value: {original_value}")
        exec(f"odrv.{param_path} = {original_value}")
        odrv = save_configuration(odrv)
    
    return result, odrv

def find_latest_backup():
    """Find the latest backup file in the current directory."""
    backup_files = [f for f in os.listdir('.') if f.startswith('odrive_backup_') and f.endswith('.json')]
    if not backup_files:
        return None
    return sorted(backup_files)[-1]  # Return the latest backup file

def run_incremental_tuning():
    """Run the incremental tuning process."""
    print("=== ODrive Incremental Tuning ===")
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Find the latest backup file
    backup_file = find_latest_backup()
    if not backup_file:
        print("No backup file found. Please run backup_odrive_config.py first.")
        sys.exit(1)
    
    print(f"Using backup file: {backup_file}")
    
    # Restore original configuration
    if not restore_original_config(odrv, backup_file):
        print("Failed to restore original configuration. Exiting.")
        sys.exit(1)
    
    # Save the restored configuration
    odrv = save_configuration(odrv)
    
    # Clear any errors
    clear_errors(odrv)
    
    # Test baseline response time with original configuration
    print("\n=== Testing baseline response time with original configuration ===")
    baseline_response_time, baseline_max_velocity = test_velocity_response(odrv, 2.0)
    
    print(f"\nBaseline response time: {baseline_response_time if baseline_response_time != float('inf') else 'No response'}")
    print(f"Baseline max velocity: {baseline_max_velocity}")
    
    # Define parameters to test
    parameters = [
        {
            "name": "Input Filter Bandwidth",
            "path": "axis0.controller.config.input_filter_bandwidth",
            "original": odrv.axis0.controller.config.input_filter_bandwidth,
            "new": 20.0
        },
        {
            "name": "Velocity Ramp Rate",
            "path": "axis0.controller.config.vel_ramp_rate",
            "original": odrv.axis0.controller.config.vel_ramp_rate,
            "new": 10.0
        },
        {
            "name": "Velocity Gain",
            "path": "axis0.controller.config.vel_gain",
            "original": odrv.axis0.controller.config.vel_gain,
            "new": 0.25
        },
        {
            "name": "Startup Closed Loop Control",
            "path": "axis0.config.startup_closed_loop_control",
            "original": odrv.axis0.config.startup_closed_loop_control,
            "new": True
        },
        {
            "name": "Current Control Bandwidth",
            "path": "axis0.motor.config.current_control_bandwidth",
            "original": odrv.axis0.motor.config.current_control_bandwidth,
            "new": 1000.0
        }
    ]
    
    # Test each parameter change
    results = []
    for param in parameters:
        result, odrv = test_parameter_change(
            odrv, 
            param["name"], 
            param["path"], 
            param["original"], 
            param["new"]
        )
        results.append(result)
    
    # Print summary of results
    print("\n=== Incremental Tuning Results ===")
    print("Parameter | Original Value | New Value | Response Time | Success")
    print("---------|----------------|-----------|---------------|--------")
    
    for result in results:
        success_str = "✓" if result["success"] else "✗"
        response_time_str = f"{result['response_time']:.3f}s" if result['response_time'] != float('inf') else "No response"
        print(f"{result['param_name']} | {result['original_value']} | {result['new_value']} | {response_time_str} | {success_str}")
    
    # Apply all successful changes together
    print("\n=== Applying all successful changes together ===")
    successful_changes = [r for r in results if r["success"]]
    
    if not successful_changes:
        print("No successful parameter changes found.")
    else:
        print("Applying the following successful changes:")
        for change in successful_changes:
            print(f"  {change['param_name']}: {change['original_value']} → {change['new_value']}")
            exec(f"odrv.{change['param_path']} = {change['new_value']}")
        
        # Save the final configuration
        odrv = save_configuration(odrv)
        
        # Test the final configuration
        print("\n=== Testing final configuration with all successful changes ===")
        final_response_time, final_max_velocity = test_velocity_response(odrv, 2.0)
        
        print(f"\nFinal response time: {final_response_time if final_response_time != float('inf') else 'No response'}")
        print(f"Final max velocity: {final_max_velocity}")
        
        if final_response_time != float('inf'):
            improvement = (baseline_response_time - final_response_time) / baseline_response_time * 100
            print(f"Improvement: {improvement:.2f}%")
    
    print("\nIncremental tuning complete.")
    print("You can now use the ODrive with the optimized configuration.")

if __name__ == "__main__":
    run_incremental_tuning()
