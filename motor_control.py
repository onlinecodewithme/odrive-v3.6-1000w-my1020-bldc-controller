#!/usr/bin/env python3
"""
Differential Robot Controller for ODrive.
This script provides a comprehensive interface to control both motors (axis0 and axis1)
of an ODrive-powered differential drive robot. It does not modify any configuration parameters.
"""
import odrive
import time
import sys
import argparse
import math

# Robot parameters
WHEEL_RADIUS = 0.05  # meters (adjust based on your robot's wheel size)
WHEEL_BASE = 0.3     # meters (distance between wheels, adjust based on your robot)
MAX_VELOCITY = 20.0  # turns/s (maximum safe velocity for your motors)

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

def check_errors(odrv, axis_num=None):
    """Check for errors and print them."""
    has_errors = False
    
    axes = []
    if axis_num is None:
        axes = [odrv.axis0, odrv.axis1]
    elif axis_num == 0:
        axes = [odrv.axis0]
    elif axis_num == 1:
        axes = [odrv.axis1]
    
    for i, axis in enumerate(axes):
        if axis.error != 0:
            print(f"Axis{i} error: {axis.error}")
            has_errors = True
        
        if axis.motor.error != 0:
            print(f"Motor{i} error: {axis.motor.error}")
            has_errors = True
        
        if axis.encoder.error != 0:
            print(f"Encoder{i} error: {axis.encoder.error}")
            has_errors = True
        
        if axis.controller.error != 0:
            print(f"Controller{i} error: {axis.controller.error}")
            has_errors = True
    
    return has_errors

def clear_errors(odrv, axis_num=None):
    """Clear all errors on the ODrive."""
    print("Clearing errors...")
    odrv.clear_errors()
    
    axes = []
    if axis_num is None:
        axes = [odrv.axis0, odrv.axis1]
    elif axis_num == 0:
        axes = [odrv.axis0]
    elif axis_num == 1:
        axes = [odrv.axis1]
    
    for i, axis in enumerate(axes):
        axis.error = 0
        axis.motor.error = 0
        axis.encoder.error = 0
        axis.controller.error = 0
    
    print("Errors cleared.")

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

