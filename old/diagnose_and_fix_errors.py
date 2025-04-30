#!/usr/bin/env python3
"""
ODrive error diagnosis and fixing script.
This script specifically addresses axis error 64 and other common issues
that prevent entering closed loop control mode.
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
        error_codes = decode_motor_error(odrv.axis0.motor.error)
        print(f"Clearing motor error: {odrv.axis0.motor.error} ({', '.join(error_codes)})")
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

def fix_motor_failed_error(odrv):
    """Fix MOTOR_FAILED error (axis error 64)."""
    print("\nAttempting to fix MOTOR_FAILED error (axis error 64)...")
    
    # First, check if we have this specific error
    if odrv.axis0.error & 0x00000040:  # MOTOR_FAILED
        print("Confirmed MOTOR_FAILED error.")
        
        # Check motor error for more details
        motor_errors = decode_motor_error(odrv.axis0.motor.error)
        print(f"Motor errors: {', '.join(motor_errors)}")
        
        # Clear all errors first
        clear_errors(odrv)
        
        # Check if motor is calibrated
        if not odrv.axis0.motor.is_calibrated:
            print("Motor is not calibrated. Performing motor calibration...")
            odrv.axis0.requested_state = 4  # AXIS_STATE_MOTOR_CALIBRATION
            
            # Wait for calibration to complete
            print("Waiting for motor calibration to complete...")
            start_time = time.time()
            timeout = 30.0
            
            while odrv.axis0.current_state != 1:  # AXIS_STATE_IDLE
                time.sleep(0.5)
                print(".", end="", flush=True)
                
                if odrv.axis0.motor.error != 0:
                    error_codes = decode_motor_error(odrv.axis0.motor.error)
                    print(f"\nMotor calibration failed with errors: {', '.join(error_codes)}")
                    return False
                
                if time.time() - start_time > timeout:
                    print("\nMotor calibration timed out.")
                    return False
            
            print("\nMotor calibration completed successfully.")
        else:
            print("Motor is already calibrated.")
        
        # Check if encoder is ready
        if not odrv.axis0.encoder.is_ready:
            print("Encoder is not ready. Performing encoder offset calibration...")
            odrv.axis0.requested_state = 7  # AXIS_STATE_ENCODER_OFFSET_CALIBRATION
            
            # Wait for calibration to complete
            print("Waiting for encoder calibration to complete...")
            start_time = time.time()
            timeout = 20.0
            
            while odrv.axis0.current_state != 1:  # AXIS_STATE_IDLE
                time.sleep(0.5)
                print(".", end="", flush=True)
                
                if odrv.axis0.encoder.error != 0:
                    error_codes = decode_encoder_error(odrv.axis0.encoder.error)
                    print(f"\nEncoder calibration failed with errors: {', '.join(error_codes)}")
                    return False
                
                if time.time() - start_time > timeout:
                    print("\nEncoder calibration timed out.")
                    return False
            
            print("\nEncoder calibration completed successfully.")
        else:
            print("Encoder is already calibrated.")
        
        # Save configuration
        print("Saving configuration...")
        try:
            odrv.axis0.motor.config.pre_calibrated = True
            odrv.axis0.encoder.config.pre_calibrated = True
            odrv.save_configuration()
            print("Configuration saved. ODrive will reboot.")
        except Exception as e:
            print(f"Exception during save: {e}")
            print("ODrive disconnected during save as expected.")
        
        # Wait for ODrive to come back online
        odrv = wait_for_odrive()
        
        # Clear errors again after reboot
        clear_errors(odrv)
        
        print("MOTOR_FAILED error should now be fixed.")
        return True, odrv
    else:
        print("No MOTOR_FAILED error detected.")
        return True, odrv

def check_calibration_status(odrv):
    """Check and report calibration status."""
    print("\nChecking calibration status:")
    print(f"Motor calibrated: {odrv.axis0.motor.is_calibrated}")
    print(f"Encoder ready: {odrv.axis0.encoder.is_ready}")
    print(f"Motor pre-calibrated: {odrv.axis0.motor.config.pre_calibrated}")
    print(f"Encoder pre-calibrated: {odrv.axis0.encoder.config.pre_calibrated}")
    
    # Check current state
    states = {
        0: "UNDEFINED",
        1: "IDLE",
        2: "STARTUP_SEQUENCE",
        3: "FULL_CALIBRATION_SEQUENCE",
        4: "MOTOR_CALIBRATION",
        5: "SENSORLESS_CONTROL",
        6: "ENCODER_INDEX_SEARCH",
        7: "ENCODER_OFFSET_CALIBRATION",
        8: "CLOSED_LOOP_CONTROL",
        9: "LOCKIN_SPIN",
        10: "ENCODER_DIR_FIND",
        11: "HOMING",
        12: "ENCODER_HALL_POLARITY_CALIBRATION",
        13: "ENCODER_HALL_PHASE_CALIBRATION"
    }
    
    current_state = odrv.axis0.current_state
    state_name = states.get(current_state, f"UNKNOWN ({current_state})")
    print(f"Current state: {state_name}")
    
    # Check errors
    if odrv.axis0.error != 0:
        error_codes = decode_axis_error(odrv.axis0.error)
        print(f"Axis error: {odrv.axis0.error} ({', '.join(error_codes)})")
    
    if odrv.axis0.motor.error != 0:
        error_codes = decode_motor_error(odrv.axis0.motor.error)
        print(f"Motor error: {odrv.axis0.motor.error} ({', '.join(error_codes)})")
    
    if odrv.axis0.encoder.error != 0:
        error_codes = decode_encoder_error(odrv.axis0.encoder.error)
        print(f"Encoder error: {odrv.axis0.encoder.error} ({', '.join(error_codes)})")

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
    print("=== ODrive Error Diagnosis and Fixing ===")
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Check initial status
    print("\n--- Initial Status ---")
    check_calibration_status(odrv)
    
    # Clear all errors
    clear_errors(odrv)
    
    # Fix motor failed error if present
    success, odrv = fix_motor_failed_error(odrv)
    if not success:
        print("Failed to fix motor error. Exiting.")
        sys.exit(1)
    
    # Check status after fixes
    print("\n--- Status After Fixes ---")
    check_calibration_status(odrv)
    
    # Try to enter closed loop control
    success = enter_closed_loop_control(odrv)
    if not success:
        print("Failed to enter closed loop control even after fixes. Exiting.")
        sys.exit(1)
    
    # Test a velocity command
    success = test_velocity_command(odrv, 5.0)
    if not success:
        print("Velocity command test failed.")
    else:
        print("Velocity command test succeeded!")
    
    print("\nDiagnosis and fixing complete.")
    print("You should now be able to control the motor with velocity commands.")
    print("Example: odrv0.axis0.controller.input_vel = 5.0")
