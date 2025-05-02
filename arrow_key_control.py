#!/usr/bin/env python3
"""
Arrow Key Controller for ODrive.
This script allows controlling an ODrive-powered differential drive robot using arrow keys.
"""
import odrive
import time
import sys
import signal
import readchar

# Import functions from motor_control.py
from motor_control import connect_to_odrive, enter_closed_loop_control, set_velocity_mode, stop_robot

# Robot parameters
MAX_VELOCITY = 5.0  # turns/s (maximum safe velocity for your motors)
VELOCITY_INCREMENT = 0.5  # How much to increase/decrease velocity with each key press
DEFAULT_VELOCITY = 30.0  # Default velocity when pressing arrow keys

# Global variables
current_velocity = DEFAULT_VELOCITY
is_running = True

def handle_exit(signal, frame):
    """Handle exit signal to ensure robot stops before exiting."""
    global is_running
    print("\nExiting arrow key control mode...")
    is_running = False
    if 'odrv' in globals():
        stop_robot(odrv)
    sys.exit(0)

def print_instructions():
    """Print instructions for arrow key control."""
    print("\n=== Arrow Key Control Mode ===")
    print("Use the following keys to control the robot:")
    print("  w or ↑           - Move forward")
    print("  s or ↓           - Move backward")
    print("  a or ←           - Turn left")
    print("  d or →           - Turn right")
    print("  + or =           - Increase velocity")
    print("  - or _           - Decrease velocity")
    print("  Space            - Stop robot")
    print("  q or Esc         - Exit")
    print(f"\nCurrent velocity: {current_velocity:.1f}")

def set_direct_velocity(odrv, left_vel, right_vel):
    """Set velocity directly without monitoring."""
    # Make sure we're in velocity control mode
    set_velocity_mode(odrv)
    
    # Apply direction correction (for differential drive where motors are mounted in opposite directions)
    # Note: These direction constants should match those in motor_control.py
    LEFT_MOTOR_DIRECTION = 1    # 1 for normal, -1 for inverted
    RIGHT_MOTOR_DIRECTION = -1  # 1 for normal, -1 for inverted
    
    left_vel = left_vel * LEFT_MOTOR_DIRECTION
    right_vel = right_vel * RIGHT_MOTOR_DIRECTION
    
    # Clamp velocities to safe limits
    left_vel = max(min(left_vel, MAX_VELOCITY), -MAX_VELOCITY)
    right_vel = max(min(right_vel, MAX_VELOCITY), -MAX_VELOCITY)
    
    # Set velocities directly (no gradual change for more responsive control)
    odrv.axis0.controller.input_vel = left_vel
    odrv.axis1.controller.input_vel = right_vel

def arrow_key_control(odrv):
    """Control the robot using arrow keys."""
    global current_velocity, is_running
    
    # Register signal handlers for clean exit
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    # Make sure we're in closed loop control
    if not enter_closed_loop_control(odrv):
        print("Failed to enter closed loop control. Please calibrate first.")
        return False
    
    # Print instructions
    print_instructions()
    
    # Initialize state
    is_moving = False
    current_left_vel = 0.0
    current_right_vel = 0.0
    
    # Main control loop
    print("Press a key to control the robot (q to quit)...")
    
    while is_running:
        # Read a key without blocking
        key = readchar.readkey()
        
        # Process the key
        if key in ('w', 'W', readchar.key.UP):
            current_left_vel = current_velocity
            current_right_vel = current_velocity
            is_moving = True
            print(f"Moving forward at velocity {current_velocity:.1f}    ")
        
        elif key in ('s', 'S', readchar.key.DOWN):
            current_left_vel = -current_velocity
            current_right_vel = -current_velocity
            is_moving = True
            print(f"Moving backward at velocity {current_velocity:.1f}   ")
        
        elif key in ('a', 'A', readchar.key.LEFT):
            current_left_vel = -current_velocity
            current_right_vel = current_velocity
            is_moving = True
            print(f"Turning left at velocity {current_velocity:.1f}      ")
        
        elif key in ('d', 'D', readchar.key.RIGHT):
            current_left_vel = current_velocity
            current_right_vel = -current_velocity
            is_moving = True
            print(f"Turning right at velocity {current_velocity:.1f}     ")
        
        elif key == ' ':  # Space
            if is_moving:
                current_left_vel = 0.0
                current_right_vel = 0.0
                is_moving = False
                print("Stopped                                  ")
                # Use stop_robot to set to IDLE mode
                stop_robot(odrv)
                # Need to re-enter closed loop control for next movement
                enter_closed_loop_control(odrv)
        
        elif key in ('+', '='):
            current_velocity = min(current_velocity + VELOCITY_INCREMENT, MAX_VELOCITY)
            print(f"Velocity increased to {current_velocity:.1f}          ")
        
        elif key in ('-', '_'):
            current_velocity = max(current_velocity - VELOCITY_INCREMENT, VELOCITY_INCREMENT)
            print(f"Velocity decreased to {current_velocity:.1f}          ")
        
        elif key in ('q', 'Q', readchar.key.ESC):
            break
        
        # If moving, set the velocity
        if is_moving:
            set_direct_velocity(odrv, current_left_vel, current_right_vel)
    
    # Make sure to stop the robot before exiting
    stop_robot(odrv)
    print("\nExited arrow key control mode.")
    return True

def main():
    """Main function."""
    print("Arrow Key Controller for ODrive")
    print("This script allows controlling an ODrive-powered differential drive robot using arrow keys.")
    
    # Connect to ODrive
    try:
        odrv = connect_to_odrive()
    except Exception as e:
        print(f"Error connecting to ODrive: {e}")
        sys.exit(1)
    
    # Run arrow key control
    try:
        arrow_key_control(odrv)
    except Exception as e:
        print(f"Error during arrow key control: {e}")
        # Make sure to stop the robot if there's an error
        stop_robot(odrv)
        sys.exit(1)

if __name__ == "__main__":
    main()