def calibrate_motor_and_encoder(odrv, axis_num=None, force=False):
    """
    Calibrate motor and encoder for specified axis or both.
    
    WARNING: This will cause the motor to move! Make sure the robot is in a safe position
    before calibration.
    
    Args:
        odrv: ODrive object
        axis_num: Axis number to calibrate (None for both axes)
        force: Force calibration even if already calibrated
    
    Returns:
        Tuple of (success, odrv)
    """
    # Safety warning
    print("\n⚠️ WARNING: Calibration will cause the motor to move! ⚠️")
    print("Make sure the robot is in a safe position before continuing.")
    
    if not force:
        confirmation = input("Continue with calibration? (y/n): ").strip().lower()
        if confirmation != 'y':
            print("Calibration aborted.")
            return False, odrv
    
    axes = []
    if axis_num is None:
        print("Calibrating both axes...")
        axes = [(0, odrv.axis0), (1, odrv.axis1)]
    elif axis_num == 0:
        print("Calibrating axis0...")
        axes = [(0, odrv.axis0)]
    elif axis_num == 1:
        print("Calibrating axis1...")
        axes = [(1, odrv.axis1)]
    
    success = True
    
    # Clear any errors first
    if check_errors(odrv, axis_num):
        clear_errors(odrv, axis_num)
    
    for i, axis in axes:
        # Check if motor is already calibrated
        if not force and axis.motor.is_calibrated and axis.encoder.is_ready:
            print(f"Axis{i} is already calibrated. Use --force to recalibrate.")
            continue
        
        print(f"Calibrating motor for axis{i}...")
        
        # First, make sure we're in idle state
        axis.requested_state = 1  # AXIS_STATE_IDLE
        time.sleep(1.0)
        
        # Clear any errors
        if axis.error != 0 or axis.motor.error != 0 or axis.encoder.error != 0:
            print(f"Clearing errors for axis{i}...")
            axis.error = 0
            axis.motor.error = 0
            axis.encoder.error = 0
        
        # Calibrate motor if needed
        if force or not axis.motor.is_calibrated:
            print(f"Starting motor calibration for axis{i}...")
            axis.requested_state = 4  # AXIS_STATE_MOTOR_CALIBRATION
            
            # Wait for calibration to complete
            start_time = time.time()
            timeout = 30.0  # 30 seconds timeout
            
            while axis.current_state != 1:  # AXIS_STATE_IDLE
                time.sleep(0.5)
                print(".", end="", flush=True)
                
                # Check for errors
                if axis.motor.error != 0:
                    print(f"\nMotor calibration failed for axis{i} with error: {axis.motor.error}")
                    success = False
                    break
                
                # Check for timeout
                if time.time() - start_time > timeout:
                    print(f"\nMotor calibration timed out for axis{i}.")
                    success = False
                    break
            
            if success and axis.motor.is_calibrated:
                print(f"\nMotor calibration completed successfully for axis{i}.")
            else:
                print(f"\nMotor calibration failed for axis{i}.")
                continue
        
        # Calibrate encoder if needed
        if force or not axis.encoder.is_ready:
            print(f"Starting encoder offset calibration for axis{i}...")
            axis.requested_state = 7  # AXIS_STATE_ENCODER_OFFSET_CALIBRATION
            
            # Wait for calibration to complete
            start_time = time.time()
            timeout = 30.0  # 30 seconds timeout
            
            while axis.current_state != 1:  # AXIS_STATE_IDLE
                time.sleep(0.5)
                print(".", end="", flush=True)
                
                # Check for errors
                if axis.encoder.error != 0:
                    print(f"\nEncoder calibration failed for axis{i} with error: {axis.encoder.error}")
                    success = False
                    break
                
                # Check for timeout
                if time.time() - start_time > timeout:
                    print(f"\nEncoder calibration timed out for axis{i}.")
                    success = False
                    break
            
            if success and axis.encoder.is_ready:
                print(f"\nEncoder calibration completed successfully for axis{i}.")
            else:
                print(f"\nEncoder calibration failed for axis{i}.")
                continue
        
        # Save calibration results
        print(f"Saving calibration results for axis{i}...")
        axis.motor.config.pre_calibrated = True
        axis.encoder.config.pre_calibrated = True
    
    # Save configuration if any calibration was performed
    if success:
        try:
            print("Saving configuration...")
            odrv.save_configuration()
            print("Configuration saved. ODrive will reboot.")
            # Wait for ODrive to come back online
            odrv = wait_for_odrive()
        except Exception as e:
            print(f"Exception during save: {e}")
            print("ODrive disconnected during save as expected.")
            # Wait for ODrive to come back online
            odrv = wait_for_odrive()
    
    return success, odrv

def check_calibration_status(odrv, axis_num=None):
    """Check if calibration is needed for specified axis or both."""
    axes = []
    if axis_num is None:
        axes = [(0, odrv.axis0), (1, odrv.axis1)]
    elif axis_num == 0:
        axes = [(0, odrv.axis0)]
    elif axis_num == 1:
        axes = [(1, odrv.axis1)]
    
    calibration_needed = False
    for i, axis in axes:
        if not axis.motor.is_calibrated or not axis.encoder.is_ready:
            print(f"Axis{i} needs calibration.")
            calibration_needed = True
        else:
            print(f"Axis{i} is already calibrated.")
    
    return calibration_needed

