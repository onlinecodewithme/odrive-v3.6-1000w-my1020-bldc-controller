#!/usr/bin/env python3
"""
Script to fix the MOTOR_FAILED error (axis error 64) on ODrive.
This script focuses on proper motor and encoder calibration.
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

def decode_motor_error(error_code):
    """Decode motor error code into human-readable format."""
    error_descriptions = {
        0x00000001: "PHASE_RESISTANCE_OUT_OF_RANGE",
        0x00000002: "PHASE_INDUCTANCE_OUT_OF_RANGE",
        0x00000004: "DRV_FAULT",
        0x00000008: "CONTROL_DEADLINE_MISSED",
        0x00000010: "MODULATION_MAGNITUDE",
        0x00000020: "CURRENT_SENSE_SATURATION",
        0x00000040: "CURRENT_LIMIT_VIOLATION",
        0x00000080: "MODULATION_IS_NAN",
        0x00000100: "MOTOR_THERMISTOR_OVER_TEMP",
        0x00000200: "FET_THERMISTOR_OVER_TEMP",
        0x00000400: "TIMER_UPDATE_MISSED",
        0x00000800: "CURRENT_MEASUREMENT_UNAVAILABLE",
        0x00001000: "CONTROLLER_FAILED",
        0x00002000: "I_BUS_OUT_OF_RANGE",
        0x00004000: "BRAKE_RESISTOR_DISARMED",
        0x00008000: "SYSTEM_LEVEL",
        0x00010000: "BAD_TIMING",
        0x00020000: "UNKNOWN_PHASE_ESTIMATE",
        0x00040000: "UNKNOWN_PHASE_VEL",
        0x00080000: "UNKNOWN_TORQUE",
        0x00100000: "UNKNOWN_CURRENT_COMMAND",
        0x00200000: "UNKNOWN_CURRENT_MEASUREMENT",
        0x00400000: "UNKNOWN_VBUS_VOLTAGE",
        0x00800000: "UNKNOWN_VOLTAGE_COMMAND",
        0x01000000: "UNKNOWN_GAINS",
        0x02000000: "CONTROLLER_INITIALIZING",
        0x04000000: "UNBALANCED_PHASES",
        0x10000000: "MOTOR_UNSPECIFIED",
        0x20000000: "MOTOR_UNINITIALIZED",
        0x40000000: "MOTOR_UNINITIALIZED_CONFIGS"
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
        error_codes = decode_motor_error(odrv.axis0.motor.error)
        print(f"Clearing motor error: {odrv.axis0.motor.error} ({', '.join(error_codes)})")
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

def check_status(odrv):
    """Check and print the current status of the ODrive."""
    print("\n=== ODrive Status ===")
    print(f"Axis state: {odrv.axis0.current_state}")
    print(f"Motor is calibrated: {odrv.axis0.motor.is_calibrated}")
    print(f"Encoder is ready: {odrv.axis0.encoder.is_ready}")
    
    if odrv.axis0.error != 0:
        error_codes = decode_axis_error(odrv.axis0.error)
        print(f"Axis error: {odrv.axis0.error} ({', '.join(error_codes)})")
    
    if odrv.axis0.motor.error != 0:
        error_codes = decode_motor_error(odrv.axis0.motor.error)
        print(f"Motor error: {odrv.axis0.motor.error} ({', '.join(error_codes)})")
    
    if odrv.axis0.encoder.error != 0:
        print(f"Encoder error: {odrv.axis0.encoder.error}")
    
    if odrv.axis0.controller.error != 0:
        print(f"Controller error: {odrv.axis0.controller.error}")

def reset_configuration(odrv):
    """Reset the ODrive configuration to default values."""
    print("\nResetting ODrive configuration to default values...")
    
    # Reset motor configuration
    odrv.axis0.motor.config.pre_calibrated = False
    odrv.axis0.motor.config.pole_pairs = 7  # Default for most BLDC motors
    odrv.axis0.motor.config.calibration_current = 10.0  # Lower calibration current
    odrv.axis0.motor.config.resistance_calib_max_voltage = 4.0
    odrv.axis0.motor.config.current_control_bandwidth = 1000.0
    
    # Reset encoder configuration
    odrv.axis0.encoder.config.mode = 0  # MODE_INCREMENTAL
    odrv.axis0.encoder.config.cpr = 1000  # 1000 PPR as specified
    odrv.axis0.encoder.config.pre_calibrated = False
    odrv.axis0.encoder.config.bandwidth = 1000.0
    
    # Reset controller configuration
    odrv.axis0.controller.config.control_mode = 2  # CONTROL_MODE_VELOCITY_CONTROL
    odrv.axis0.controller.config.input_mode = 1  # INPUT_MODE_PASSTHROUGH
    odrv.axis0.controller.config.vel_gain = 0.2
    odrv.axis0.controller.config.vel_integrator_gain = 0.1
    odrv.axis0.controller.config.vel_limit = 10.0
    odrv.axis0.controller.config.vel_ramp_rate = 1.0
    
    # Save configuration
    print("Saving configuration...")
    try:
        odrv.save_configuration()
        print("Configuration saved. ODrive will reboot.")
    except Exception as e:
        print(f"Exception during save: {e}")
        print("ODrive disconnected during save as expected.")
    
    # Wait for ODrive to come back online
    return wait_for_odrive()

def calibrate_motor(odrv):
    """Calibrate the motor."""
    print("\nStarting motor calibration...")
    
    # Make sure we're in idle state
    print("Setting to idle state...")
    odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
    time.sleep(1)
    
    # Clear any errors
    clear_errors(odrv)
    
    # Start motor calibration
    print("Starting motor calibration...")
    odrv.axis0.requested_state = 4  # AXIS_STATE_MOTOR_CALIBRATION
    
    # Wait for calibration to complete
    print("Waiting for motor calibration to complete...")
    start_time = time.time()
    timeout = 30.0  # 30 seconds timeout
    
    while odrv.axis0.current_state != 1:  # AXIS_STATE_IDLE
        time.sleep(0.5)
        print(".", end="", flush=True)
        
        # Check for errors
        if odrv.axis0.motor.error != 0:
            error_codes = decode_motor_error(odrv.axis0.motor.error)
            print(f"\nMotor calibration failed with errors: {', '.join(error_codes)}")
            return False
        
        # Check for timeout
        if time.time() - start_time > timeout:
            print("\nMotor calibration timed out.")
            return False
    
    print("\nMotor calibration completed successfully.")
    
    # Check if motor is now calibrated
    if odrv.axis0.motor.is_calibrated:
        print("Motor is now calibrated!")
        return True
    else:
        print("Motor is still not calibrated after calibration.")
        return False

def calibrate_encoder(odrv):
    """Calibrate the encoder."""
    print("\nStarting encoder calibration...")
    
    # Make sure we're in idle state
    print("Setting to idle state...")
    odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
    time.sleep(1)
    
    # Clear any errors
    clear_errors(odrv)
    
    # Start encoder offset calibration
    print("Starting encoder offset calibration...")
    odrv.axis0.requested_state = 7  # AXIS_STATE_ENCODER_OFFSET_CALIBRATION
    
    # Wait for calibration to complete
    print("Waiting for encoder calibration to complete (this may take 5-10 seconds)...")
    start_time = time.time()
    timeout = 30.0  # 30 seconds timeout
    
    while odrv.axis0.current_state != 1:  # AXIS_STATE_IDLE
        time.sleep(0.5)
        print(".", end="", flush=True)
        
        # Check for errors
        if odrv.axis0.encoder.error != 0:
            print(f"\nEncoder calibration failed with error: {odrv.axis0.encoder.error}")
            return False
        
        # Check for timeout
        if time.time() - start_time > timeout:
            print("\nEncoder calibration timed out.")
            return False
    
    print("\nEncoder calibration completed.")
    
    # Check if encoder is now ready
    if odrv.axis0.encoder.is_ready:
        print("Encoder is now ready!")
        return True
    else:
        print("Encoder is still not ready after calibration.")
        return False

def save_calibration(odrv):
    """Save the calibration results."""
    print("\nSaving calibration results...")
    
    # Set pre-calibrated flags
    odrv.axis0.motor.config.pre_calibrated = True
    odrv.axis0.encoder.config.pre_calibrated = True
    
    # Save configuration
    try:
        odrv.save_configuration()
        print("Calibration saved. ODrive will reboot.")
    except Exception as e:
        print(f"Exception during save: {e}")
        print("ODrive disconnected during save as expected.")
    
    # Wait for ODrive to come back online
    return wait_for_odrive()

def test_closed_loop_control(odrv):
    """Test entering closed loop control mode."""
    print("\nTesting closed loop control...")
    
    # Make sure we're in idle state
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
    if odrv.axis0.current_state == 8:
        print("Successfully entered closed loop control mode!")
        
        # Test a simple velocity command
        print("Testing velocity command (2.0)...")
        odrv.axis0.controller.input_vel = 2.0
        time.sleep(2)
        
        # Stop the motor
        print("Stopping motor...")
        odrv.axis0.controller.input_vel = 0.0
        time.sleep(1)
        
        # Return to idle state
        print("Returning to idle state...")
        odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
        
        return True
    else:
        print(f"Failed to enter closed loop control. Current state: {odrv.axis0.current_state}")
        if odrv.axis0.error != 0:
            error_codes = decode_axis_error(odrv.axis0.error)
            print(f"Axis error: {odrv.axis0.error} ({', '.join(error_codes)})")
        return False

def fix_motor_failed_error():
    """Fix the MOTOR_FAILED error."""
    print("=== Fixing MOTOR_FAILED Error ===")
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Check initial status
    check_status(odrv)
    
    # Clear any errors
    clear_errors(odrv)
    
    # Reset configuration to defaults
    odrv = reset_configuration(odrv)
    
    # Calibrate motor
    if not calibrate_motor(odrv):
        print("Motor calibration failed. Exiting.")
        sys.exit(1)
    
    # Calibrate encoder
    if not calibrate_encoder(odrv):
        print("Encoder calibration failed. Exiting.")
        sys.exit(1)
    
    # Save calibration results
    odrv = save_calibration(odrv)
    
    # Check status after calibration
    check_status(odrv)
    
    # Test closed loop control
    if test_closed_loop_control(odrv):
        print("\nMOTOR_FAILED error has been fixed!")
        print("You can now use the ODrive in closed loop control mode.")
    else:
        print("\nFailed to fix MOTOR_FAILED error.")
        print("Please check your hardware connections and try again.")

if __name__ == "__main__":
    fix_motor_failed_error()
