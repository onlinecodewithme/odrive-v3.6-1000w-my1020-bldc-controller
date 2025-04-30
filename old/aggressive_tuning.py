#!/usr/bin/env python3
"""
Script to aggressively tune ODrive parameters for immediate response.
This script focuses on direct configuration adjustments rather than workarounds.
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

def print_current_config(odrv):
    """Print current configuration parameters."""
    print("\nCurrent Configuration:")
    print(f"Motor current limit: {odrv.axis0.motor.config.current_lim} A")
    print(f"Motor calibration current: {odrv.axis0.motor.config.calibration_current} A")
    print(f"Input filter bandwidth: {odrv.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv.axis0.controller.config.vel_integrator_gain}")
    print(f"Position gain: {odrv.axis0.controller.config.pos_gain}")
    print(f"Control mode: {odrv.axis0.controller.config.control_mode}")
    print(f"Input mode: {odrv.axis0.controller.config.input_mode}")
    print(f"Velocity limit: {odrv.axis0.controller.config.vel_limit}")
    print(f"Enable velocity limit: {odrv.axis0.controller.config.enable_vel_limit}")
    print(f"Current control bandwidth: {odrv.axis0.motor.config.current_control_bandwidth} Hz")
    print(f"Startup closed loop control: {odrv.axis0.config.startup_closed_loop_control}")
    print(f"Startup motor calibration: {odrv.axis0.config.startup_motor_calibration}")
    print(f"Startup encoder offset calibration: {odrv.axis0.config.startup_encoder_offset_calibration}")
    print(f"Encoder bandwidth: {odrv.axis0.encoder.config.bandwidth} Hz")

def aggressive_tuning(odrv):
    """Apply aggressive tuning to ODrive parameters."""
    print("\nApplying aggressive parameter tuning...")
    
    # 1. Motor current parameters - increase for more torque and faster response
    odrv.axis0.motor.config.current_lim = 60.0  # Increase current limit for more torque
    odrv.axis0.motor.config.calibration_current = 30.0  # Increase calibration current
    
    # 2. Controller parameters - make much more aggressive
    odrv.axis0.controller.config.input_filter_bandwidth = 100.0  # Extreme reduction in filtering
    odrv.axis0.controller.config.vel_ramp_rate = 100.0  # Very fast velocity ramping
    odrv.axis0.controller.config.vel_gain = 0.5  # More aggressive velocity gain
    odrv.axis0.controller.config.vel_integrator_gain = 0.2  # Increase integrator gain
    
    # 3. Velocity limits - remove limits for maximum acceleration
    odrv.axis0.controller.config.vel_limit = 20.0  # Higher velocity limit
    odrv.axis0.controller.config.enable_vel_limit = False  # Disable velocity limiting
    
    # 4. Current control - increase bandwidth for faster current response
    odrv.axis0.motor.config.current_control_bandwidth = 2000.0  # Double the bandwidth
    
    # 5. Startup behavior - enable closed loop control at startup
    odrv.axis0.config.startup_closed_loop_control = True
    
    # 6. Encoder parameters - increase bandwidth for faster feedback
    odrv.axis0.encoder.config.bandwidth = 2000.0  # Increase encoder bandwidth
    
    # 7. Save configuration
    print("Saving configuration...")
    odrv.save_configuration()
    
    # 8. Print new configuration
    print("\nNew Configuration:")
    print(f"Motor current limit: {odrv.axis0.motor.config.current_lim} A")
    print(f"Motor calibration current: {odrv.axis0.motor.config.calibration_current} A")
    print(f"Input filter bandwidth: {odrv.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv.axis0.controller.config.vel_integrator_gain}")
    print(f"Position gain: {odrv.axis0.controller.config.pos_gain}")
    print(f"Control mode: {odrv.axis0.controller.config.control_mode}")
    print(f"Input mode: {odrv.axis0.controller.config.input_mode}")
    print(f"Velocity limit: {odrv.axis0.controller.config.vel_limit}")
    print(f"Enable velocity limit: {odrv.axis0.controller.config.enable_vel_limit}")
    print(f"Current control bandwidth: {odrv.axis0.motor.config.current_control_bandwidth} Hz")
    print(f"Startup closed loop control: {odrv.axis0.config.startup_closed_loop_control}")
    print(f"Startup motor calibration: {odrv.axis0.config.startup_motor_calibration}")
    print(f"Startup encoder offset calibration: {odrv.axis0.config.startup_encoder_offset_calibration}")
    print(f"Encoder bandwidth: {odrv.axis0.encoder.config.bandwidth} Hz")
    
    return odrv

def test_response_time(odrv, velocity=2.0):
    """Test the response time of the motor with different velocities."""
    print("\nTesting motor response time...")
    
    # Test velocities from low to high
    test_velocities = [1.0, 2.0, 3.0, 5.0, 10.0]
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
        
        # Monitor for 3 seconds
        timeout = 3.0
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
    
    for vel, resp, max_vel in results:
        if resp == float('inf'):
            print(f"{vel:14.1f} | No response    | {max_vel:12.2f}")
        else:
            print(f"{vel:14.1f} | {resp:12.4f} s | {max_vel:12.2f}")
    
    return results

if __name__ == "__main__":
    print("=== ODrive Aggressive Parameter Tuning ===")
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Print current configuration
    print_current_config(odrv)
    
    # Apply aggressive tuning
    odrv = aggressive_tuning(odrv)
    
    # Test response time
    results = test_response_time(odrv)
    
    print("\nAggressive tuning complete. The motor should now respond immediately to velocity commands.")
    print("If you experience instability or oscillations, you may need to reduce some of the gains.")