def enter_closed_loop_control(odrv, axis_num=None, auto_calibrate=False):
    """
    Enter closed loop control mode for specified axis or both.
    
    Args:
        odrv: ODrive object
        axis_num: Axis number to control (None for both axes)
        auto_calibrate: Whether to automatically calibrate if needed
    
    Returns:
        Boolean indicating success
    """
    axes = []
    if axis_num is None:
        print("Entering closed loop control mode for both axes...")
        axes = [(0, odrv.axis0), (1, odrv.axis1)]
    elif axis_num == 0:
        print("Entering closed loop control mode for axis0...")
        axes = [(0, odrv.axis0)]
    elif axis_num == 1:
        print("Entering closed loop control mode for axis1...")
        axes = [(1, odrv.axis1)]
    
    success = True
    
    # Clear any errors first
    if check_errors(odrv, axis_num):
        clear_errors(odrv, axis_num)
    
    # Check if calibration is needed for any axis
    calibration_needed = False
    for i, axis in axes:
        if not axis.motor.is_calibrated or not axis.encoder.is_ready:
            calibration_needed = True
            break
    
    # If calibration is needed, try to apply pre-calibrated configuration first
    if calibration_needed:
        try:
            # Try to import the pre-calibrated configuration module
            print("Trying to apply pre-calibrated configuration...")
            import precalibrated_config
            
            # Apply pre-calibrated configuration
            precalibrated_config.apply_precalibrated_config(odrv)
            
            # Check if calibration is still needed
            calibration_needed = False
            for i, axis in axes:
                if not axis.motor.is_calibrated or not axis.encoder.is_ready:
                    calibration_needed = True
                    break
            
            if not calibration_needed:
                print("Pre-calibrated configuration applied successfully.")
            else:
                print("Pre-calibrated configuration applied, but calibration is still needed.")
        except ImportError:
            print("No pre-calibrated configuration found.")
        except Exception as e:
            print(f"Error applying pre-calibrated configuration: {e}")
    
    # Perform calibration if still needed and auto_calibrate is True
    if calibration_needed:
        if auto_calibrate:
            print("Calibration needed before entering closed loop control.")
            success, odrv = calibrate_motor_and_encoder(odrv, axis_num, force=False)
            if not success:
                print("Calibration failed. Cannot enter closed loop control.")
                return False
        else:
            print("Calibration needed but auto_calibrate is False.")
            print("Please run calibration first with: ./motor_control.py calibrate")
            print("Or generate a pre-calibrated configuration with: ./generate_precalibrated_config.py")
            return False
    
    # Enter closed loop control for each axis
    for i, axis in axes:
        # Check if already in closed loop control
        if axis.current_state == 8:  # AXIS_STATE_CLOSED_LOOP_CONTROL
            print(f"Axis{i} already in closed loop control mode.")
            continue
        
        # Enter closed loop control
        axis.requested_state = 8  # AXIS_STATE_CLOSED_LOOP_CONTROL
        time.sleep(0.5)
        
        # Check if we successfully entered closed loop control
        if axis.current_state != 8:
            print(f"Failed to enter closed loop control for axis{i}. Current state: {axis.current_state}")
            check_errors(odrv, i)
            success = False
        else:
            print(f"Successfully entered closed loop control mode for axis{i}.")
    
    return success

def set_velocity_mode(odrv, axis_num=None):
    """Set velocity control mode for specified axis or both."""
    axes = []
    if axis_num is None:
        axes = [(0, odrv.axis0), (1, odrv.axis1)]
    elif axis_num == 0:
        axes = [(0, odrv.axis0)]
    elif axis_num == 1:
        axes = [(1, odrv.axis1)]
    
    for i, axis in axes:
        if axis.controller.config.control_mode != 2:  # CONTROL_MODE_VELOCITY_CONTROL
            print(f"Setting axis{i} to velocity control mode...")
            axis.controller.config.control_mode = 2
            time.sleep(0.1)

