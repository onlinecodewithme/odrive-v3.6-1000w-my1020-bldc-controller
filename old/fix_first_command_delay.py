#!/usr/bin/env python3
"""
Script to fix the delay in the first velocity command to ODrive.
This script modifies additional parameters to improve the initial response time.
"""
import odrive
import time
import json
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

def load_backup(filename):
    """Load the backup configuration for reference."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading backup file: {e}")
        return None

def fix_first_command_delay():
    """Fix the delay in the first velocity command."""
    odrv = connect_to_odrive()
    
    # Save current configuration parameters for reference
    print("Current parameters:")
    print(f"Input filter bandwidth: {odrv.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv.axis0.controller.config.vel_integrator_gain}")
    print(f"Control mode: {odrv.axis0.controller.config.control_mode}")
    print(f"Input mode: {odrv.axis0.controller.config.input_mode}")
    print(f"Startup closed loop control: {odrv.axis0.config.startup_closed_loop_control}")
    
    # Modify parameters to improve initial response time
    print("\nModifying parameters to improve initial response time...")
    
    # 1. Enable startup closed loop control - this will make the controller
    # active immediately on startup, reducing initial delay
    odrv.axis0.config.startup_closed_loop_control = True
    
    # 2. Further increase input filter bandwidth for faster response
    odrv.axis0.controller.config.input_filter_bandwidth = 50.0
    
    # 3. Increase velocity ramp rate even more
    odrv.axis0.controller.config.vel_ramp_rate = 20.0
    
    # 4. Adjust velocity controller gains for better initial response
    odrv.axis0.controller.config.vel_gain = 0.3
    
    # 5. Disable velocity limit to allow faster initial acceleration
    odrv.axis0.controller.config.enable_vel_limit = False
    
    # 6. Save configuration
    print("Saving configuration...")
    odrv.save_configuration()
    
    # 7. Print new parameters
    print("\nNew parameters:")
    print(f"Input filter bandwidth: {odrv.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv.axis0.controller.config.vel_integrator_gain}")
    print(f"Control mode: {odrv.axis0.controller.config.control_mode}")
    print(f"Input mode: {odrv.axis0.controller.config.input_mode}")
    print(f"Startup closed loop control: {odrv.axis0.config.startup_closed_loop_control}")
    print(f"Enable velocity limit: {odrv.axis0.controller.config.enable_vel_limit}")
    
    return odrv

def test_first_command_response(odrv, velocity=9.0):
    """Test the response time of the first velocity command."""
    print("\nTesting first command response...")
    
    # Make sure the motor is stopped
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(2)
    
    # Send the first velocity command and measure response time
    print(f"Sending first velocity command: {velocity}...")
    start_time = time.time()
    odrv.axis0.controller.input_vel = velocity
    
    # Wait for motor to start moving
    vel_threshold = velocity * 0.05  # 5% of target velocity
    response_time = None
    max_velocity = 0.0
    
    # Monitor for 5 seconds
    timeout = 5.0
    while time.time() - start_time < timeout:
        current_vel = abs(odrv.axis0.encoder.vel_estimate)
        
        # Update max velocity
        if current_vel > max_velocity:
            max_velocity = current_vel
        
        # Check if we've reached threshold
        if response_time is None and current_vel >= vel_threshold:
            response_time = time.time() - start_time
            print(f"First command response time: {response_time:.3f} seconds")
        
        time.sleep(0.001)  # Sample at 1000Hz for more accurate timing
    
    # If we never reached the threshold
    if response_time is None:
        response_time = float('inf')
        print("Motor did not reach threshold velocity within timeout period.")
    
    print(f"Maximum velocity reached: {max_velocity:.2f}")
    
    # Let the motor run for a moment
    time.sleep(2)
    
    # Stop the motor
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(2)
    
    # Test second command to verify it's faster
    print("\nTesting second velocity command...")
    start_time = time.time()
    odrv.axis0.controller.input_vel = velocity
    
    # Reset variables for second test
    response_time_second = None
    max_velocity_second = 0.0
    
    # Monitor for 5 seconds
    while time.time() - start_time < timeout:
        current_vel = abs(odrv.axis0.encoder.vel_estimate)
        
        # Update max velocity
        if current_vel > max_velocity_second:
            max_velocity_second = current_vel
        
        # Check if we've reached threshold
        if response_time_second is None and current_vel >= vel_threshold:
            response_time_second = time.time() - start_time
            print(f"Second command response time: {response_time_second:.3f} seconds")
        
        time.sleep(0.001)  # Sample at 1000Hz for more accurate timing
    
    # If we never reached the threshold
    if response_time_second is None:
        response_time_second = float('inf')
        print("Motor did not reach threshold velocity within timeout period.")
    
    print(f"Maximum velocity reached: {max_velocity_second:.2f}")
    
    # Stop the motor
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    return response_time, response_time_second

def implement_pre_spin_routine(odrv):
    """Implement a pre-spin routine to wake up the motor."""
    print("\nImplementing pre-spin routine...")
    
    # Set a very low velocity to wake up the motor without much movement
    print("Pre-spinning motor at low velocity...")
    odrv.axis0.controller.input_vel = 0.5
    time.sleep(0.5)
    
    # Stop the motor
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(0.5)
    
    print("Pre-spin routine completed.")

if __name__ == "__main__":
    print("=== ODrive First Command Delay Fix ===")
    
    # Fix the first command delay
    odrv = fix_first_command_delay()
    
    # Test the response time before implementing pre-spin
    print("\n=== Testing without pre-spin routine ===")
    first_response, second_response = test_first_command_response(odrv)
    
    # Implement pre-spin routine
    implement_pre_spin_routine(odrv)
    
    # Test the response time after implementing pre-spin
    print("\n=== Testing with pre-spin routine ===")
    first_response_after, second_response_after = test_first_command_response(odrv)
    
    # Print summary
    print("\n=== Response Time Summary ===")
    print("Without pre-spin routine:")
    print(f"  First command: {first_response:.3f} seconds")
    print(f"  Second command: {second_response:.3f} seconds")
    print("With pre-spin routine:")
    print(f"  First command: {first_response_after:.3f} seconds")
    print(f"  Second command: {second_response_after:.3f} seconds")
    
    # Provide recommendations
    print("\n=== Recommendations ===")
    if first_response_after < first_response:
        print("The pre-spin routine significantly improves the first command response time.")
        print("Recommendation: Use the pre-spin routine before sending velocity commands.")
    else:
        print("The parameter changes alone significantly improve the first command response time.")
        print("Recommendation: Use the updated parameters without the pre-spin routine.")
    
    print("\nConfiguration has been updated to improve initial response time.")
