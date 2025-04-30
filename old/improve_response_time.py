#!/usr/bin/env python3
"""
Script to improve ODrive response time by modifying key parameters.
"""
import odrive
import time
import json
from datetime import datetime

def load_backup(filename):
    """Load the backup configuration for reference."""
    with open(filename, 'r') as f:
        return json.load(f)

def improve_response_time():
    print("Looking for ODrive...")
    odrv = odrive.find_any()
    print(f"Found ODrive: {str(odrv.serial_number)}")
    
    # Save current configuration parameters for reference
    print("Current parameters:")
    print(f"Input filter bandwidth: {odrv.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv.axis0.controller.config.vel_integrator_gain}")
    print(f"Control mode: {odrv.axis0.controller.config.control_mode}")
    print(f"Input mode: {odrv.axis0.controller.config.input_mode}")
    print(f"Startup closed loop control: {odrv.axis0.config.startup_closed_loop_control}")
    print(f"Enable velocity limit: {odrv.axis0.controller.config.enable_vel_limit}")
    
    # Modify parameters to improve response time
    print("\nModifying parameters to improve response time...")
    
    # 1. Increase input filter bandwidth (higher = less filtering = faster response)
    # Default is 2.0 Hz, increase to 50 Hz for much faster response
    odrv.axis0.controller.config.input_filter_bandwidth = 50.0
    
    # 2. Increase velocity ramp rate (higher = faster acceleration)
    # Default is 1.0, increase to 20.0 for faster acceleration
    odrv.axis0.controller.config.vel_ramp_rate = 20.0
    
    # 3. Adjust velocity controller gains for better response
    # Increase vel_gain for more aggressive response
    odrv.axis0.controller.config.vel_gain = 0.3
    
    # 4. Enable startup closed loop control for faster initial response
    odrv.axis0.config.startup_closed_loop_control = True
    
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
    
    # 8. Implement pre-spin routine to wake up the motor
    print("\nImplementing pre-spin routine to wake up the motor...")
    implement_pre_spin_routine(odrv)
    
    return odrv

def implement_pre_spin_routine(odrv):
    """Implement a pre-spin routine to wake up the motor."""
    print("Pre-spinning motor at low velocity...")
    odrv.axis0.controller.input_vel = 0.5
    time.sleep(0.5)
    
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(0.5)
    
    print("Pre-spin routine completed.")

def test_response_time(odrv):
    """Test the response time of the motor."""
    print("\nTesting motor response time...")
    print("Setting velocity to 0...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    print("Setting velocity to 9.0 and measuring response time...")
    start_time = time.time()
    odrv.axis0.controller.input_vel = 9.0
    
    # Wait for motor to start moving
    vel_threshold = 0.9  # Consider motor responding when it reaches 10% of target velocity
    while abs(odrv.axis0.encoder.vel_estimate) < vel_threshold:
        time.sleep(0.01)
        # Add timeout to prevent infinite loop
        if time.time() - start_time > 5:
            print("Timeout waiting for motor response!")
            break
    
    response_time = time.time() - start_time
    print(f"Motor response time: {response_time:.3f} seconds")
    
    # Let motor run for a moment
    time.sleep(2)
    
    # Stop motor
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    return response_time

if __name__ == "__main__":
    # Load the backup for reference
    backup_file = "odrive_backup_20250430_000203.json"
    backup_config = load_backup(backup_file)
    
    # Improve response time
    odrv = improve_response_time()
    
    # Test the response time
    response_time = test_response_time(odrv)
    
    print("\nConfiguration has been updated to improve response time.")
    print("You can now test the motor response by sending velocity commands.")
    print("Example: odrv0.axis0.controller.input_vel = 2.0")