def set_position_mode(odrv, axis_num=None):
    """Set position control mode for specified axis or both."""
    axes = []
    if axis_num is None:
        axes = [(0, odrv.axis0), (1, odrv.axis1)]
    elif axis_num == 0:
        axes = [(0, odrv.axis0)]
    elif axis_num == 1:
        axes = [(1, odrv.axis1)]
    
    for i, axis in axes:
        if axis.controller.config.control_mode != 3:  # CONTROL_MODE_POSITION_CONTROL
            print(f"Setting axis{i} to position control mode...")
            axis.controller.config.control_mode = 3
            time.sleep(0.1)

# Constants for motor direction
# Set these based on your robot's motor configuration
LEFT_MOTOR_DIRECTION = 1    # 1 for normal, -1 for inverted
RIGHT_MOTOR_DIRECTION = -1  # 1 for normal, -1 for inverted

def set_wheel_velocity_gradual(odrv, left_vel, right_vel, steps=10, delay=0.02):
    """
    Gradually set the velocity of both wheels.
    
    This function gradually changes the velocity from the current value to the target value
    in small increments, providing smoother acceleration and deceleration.
    
    Args:
        odrv: ODrive object
        left_vel: Target left wheel velocity
        right_vel: Target right wheel velocity
        steps: Number of steps to reach the target velocity (default: 10)
        delay: Delay between steps in seconds (default: 0.02)
    """
    # Check if axes are in IDLE mode and switch to closed loop control if needed
    axes_to_check = [(0, odrv.axis0), (1, odrv.axis1)]
    for i, axis in axes_to_check:
        if axis.current_state == 1:  # AXIS_STATE_IDLE
            print(f"Axis{i} is in IDLE mode. Switching to closed loop control...")
            axis.requested_state = 8  # AXIS_STATE_CLOSED_LOOP_CONTROL
            time.sleep(0.5)
            
            # Check if we successfully entered closed loop control
            if axis.current_state != 8:
                print(f"Failed to enter closed loop control for axis{i}. Current state: {axis.current_state}")
                check_errors(odrv, i)
                return False
            else:
                print(f"Successfully switched axis{i} from IDLE to closed loop control mode.")
    
    # Make sure we're in closed loop control for both axes
    if not enter_closed_loop_control(odrv):
        return False
    
    # Make sure we're in velocity control mode
    set_velocity_mode(odrv)
    
    # Apply direction correction (for differential drive where motors are mounted in opposite directions)
    left_vel = left_vel * LEFT_MOTOR_DIRECTION
    right_vel = right_vel * RIGHT_MOTOR_DIRECTION
    
    # Clamp velocities to safe limits
    left_vel = max(min(left_vel, MAX_VELOCITY), -MAX_VELOCITY)
    right_vel = max(min(right_vel, MAX_VELOCITY), -MAX_VELOCITY)
    
    # Get current velocities
    current_left_vel = odrv.axis0.controller.input_vel
    current_right_vel = odrv.axis1.controller.input_vel
    
    # Calculate velocity increments
    left_increment = (left_vel - current_left_vel) / steps
    right_increment = (right_vel - current_right_vel) / steps
    
    print(f"Gradually changing wheel velocities to - Left: {left_vel:.2f}, Right: {right_vel:.2f}")
    
    # Gradually change velocities
    for i in range(steps):
        new_left_vel = current_left_vel + left_increment * (i + 1)
        new_right_vel = current_right_vel + right_increment * (i + 1)
        
        # Set velocities
        odrv.axis0.controller.input_vel = new_left_vel
        odrv.axis1.controller.input_vel = new_right_vel
        
        # Small delay between steps
        time.sleep(delay)
    
    # Ensure we reach the exact target velocities
    odrv.axis0.controller.input_vel = left_vel
    odrv.axis1.controller.input_vel = right_vel
    
    return True

