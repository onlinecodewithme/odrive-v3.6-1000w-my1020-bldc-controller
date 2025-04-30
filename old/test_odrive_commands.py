#!/usr/bin/env python3
"""
Script to test ODrive velocity commands with improved response time.
This script provides a simple interface to send velocity commands to the ODrive
and observe the response time.
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

def test_velocity_command(odrv, velocity):
    """Test a velocity command and measure response time."""
    print(f"\nTesting velocity command: {velocity}")
    
    # First stop the motor
    print("Setting velocity to 0...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    # Send the velocity command and measure response time
    print(f"Setting velocity to {velocity} and measuring response time...")
    start_time = time.time()
    odrv.axis0.controller.input_vel = velocity
    
    # Wait for motor to start moving
    vel_threshold = abs(velocity) * 0.25  # Consider motor responding when it reaches 25% of target velocity
    while abs(odrv.axis0.encoder.vel_estimate) < vel_threshold:
        time.sleep(0.001)  # Check every 1ms
        # Add timeout to prevent infinite loop
        if time.time() - start_time > 5:
            print("Timeout waiting for motor response!")
            break
    
    response_time = time.time() - start_time
    print(f"Motor response time: {response_time:.3f} seconds")
    
    # Print current velocity
    print(f"Current velocity: {odrv.axis0.encoder.vel_estimate:.2f}")
    
    # Let motor run for a moment
    time.sleep(2)
    
    # Print final velocity
    print(f"Final velocity: {odrv.axis0.encoder.vel_estimate:.2f}")
    
    return response_time

def interactive_mode(odrv):
    """Interactive mode to test different velocity commands."""
    print("\n=== ODrive Velocity Command Tester ===")
    print("Enter velocity values to test (or 'q' to quit)")
    
    while True:
        user_input = input("\nEnter velocity (or 'q' to quit): ")
        
        if user_input.lower() == 'q':
            # Stop the motor before quitting
            print("Stopping motor...")
            odrv.axis0.controller.input_vel = 0.0
            time.sleep(1)
            break
        
        try:
            velocity = float(user_input)
            test_velocity_command(odrv, velocity)
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")

if __name__ == "__main__":
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    if len(sys.argv) > 1:
        # If velocity is provided as command line argument
        try:
            velocity = float(sys.argv[1])
            test_velocity_command(odrv, velocity)
            # Stop the motor
            print("Stopping motor...")
            odrv.axis0.controller.input_vel = 0.0
        except ValueError:
            print(f"Invalid velocity value: {sys.argv[1]}")
    else:
        # Interactive mode
        interactive_mode(odrv)
    
    print("\nTest completed. Motor stopped.")
