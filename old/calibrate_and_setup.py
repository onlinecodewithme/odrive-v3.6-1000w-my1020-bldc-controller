#!/usr/bin/env python3
"""
Comprehensive ODrive calibration and setup script.
This script performs the necessary calibration steps before running velocity commands:
1. Clear errors
2. Calibrate motor
3. Calibrate encoder offset
4. Switch to closed loop control
5. Set control mode to velocity
6. Test velocity commands
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

def clear_errors(odrv):
    """Clear any errors on the ODrive."""
    print("\nClearing errors...")
    
    # Clear errors on axis 0
    if odrv.axis0.error != 0:
        print(f"Clearing axis error: {odrv.axis0.error}")
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

def optimize_parameters(odrv):
    """Set optimized parameters for better response time."""
    print("\nSetting optimized parameters...")
    
    # Controller parameters
    odrv.axis0.controller.config.input_filter_bandwidth = 150.0  # Significant reduction in filtering
    odrv.axis0.controller.config.vel_ramp_rate = 150.0  # Fast velocity ramping
    odrv.axis0.controller.config.vel_gain = 0.6  # Aggressive velocity gain
    odrv.axis0.controller.config.vel_integrator_gain = 0.3  # Increase integrator gain
    
    # Velocity limits
    odrv.axis0.controller.config.vel_limit = 30.0  # Higher velocity limit
    odrv.axis0.controller.config.enable_vel_limit = False  # Disable velocity limiting
    
    # Current control
    odrv.axis0.motor.config.current_control_bandwidth = 2500.0  # Higher bandwidth
    
    # Encoder parameters
    odrv.axis0.encoder.config.bandwidth = 2500.0  # Higher encoder bandwidth
    
    # Torque parameters
    odrv.axis0.controller.config.torque_ramp_rate = 0.05  # Increase torque ramp rate
    
    # Save configuration
    print("Saving configuration (ODrive will reboot)...")
    try:
        odrv.save_configuration()
        print("Configuration saved. ODrive is rebooting...")
    except:
        print("ODrive disconnected during save as expected. Waiting for reboot...")
    
    # Wait for ODrive to come back online
    odrv = wait_for_odrive()
    
    return odrv

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

def calibrate_motor_and_encoder(odrv):
    """Calibrate the motor and encoder."""
    print("\nStarting motor and encoder calibration...")
    
    # First, make sure we're in the right state
    print("Setting ODrive to idle state...")
    odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
    time.sleep(1.0)  # Wait a bit longer to ensure it's in idle state
    
    # Clear any errors before calibration
    clear_errors(odrv)
    
    # Check if motor is already calibrated
    if odrv.axis0.motor.is_calibrated:
        print("Motor is already calibrated. Skipping motor calibration.")
    else:
        # Start motor calibration
        print("Starting motor calibration...")
        odrv.axis0.requested_state = 4  # AXIS_STATE_MOTOR_CALIBRATION
        
        # Wait for motor calibration to complete (with timeout)
        print("Waiting for motor calibration to complete...")
        start_time = time.time()
        timeout = 30.0  # 30 seconds timeout
        
        while odrv.axis0.current_state != 1:  # AXIS_STATE_IDLE
            time.sleep(0.5)  # Check less frequently
            print(".", end="", flush=True)
            
            # Check for errors
            if odrv.axis0.motor.error != 0:
                error_codes = decode_motor_error(odrv.axis0.motor.error)
                print(f"\nMotor calibration failed with errors: {error_codes}")
                return odrv, False
            
            # Check for timeout
            if time.time() - start_time > timeout:
                print("\nMotor calibration timed out after 30 seconds.")
                return odrv, False
        
        print("\nMotor calibration completed successfully.")
    
    # Check if encoder is already calibrated
    if odrv.axis0.encoder.is_ready:
        print("Encoder is already calibrated. Skipping encoder calibration.")
    else:
        # Start encoder offset calibration
        print("Starting encoder offset calibration...")
        odrv.axis0.requested_state = 7  # AXIS_STATE_ENCODER_OFFSET_CALIBRATION
        
        # Wait for encoder calibration to complete (with timeout)
        print("Waiting for encoder calibration to complete (this may take 5-10 seconds)...")
        start_time = time.time()
        timeout = 20.0  # 20 seconds timeout for encoder calibration
        
        while odrv.axis0.current_state != 1:  # AXIS_STATE_IDLE
            time.sleep(0.5)  # Check less frequently
            print(".", end="", flush=True)
            
            # Check for errors
            if odrv.axis0.encoder.error != 0:
                print(f"\nEncoder calibration failed with error: {odrv.axis0.encoder.error}")
                return odrv, False
            
            # Check for timeout
            if time.time() - start_time > timeout:
                print("\nEncoder calibration timed out after 20 seconds.")
                return odrv, False
        
        print("\nEncoder calibration completed successfully.")
    
    # Save the calibration results
    print("Saving calibration results (ODrive will reboot)...")
    try:
        odrv.axis0.motor.config.pre_calibrated = True
        odrv.axis0.encoder.config.pre_calibrated = True
        odrv.save_configuration()
        print("Calibration saved. ODrive is rebooting...")
    except Exception as e:
        print(f"Exception during save: {e}")
        print("ODrive disconnected during save as expected. Waiting for reboot...")
    
    # Wait for ODrive to come back online
    odrv = wait_for_odrive()
    
    return odrv, True

def enter_closed_loop_control(odrv):
    """Enter closed loop control mode."""
    print("\nEntering closed loop control mode...")
    
    # Clear any errors first
    clear_errors(odrv)
    
    # Set control mode to velocity control
    print("Setting control mode to velocity control...")
    odrv.axis0.controller.config.control_mode = 2  # CONTROL_MODE_VELOCITY_CONTROL
    
    # Set input mode to velocity
    odrv.axis0.controller.config.input_mode = 1  # INPUT_MODE_PASSTHROUGH
    
    # Enter closed loop control
    print("Entering closed loop control...")
    odrv.axis0.requested_state = 8  # AXIS_STATE_CLOSED_LOOP_CONTROL
    
    # Wait for transition to complete
    time.sleep(0.5)
    
    # Check if we successfully entered closed loop control
    if odrv.axis0.current_state != 8:
        print(f"Failed to enter closed loop control. Current state: {odrv.axis0.current_state}")
        if odrv.axis0.error != 0:
            print(f"Axis error: {odrv.axis0.error}")
        return False
    
    print("Successfully entered closed loop control mode.")
    return True

def test_velocity_commands(odrv):
    """Test velocity commands with different velocities."""
    print("\nTesting velocity commands...")
    
    # Test velocities
    test_velocities = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0]
    results = []
    
    for vel in test_velocities:
        print(f"\nTesting velocity: {vel}")
        
        # Stop the motor first
        print("Stopping motor...")
        odrv.axis0.controller.input_vel = 0.0
        time.sleep(1)
        
        # Send velocity command and measure response time
        print(f"Setting velocity to {vel}...")
        start_time = time.time()
        odrv.axis0.controller.input_vel = vel
        
        # Wait for motor to start moving
        vel_threshold = vel * 0.05  # 5% of target velocity
        response_time = None
        max_velocity = 0.0
        
        # Monitor for 2 seconds
        timeout = 2.0
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
        
        # Let the motor run for a moment
        time.sleep(1)
        
        # Stop the motor
        print("Stopping motor...")
        odrv.axis0.controller.input_vel = 0.0
        time.sleep(1)
        
        results.append((vel, response_time, max_velocity))
    
    # Print summary
    print("\n=== Response Time Summary ===")
    print("Target Velocity | Response Time | Max Velocity")
    print("-------------------------------------------")
    
    total_response_time = 0
    count = 0
    
    for vel, resp, max_vel in results:
        if resp == float('inf'):
            print(f"{vel:14.1f} | No response    | {max_vel:12.2f}")
        else:
            print(f"{vel:14.1f} | {resp:12.4f} s | {max_vel:12.2f}")
            total_response_time += resp
            count += 1
    
    # Calculate average response time
    if count > 0:
        avg_response = total_response_time / count
        print(f"\nAverage response time: {avg_response:.4f} seconds")
    
    return results

if __name__ == "__main__":
    print("=== ODrive Calibration and Setup ===")
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Clear any existing errors
    clear_errors(odrv)
    
    # Set optimized parameters
    odrv = optimize_parameters(odrv)
    
    # Calibrate motor and encoder
    odrv, success = calibrate_motor_and_encoder(odrv)
    if not success:
        print("Calibration failed. Exiting.")
        sys.exit(1)
    
    # Enter closed loop control
    success = enter_closed_loop_control(odrv)
    if not success:
        print("Failed to enter closed loop control. Exiting.")
        sys.exit(1)
    
    # Test velocity commands
    results = test_velocity_commands(odrv)
    
    print("\nCalibration and setup complete. The motor should now respond immediately to velocity commands.")
    print("Example: odrv0.axis0.controller.input_vel = 5.0")