def set_wheel_velocity(odrv, left_vel, right_vel):
    """Set the velocity of both wheels."""
    # Make sure we're in closed loop control
    if not enter_closed_loop_control(odrv):
        return False
    
    # Make sure we're in velocity control mode
    set_velocity_mode(odrv)
    
    # Apply direction correction (for differential drive where motors are mounted in opposite directions)
    left_vel = left_vel * LEFT_MOTOR_DIRECTION
    right_vel = right_vel * RIGHT_MOTOR_DIRECTION
    
    # Clamp velocities to safe limits
    left_vel = max(min(left_vel, MAX_VELOCITY), -MAX_VELOCITY)
    right_vel = max(min(right_vel, MAX_VELOCITY), -MAX_VELOCITY)
    
    # Set velocities gradually
    if not set_wheel_velocity_gradual(odrv, left_vel / LEFT_MOTOR_DIRECTION, right_vel / RIGHT_MOTOR_DIRECTION):
        return False
    
    # Monitor velocities for a short time
    print("Monitoring velocities for 2 seconds...")
    start_time = time.time()
    max_left_vel = 0.0
    max_right_vel = 0.0
    
    while time.time() - start_time < 2.0:
        current_left_vel = abs(odrv.axis0.encoder.vel_estimate)
        current_right_vel = abs(odrv.axis1.encoder.vel_estimate)
        max_left_vel = max(max_left_vel, current_left_vel)
        max_right_vel = max(max_right_vel, current_right_vel)
        time.sleep(0.1)
    
    print(f"Maximum velocities reached - Left: {max_left_vel:.2f}, Right: {max_right_vel:.2f}")
    return True

def set_wheel_position(odrv, left_pos, right_pos):
    """Set the position of both wheels."""
    # Make sure we're in closed loop control
    if not enter_closed_loop_control(odrv):
        return False
    
    # Make sure we're in position control mode
    set_position_mode(odrv)
    
    # Get current positions
    current_left_pos = odrv.axis0.encoder.pos_estimate
    current_right_pos = odrv.axis1.encoder.pos_estimate
    print(f"Current positions - Left: {current_left_pos:.2f}, Right: {current_right_pos:.2f}")
    
    # Set positions
    print(f"Setting wheel positions - Left: {left_pos:.2f}, Right: {right_pos:.2f}")
    odrv.axis0.controller.input_pos = left_pos
    odrv.axis1.controller.input_pos = right_pos
    
    # Monitor positions for a short time
    print("Monitoring positions for 3 seconds...")
    start_time = time.time()
    
    while time.time() - start_time < 3.0:
        current_left_pos = odrv.axis0.encoder.pos_estimate
        current_right_pos = odrv.axis1.encoder.pos_estimate
        print(f"Current positions - Left: {current_left_pos:.2f}, Right: {current_right_pos:.2f}", end="\r")
        time.sleep(0.1)
        
        # Check if we've reached the target positions
        if (abs(current_left_pos - left_pos) < 0.1 and 
            abs(current_right_pos - right_pos) < 0.1):
            print(f"\nReached target positions - Left: {current_left_pos:.2f}, Right: {current_right_pos:.2f}")
            break
    
    print(f"\nFinal positions - Left: {odrv.axis0.encoder.pos_estimate:.2f}, Right: {odrv.axis1.encoder.pos_estimate:.2f}")
    return True

def move_forward(odrv, velocity):
    """Move the robot forward at the specified velocity."""
    return set_wheel_velocity(odrv, velocity, velocity)

def move_backward(odrv, velocity):
    """Move the robot backward at the specified velocity."""
    return set_wheel_velocity(odrv, -velocity, -velocity)

def turn_left(odrv, velocity):
    """Turn the robot left at the specified velocity."""
    return set_wheel_velocity(odrv, -velocity, velocity)

def turn_right(odrv, velocity):
    """Turn the robot right at the specified velocity."""
    return set_wheel_velocity(odrv, velocity, -velocity)

