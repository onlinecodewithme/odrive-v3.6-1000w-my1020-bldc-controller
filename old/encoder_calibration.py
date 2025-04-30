#!/usr/bin/env python3
"""
ODrive encoder calibration script.
This script focuses specifically on properly calibrating the encoder
and ensuring it's ready for closed loop control.
"""
import odrive
import time
import sys

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

def decode_encoder_error(error_code):
    """Decode encoder error code into human-readable format."""
    error_descriptions = {
        0x00000001: "UNSTABLE_GAIN",
        0x00000002: "CPR_POLEPAIRS_MISMATCH",
        0x00000004: "NO_RESPONSE",
        0x00000008: "UNSUPPORTED_ENCODER_MODE",
        0x00000010: "ILLEGAL_HALL_STATE",
        0x00000020: "INDEX_NOT_FOUND_YET",
        0x00000040: "ABS_SPI_TIMEOUT",
        0x00000080: "ABS_SPI_COM_FAIL",
        0x00000100: "ABS_SPI_NOT_READY",
        0x00000200: "HALL_NOT_CALIBRATED_YET"
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
        error_codes = decode_encoder_error(odrv.axis0.encoder.error)
        print(f"Clearing encoder error: {odrv.axis0.encoder.error} ({', '.join(error_codes)})")
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

def check_encoder_config(odrv):
    """Check and print encoder configuration."""
    print("\nEncoder Configuration:")
    print(f"Mode: {odrv.axis0.encoder.config.mode}")
    print(f"CPR (Counts Per Revolution): {odrv.axis0.encoder.config.cpr}")
    print(f"Bandwidth: {odrv.axis0.encoder.config.bandwidth} Hz")
    print(f"Calib range: {odrv.axis0.encoder.config.calib_range}")
    print(f"Calib scan distance: {odrv.axis0.encoder.config.calib_scan_distance}")
    print(f"Calib scan omega: {odrv.axis0.encoder.config.calib_scan_omega}")
    print(f"Use index: {odrv.axis0.encoder.config.use_index}")
    print(f"Pre-calibrated: {odrv.axis0.encoder.config.pre_calibrated}")
    
    # Print additional attributes if they exist
    try:
        print(f"Ignore illegal hall state: {odrv.axis0.encoder.config.ignore_illegal_hall_state}")
    except AttributeError:
        pass
    
    print("\nEncoder Status:")
    print(f"Is ready: {odrv.axis0.encoder.is_ready}")
    print(f"Index found: {odrv.axis0.encoder.index_found}")
    print(f"Shadow count: {odrv.axis0.encoder.shadow_count}")
    print(f"Count in CPR: {odrv.axis0.encoder.count_in_cpr}")
    
    # Try to print offset values if they exist
    try:
        print(f"Offset float: {odrv.axis0.encoder.config.offset_float}")
    except AttributeError:
        pass
    
    print(f"Encoder error: {odrv.axis0.encoder.error}")
    
    if odrv.axis0.encoder.error != 0:
        error_codes = decode_encoder_error(odrv.axis0.encoder.error)
        print(f"Encoder error details: {', '.join(error_codes)}")

def optimize_encoder_config(odrv):
    """Optimize encoder configuration for better performance."""
    print("\nOptimizing encoder configuration...")
    
    # Set encoder mode to INCREMENTAL (0) for 1000PPR rotary encoder
    odrv.axis0.encoder.config.mode = 0  # MODE_INCREMENTAL
    
    # Set CPR to 1000 for 1000PPR encoder
    odrv.axis0.encoder.config.cpr = 1000
    
    # Increase bandwidth for faster response
    odrv.axis0.encoder.config.bandwidth = 2000.0
    
    # Optimize calibration parameters
    odrv.axis0.encoder.config.calib_range = 0.05  # Smaller range for more precise calibration
    odrv.axis0.encoder.config.calib_scan_distance = 50.0  # Longer scan distance
    odrv.axis0.encoder.config.calib_scan_omega = 12.0  # Faster scan speed
    
    # Save configuration
    print("Saving encoder configuration...")
    try:
        odrv.save_configuration()
        print("Configuration saved. ODrive will reboot.")
    except Exception as e:
        print(f"Exception during save: {e}")
        print("ODrive disconnected during save as expected.")
    
    # Wait for ODrive to come back online
    odrv = wait_for_odrive()
    
    return odrv

def calibrate_encoder(odrv):
    """Perform encoder calibration."""
    print("\nStarting encoder calibration...")
    
    # First, make sure we're in idle state
    print("Setting ODrive to idle state...")
    odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
    time.sleep(1.0)
    
    # Clear any errors
    clear_errors(odrv)
    
    # Start encoder offset calibration
    print("Starting encoder offset calibration...")
    odrv.axis0.requested_state = 7  # AXIS_STATE_ENCODER_OFFSET_CALIBRATION
    
    # Wait for calibration to complete (with timeout)
    print("Waiting for encoder calibration to complete (this may take 5-10 seconds)...")
    start_time = time.time()
    timeout = 30.0  # 30 seconds timeout for encoder calibration
    
    while odrv.axis0.current_state != 1:  # AXIS_STATE_IDLE
        time.sleep(0.5)
        print(".", end="", flush=True)
        
        # Check for errors
        if odrv.axis0.encoder.error != 0:
            error_codes = decode_encoder_error(odrv.axis0.encoder.error)
            print(f"\nEncoder calibration failed with errors: {', '.join(error_codes)}")
            return False
        
        # Check for timeout
        if time.time() - start_time > timeout:
            print("\nEncoder calibration timed out after 30 seconds.")
            return False
    
    print("\nEncoder calibration completed.")
    
    # Check if encoder is now ready
    if odrv.axis0.encoder.is_ready:
        print("Encoder is now ready!")
        
        # Save the calibration results
        print("Saving calibration results...")
        try:
            odrv.axis0.encoder.config.pre_calibrated = True
            odrv.save_configuration()
            print("Calibration saved. ODrive will reboot.")
        except Exception as e:
            print(f"Exception during save: {e}")
            print("ODrive disconnected during save as expected.")
        
        # Wait for ODrive to come back online
        odrv = wait_for_odrive()
        
        return True
    else:
        print("Encoder is still not ready after calibration.")
        return False

def enter_closed_loop_control(odrv):
    """Attempt to enter closed loop control mode."""
    print("\nAttempting to enter closed loop control mode...")
    
    # Clear any errors first
    clear_errors(odrv)
    
    # Set control mode to velocity control
    print("Setting control mode to velocity control...")
    odrv.axis0.controller.config.control_mode = 2  # CONTROL_MODE_VELOCITY_CONTROL
    
    # Set input mode to velocity
    odrv.axis0.controller.config.input_mode = 1  # INPUT_MODE_PASSTHROUGH
    
    # Make sure we're in idle state first
    print("Setting to idle state first...")
    odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
    time.sleep(1)
    
    # Clear errors again
    clear_errors(odrv)
    
    # Enter closed loop control
    print("Entering closed loop control...")
    odrv.axis0.requested_state = 8  # AXIS_STATE_CLOSED_LOOP_CONTROL
    
    # Wait for transition to complete
    time.sleep(1)
    
    # Check if we successfully entered closed loop control
    if odrv.axis0.current_state != 8:
        print(f"Failed to enter closed loop control. Current state: {odrv.axis0.current_state}")
        if odrv.axis0.error != 0:
            error_codes = decode_axis_error(odrv.axis0.error)
            print(f"Axis error: {odrv.axis0.error} ({', '.join(error_codes)})")
        return False
    
    print("Successfully entered closed loop control mode.")
    return True

def test_velocity_command(odrv, velocity=5.0):
    """Test a single velocity command."""
    print(f"\nTesting velocity command: {velocity}...")
    
    # Make sure we're in closed loop control
    if odrv.axis0.current_state != 8:
        print("Not in closed loop control. Cannot test velocity command.")
        return False
    
    # Send velocity command
    print(f"Setting velocity to {velocity}...")
    odrv.axis0.controller.input_vel = velocity
    
    # Monitor for 2 seconds
    start_time = time.time()
    max_velocity = 0.0
    
    print("Monitoring velocity for 2 seconds...")
    while time.time() - start_time < 2.0:
        current_vel = abs(odrv.axis0.encoder.vel_estimate)
        max_velocity = max(max_velocity, current_vel)
        time.sleep(0.1)
    
    print(f"Maximum velocity reached: {max_velocity:.2f}")
    
    # Stop the motor
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    return max_velocity > 0.5 * velocity  # Consider success if we reach at least 50% of target

if __name__ == "__main__":
    print("=== ODrive Encoder Calibration ===")
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Check initial encoder configuration
    check_encoder_config(odrv)
    
    # Clear all errors
    clear_errors(odrv)
    
    # Optimize encoder configuration
    odrv = optimize_encoder_config(odrv)
    
    # Calibrate encoder
    success = calibrate_encoder(odrv)
    if not success:
        print("Encoder calibration failed. Exiting.")
        sys.exit(1)
    
    # Check encoder configuration after calibration
    check_encoder_config(odrv)
    
    # Try to enter closed loop control
    success = enter_closed_loop_control(odrv)
    if not success:
        print("Failed to enter closed loop control. Exiting.")
        sys.exit(1)
    
    # Test a velocity command
    success = test_velocity_command(odrv, 5.0)
    if not success:
        print("Velocity command test failed.")
    else:
        print("Velocity command test succeeded!")
    
    print("\nEncoder calibration complete.")
    print("You should now be able to control the motor with velocity commands.")
    print("Example: odrv0.axis0.controller.input_vel = 5.0")
