#!/usr/bin/env python3
"""
Conservative final tuning script for ODrive to ensure immediate response at all velocities.
This script applies optimized parameter tuning without pushing the limits too far.
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
    print(f"Torque ramp rate: {odrv.axis0.controller.config.torque_ramp_rate}")
    print(f"Inertia: {odrv.axis0.controller.config.inertia}")

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

def conservative_tuning(odrv):
    """Apply conservative but effective tuning to ODrive parameters."""
    print("\nApplying conservative final parameter tuning...")
    
    # Store serial number for reconnection
    serial_number = str(odrv.serial_number)
    
    # 1. Motor current parameters - increase but stay within safe limits
    current_lim = min(70.0, odrv.axis0.motor.config.current_lim * 1.2)  # Increase by 20% or to 70A max
    odrv.axis0.motor.config.current_lim = current_lim
    odrv.axis0.motor.config.calibration_current = min(35.0, current_lim / 2)  # Half of current limit
    
    # 2. Controller parameters - optimize for consistent response across all velocities
    odrv.axis0.controller.config.input_filter_bandwidth = 150.0  # Significant reduction in filtering
    odrv.axis0.controller.config.vel_ramp_rate = 150.0  # Fast velocity ramping
    odrv.axis0.controller.config.vel_gain = 0.6  # Aggressive velocity gain
    odrv.axis0.controller.config.vel_integrator_gain = 0.3  # Increase integrator gain
    
    # 3. Velocity limits - adjust for better performance
    odrv.axis0.controller.config.vel_limit = 30.0  # Higher velocity limit
    odrv.axis0.controller.config.enable_vel_limit = False  # Disable velocity limiting
    odrv.axis0.controller.config.vel_limit_tolerance = 8.0  # Increase velocity limit tolerance
    
    # 4. Current control - increase bandwidth for faster current response
    odrv.axis0.motor.config.current_control_bandwidth = 2500.0  # Higher bandwidth
    
    # 5. Startup behavior - enable closed loop control at startup
    odrv.axis0.config.startup_closed_loop_control = True
    
    # 6. Encoder parameters - increase bandwidth for faster feedback
    odrv.axis0.encoder.config.bandwidth = 2500.0  # Higher encoder bandwidth
    
    # 7. Torque parameters - optimize for faster response
    odrv.axis0.controller.config.torque_ramp_rate = 0.05  # Increase torque ramp rate (default is 0.01)
    odrv.axis0.controller.config.inertia = 0.007  # Reduce inertia estimate for faster response
    
    # 8. Save configuration - this will cause the ODrive to reboot
    print("Saving configuration (ODrive will reboot)...")
    try:
        odrv.save_configuration()
        print("Configuration saved. ODrive is rebooting...")
    except:
        print("ODrive disconnected during save as expected. Waiting for reboot...")
    
    # 9. Wait for ODrive to come back online
    odrv = wait_for_odrive()
    
    # 10. Print new configuration
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
    print(f"Torque ramp rate: {odrv.axis0.controller.config.torque_ramp_rate}")
    print(f"Inertia: {odrv.axis0.controller.config.inertia}")
    
    return odrv

def comprehensive_test(odrv):
    """Perform comprehensive testing of motor response across all velocities."""
    print("\nPerforming comprehensive response time testing...")
    
    # Test a wide range of velocities
    test_velocities = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0]
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
    print("=== ODrive Conservative Final Tuning ===")
    
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Print current configuration
    print_current_config(odrv)
    
    # Apply conservative tuning
    odrv = conservative_tuning(odrv)
    
    # Perform comprehensive testing
    results = comprehensive_test(odrv)
    
    print("\nConservative final tuning complete. The motor should now respond immediately to all velocity commands.")
    print("If you experience instability or oscillations, you may need to reduce some of the gains.")