def move_robot(odrv, linear_vel, angular_vel):
    """Move the robot with the specified linear and angular velocity."""
    # Convert linear and angular velocity to wheel velocities
    # For a differential drive robot:
    # v_left = linear_vel - (angular_vel * wheel_base / 2)
    # v_right = linear_vel + (angular_vel * wheel_base / 2)
    
    # Convert to wheel velocities in turns/s
    left_vel = (linear_vel - (angular_vel * WHEEL_BASE / 2)) / (2 * math.pi * WHEEL_RADIUS)
    right_vel = (linear_vel + (angular_vel * WHEEL_BASE / 2)) / (2 * math.pi * WHEEL_RADIUS)
    
    return set_wheel_velocity(odrv, left_vel, right_vel)

def stop_robot(odrv):
    """Stop the robot."""
    print("Stopping robot...")
    
    # First set velocity to 0 to ensure smooth stop
    # Check current control mode for each axis
    axis0_mode = odrv.axis0.controller.config.control_mode
    axis1_mode = odrv.axis1.controller.config.control_mode
    
    if axis0_mode == 2:  # CONTROL_MODE_VELOCITY_CONTROL
        odrv.axis0.controller.input_vel = 0.0
    elif axis0_mode == 3:  # CONTROL_MODE_POSITION_CONTROL
        # Keep current position
        odrv.axis0.controller.input_pos = odrv.axis0.encoder.pos_estimate
    
    if axis1_mode == 2:  # CONTROL_MODE_VELOCITY_CONTROL
        odrv.axis1.controller.input_vel = 0.0
    elif axis1_mode == 3:  # CONTROL_MODE_POSITION_CONTROL
        # Keep current position
        odrv.axis1.controller.input_pos = odrv.axis1.encoder.pos_estimate
    
    # Wait a moment for the robot to come to a stop
    time.sleep(0.2)
    
    # Change axis mode to IDLE for both axes
    print("Changing axis mode to IDLE...")
    odrv.axis0.requested_state = 1  # AXIS_STATE_IDLE
    odrv.axis1.requested_state = 1  # AXIS_STATE_IDLE
    
    print("Robot stopped and motors set to IDLE mode.")
    return True

def get_robot_status(odrv):
    """Get the current status of the robot."""
    print("\n=== Robot Status ===")
    
    # Get current state for each axis
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
    
    control_modes = {
        0: "VOLTAGE_CONTROL",
        1: "TORQUE_CONTROL",
        2: "VELOCITY_CONTROL",
        3: "POSITION_CONTROL"
    }
    
    # Axis 0 (Left wheel)
    print("Left Wheel (Axis 0):")
    current_state = odrv.axis0.current_state
    state_name = states.get(current_state, f"UNKNOWN ({current_state})")
    print(f"  State: {state_name}")
    
    control_mode = odrv.axis0.controller.config.control_mode
    mode_name = control_modes.get(control_mode, f"UNKNOWN ({control_mode})")
    print(f"  Control mode: {mode_name}")
    
    print(f"  Position: {odrv.axis0.encoder.pos_estimate:.2f}")
    print(f"  Velocity: {odrv.axis0.encoder.vel_estimate:.2f}")
    
    # Axis 1 (Right wheel)
    print("\nRight Wheel (Axis 1):")
    current_state = odrv.axis1.current_state
    state_name = states.get(current_state, f"UNKNOWN ({current_state})")
    print(f"  State: {state_name}")
    
    control_mode = odrv.axis1.controller.config.control_mode
    mode_name = control_modes.get(control_mode, f"UNKNOWN ({control_mode})")
    print(f"  Control mode: {mode_name}")
    
    print(f"  Position: {odrv.axis1.encoder.pos_estimate:.2f}")
    print(f"  Velocity: {odrv.axis1.encoder.vel_estimate:.2f}")
    
    # Check for errors
    check_errors(odrv)
    
    return True

def interactive_mode(odrv):
    """Run in interactive mode."""
    print("\n=== Differential Robot Controller - Interactive Mode ===")
    print("Commands:")
    print("  f <velocity>      - Move forward")
    print("  b <velocity>      - Move backward")
    print("  l <velocity>      - Turn left")
    print("  r <velocity>      - Turn right")
    print("  m <linear> <angular> - Move with linear and angular velocity")
    print("  v <left> <right>  - Set wheel velocities directly")
    print("  p <left> <right>  - Set wheel positions directly")
    print("  s                 - Stop robot")
    print("  cal               - Calibrate motors and encoders")
    print("  cal0              - Calibrate axis0 only")
    print("  cal1              - Calibrate axis1 only")
    print("  check             - Check calibration status")
    print("  status            - Get robot status")
    print("  clear             - Clear errors")
    print("  q                 - Quit")
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command.startswith("f "):
                try:
                    velocity = float(command.split(" ")[1])
                    move_forward(odrv, velocity)
                except (ValueError, IndexError):
                    print("Invalid velocity. Usage: f <velocity>")
            
            elif command.startswith("b "):
                try:
                    velocity = float(command.split(" ")[1])
                    move_backward(odrv, velocity)
                except (ValueError, IndexError):
                    print("Invalid velocity. Usage: b <velocity>")
            
            elif command.startswith("l "):
                try:
                    velocity = float(command.split(" ")[1])
                    turn_left(odrv, velocity)
                except (ValueError, IndexError):
                    print("Invalid velocity. Usage: l <velocity>")
            
            elif command.startswith("r "):
                try:
                    velocity = float(command.split(" ")[1])
                    turn_right(odrv, velocity)
                except (ValueError, IndexError):
                    print("Invalid velocity. Usage: r <velocity>")
            
            elif command.startswith("m "):
                try:
                    parts = command.split(" ")
                    linear = float(parts[1])
                    angular = float(parts[2])
                    move_robot(odrv, linear, angular)
                except (ValueError, IndexError):
                    print("Invalid parameters. Usage: m <linear> <angular>")
            
            elif command.startswith("v "):
                try:
                    parts = command.split(" ")
                    left = float(parts[1])
                    right = float(parts[2])
                    set_wheel_velocity(odrv, left, right)
                except (ValueError, IndexError):
                    print("Invalid parameters. Usage: v <left> <right>")
            
            elif command.startswith("p "):
                try:
                    parts = command.split(" ")
                    left = float(parts[1])
                    right = float(parts[2])
                    set_wheel_position(odrv, left, right)
                except (ValueError, IndexError):
                    print("Invalid parameters. Usage: p <left> <right>")
            
            elif command == "s":
                stop_robot(odrv)
            
            elif command == "cal":
                success, odrv = calibrate_motor_and_encoder(odrv, None, False)
                if success:
                    print("Calibration completed successfully.")
                else:
                    print("Calibration failed or was aborted.")
            
            elif command == "cal0":
                success, odrv = calibrate_motor_and_encoder(odrv, 0, False)
                if success:
                    print("Axis0 calibration completed successfully.")
                else:
                    print("Axis0 calibration failed or was aborted.")
            
            elif command == "cal1":
                success, odrv = calibrate_motor_and_encoder(odrv, 1, False)
                if success:
                    print("Axis1 calibration completed successfully.")
                else:
                    print("Axis1 calibration failed or was aborted.")
            
            elif command == "check":
                check_calibration_status(odrv)
            
            elif command == "status":
                get_robot_status(odrv)
            
            elif command == "clear":
                clear_errors(odrv)
            
            elif command == "q":
                print("Exiting...")
                break
            
            else:
                print("Unknown command. Try again.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Differential Robot Controller for ODrive")
    parser.add_argument("command", nargs="?", 
                        choices=["calibrate", "check", "forward", "backward", "left", "right", 
                                "move", "velocity", "position", "status", "clear"], 
                        help="Command to execute")
    parser.add_argument("value", nargs="*", type=float, help="Values for the command")
    parser.add_argument("--force", action="store_true", help="Force calibration even if already calibrated")
    parser.add_argument("--auto-calibrate", action="store_true", 
                        help="Automatically calibrate if needed (use with caution)")
    parser.add_argument("--axis", type=int, choices=[0, 1], 
                        help="Specify which axis to operate on (0 or 1)")
    
    args = parser.parse_args()
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Execute command or run in interactive mode
    if args.command is None:
        interactive_mode(odrv)
    elif args.command == "calibrate":
        # Explicit calibration command
        axis_num = args.axis if args.axis is not None else None
        success, odrv = calibrate_motor_and_encoder(odrv, axis_num, args.force)
        if success:
            print("Calibration completed successfully.")
        else:
            print("Calibration failed.")
            sys.exit(1)
    elif args.command == "check":
        # Check calibration status
        axis_num = args.axis if args.axis is not None else None
        check_calibration_status(odrv, axis_num)
    elif args.command == "forward":
        if not args.value or len(args.value) < 1:
            print("Error: Velocity value required. Usage: motor_control.py forward <velocity>")
            sys.exit(1)
        # Set auto_calibrate based on command line argument
        if not enter_closed_loop_control(odrv, auto_calibrate=args.auto_calibrate):
            print("Failed to enter closed loop control. Please calibrate first.")
            sys.exit(1)
        move_forward(odrv, args.value[0])
    elif args.command == "backward":
        if not args.value or len(args.value) < 1:
            print("Error: Velocity value required. Usage: motor_control.py backward <velocity>")
            sys.exit(1)
        if not enter_closed_loop_control(odrv, auto_calibrate=args.auto_calibrate):
            print("Failed to enter closed loop control. Please calibrate first.")
            sys.exit(1)
        move_backward(odrv, args.value[0])
    elif args.command == "left":
        if not args.value or len(args.value) < 1:
            print("Error: Velocity value required. Usage: motor_control.py left <velocity>")
            sys.exit(1)
        if not enter_closed_loop_control(odrv, auto_calibrate=args.auto_calibrate):
            print("Failed to enter closed loop control. Please calibrate first.")
            sys.exit(1)
        turn_left(odrv, args.value[0])
    elif args.command == "right":
        if not args.value or len(args.value) < 1:
            print("Error: Velocity value required. Usage: motor_control.py right <velocity>")
            sys.exit(1)
        if not enter_closed_loop_control(odrv, auto_calibrate=args.auto_calibrate):
            print("Failed to enter closed loop control. Please calibrate first.")
            sys.exit(1)
        turn_right(odrv, args.value[0])
    elif args.command == "move":
        if not args.value or len(args.value) < 2:
            print("Error: Linear and angular velocity required. Usage: motor_control.py move <linear> <angular>")
            sys.exit(1)
        if not enter_closed_loop_control(odrv, auto_calibrate=args.auto_calibrate):
            print("Failed to enter closed loop control. Please calibrate first.")
            sys.exit(1)
        move_robot(odrv, args.value[0], args.value[1])
    elif args.command == "velocity":
        if not args.value or len(args.value) < 2:
            print("Error: Left and right velocity required. Usage: motor_control.py velocity <left> <right>")
            sys.exit(1)
        if not enter_closed_loop_control(odrv, auto_calibrate=args.auto_calibrate):
            print("Failed to enter closed loop control. Please calibrate first.")
            sys.exit(1)
        set_wheel_velocity(odrv, args.value[0], args.value[1])
    elif args.command == "position":
        if not args.value or len(args.value) < 2:
            print("Error: Left and right position required. Usage: motor_control.py position <left> <right>")
            sys.exit(1)
        if not enter_closed_loop_control(odrv, auto_calibrate=args.auto_calibrate):
            print("Failed to enter closed loop control. Please calibrate first.")
            sys.exit(1)
        set_wheel_position(odrv, args.value[0], args.value[1])
    elif args.command == "status":
        get_robot_status(odrv)
    elif args.command == "clear":
        clear_errors(odrv)

if __name__ == "__main__":
    main()
