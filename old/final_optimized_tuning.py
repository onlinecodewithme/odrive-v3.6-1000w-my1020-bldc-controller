#!/usr/bin/env python3
"""
Final optimized tuning script for ODrive to ensure immediate response at all velocities.
This script applies aggressive parameter tuning with additional optimizations for consistent response.
"""
import odrive
import time
import json
import sys

def connect_to_odrive():
    """Connect to the ODrive."""
    print("Looking for ODrive...")
    try:
        odrv0 = odrive.find_any()
        print(f"Found ODrive: {str(odrv0.serial_number)}")
        return odrv0
    except:
        print("Failed to find ODrive. Make sure it's connected and powered on.")
        sys.exit(1)

def print_current_config(odrv0):
    """Print current configuration parameters."""
    print("\nCurrent Configuration:")
    print(f"Motor current limit: {odrv0.axis0.motor.config.current_lim} A")
    print(f"Motor calibration current: {odrv0.axis0.motor.config.calibration_current} A")
    print(f"Input filter bandwidth: {odrv0.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv0.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv0.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv0.axis0.controller.config.vel_integrator_gain}")
    print(f"Position gain: {odrv0.axis0.controller.config.pos_gain}")
    print(f"Control mode: {odrv0.axis0.controller.config.control_mode}")
    print(f"Input mode: {odrv0.axis0.controller.config.input_mode}")
    print(f"Velocity limit: {odrv0.axis0.controller.config.vel_limit}")
    print(f"Enable velocity limit: {odrv0.axis0.controller.config.enable_vel_limit}")
    print(f"Current control bandwidth: {odrv0.axis0.motor.config.current_control_bandwidth} Hz")
    print(f"Startup closed loop control: {odrv0.axis0.config.startup_closed_loop_control}")
    print(f"Startup motor calibration: {odrv0.axis0.config.startup_motor_calibration}")
    print(f"Startup encoder offset calibration: {odrv0.axis0.config.startup_encoder_offset_calibration}")
    print(f"Encoder bandwidth: {odrv0.axis0.encoder.config.bandwidth} Hz")
    print(f"Torque ramp rate: {odrv0.axis0.controller.config.torque_ramp_rate}")
    print(f"Inertia: {odrv0.axis0.controller.config.inertia}")

def wait_for_odrive(timeout=30):
    """Wait for ODrive to come back online after reboot."""
    print("Waiting for ODrive to reboot...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            odrv0 = odrive.find_any(timeout=1)
            print(f"ODrive reconnected: {str(odrv0.serial_number)}")
            return odrv0
        except:
            print(".", end="", flush=True)
            time.sleep(1)
    
    print("\nTimeout waiting for ODrive to reconnect.")
    sys.exit(1)

def final_optimized_tuning(odrv0):
    """Apply final optimized tuning to ODrive parameters."""
    print("\nApplying final optimized parameter tuning...")
    
    # Store serial number for reconnection
    serial_number = str(odrv0.serial_number)
    
        # 1. Motor current parameters - maximize for immediate response
    odrv0.axis1.motor.config.current_lim = 40.0  # Further increase current limit
    odrv0.axis1.motor.config.calibration_current = 10.0  # Further increase calibration current

    # 2. Controller parameters - optimize for consistent response across all velocities
    odrv0.axis1.controller.config.input_filter_bandwidth = 200.0  # Extreme reduction in filtering
    odrv0.axis1.controller.config.vel_ramp_rate = 200.0  # Extremely fast velocity ramping
    # odrv0.axis1.controller.config.vel_gain = 0.8  # Very aggressive velocity gain
    # odrv0.axis1.controller.config.vel_integrator_gain = 0.4  # Increase integrator gain

    odrv0.axis0.controller.config.pos_gain = 50.0  # Much higher
    odrv0.axis0.controller.config.vel_gain = 0.1   # Slightly higher
    odrv0.axis0.controller.config.vel_integrator_gain = 0.2  # Higher for steady-state

    # 3. Velocity limits - remove limits for maximum acceleration
    odrv0.axis1.controller.config.vel_limit = 50.0  # Much higher velocity limit
    odrv0.axis1.controller.config.enable_vel_limit = False  # Disable velocity limiting
    odrv0.axis1.controller.config.vel_limit_tolerance = 10.0  # Increase velocity limit tolerance

    # 4. Current control - maximize bandwidth for fastest current response
    odrv0.axis1.motor.config.current_control_bandwidth = 4000.0  # Maximum bandwidth

    # 5. Startup behavior - enable closed loop control at startup
    odrv0.axis1.config.startup_closed_loop_control = True

    # 6. Encoder parameters - maximize bandwidth for fastest feedback
    odrv0.axis1.encoder.config.bandwidth = 4000.0  # Maximum encoder bandwidth

    # 7. Torque parameters - optimize for faster response
    odrv0.axis1.controller.config.torque_ramp_rate = 0.1  # Increase torque ramp rate (default is 0.01)
    odrv0.axis1.controller.config.inertia = 0.005  # Reduce inertia estimate for faster response
    
    # 8. Save configuration - this will cause the ODrive to reboot
    print("Saving configuration (ODrive will reboot)...")
    try:
        odrv0.save_configuration()
        print("Configuration saved. ODrive is rebooting...")
    except:
        print("ODrive disconnected during save as expected. Waiting for reboot...")
    
    # 9. Wait for ODrive to come back online
    odrv0 = wait_for_odrive()
    
    # 10. Print new configuration
    print("\nNew Configuration:")
    print(f"Motor current limit: {odrv0.axis0.motor.config.current_lim} A")
    print(f"Motor calibration current: {odrv0.axis0.motor.config.calibration_current} A")
    print(f"Input filter bandwidth: {odrv0.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv0.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv0.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv0.axis0.controller.config.vel_integrator_gain}")
    print(f"Position gain: {odrv0.axis0.controller.config.pos_gain}")
    print(f"Control mode: {odrv0.axis0.controller.config.control_mode}")
    print(f"Input mode: {odrv0.axis0.controller.config.input_mode}")
    print(f"Velocity limit: {odrv0.axis0.controller.config.vel_limit}")
    print(f"Enable velocity limit: {odrv0.axis0.controller.config.enable_vel_limit}")
    print(f"Current control bandwidth: {odrv0.axis0.motor.config.current_control_bandwidth} Hz")
    print(f"Startup closed loop control: {odrv0.axis0.config.startup_closed_loop_control}")
    print(f"Startup motor calibration: {odrv0.axis0.config.startup_motor_calibration}")
    print(f"Startup encoder offset calibration: {odrv0.axis0.config.startup_encoder_offset_calibration}")
    print(f"Encoder bandwidth: {odrv0.axis0.encoder.config.bandwidth} Hz")
    print(f"Torque ramp rate: {odrv0.axis0.controller.config.torque_ramp_rate}")
    print(f"Inertia: {odrv0.axis0.controller.config.inertia}")
    
    return odrv0

def comprehensive_test(odrv0):
    """Perform comprehensive testing of motor response across all velocities."""
    print("\nPerforming comprehensive response time testing...")
    
    # Test a wide range of velocities
    test_velocities = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0]
    results = []
    
    for vel in test_velocities:
        print(f"\nTesting velocity: {vel}")
        
        # Stop the motor first
        print("Stopping motor...")
        odrv0.axis0.controller.input_vel = 0.0
        time.sleep(1)
        
        # Send velocity command and measure response time
        print(f"Setting velocity to {vel}...")
        start_time = time.time()
        odrv0.axis0.controller.input_vel = vel
        
        # Wait for motor to start moving
        vel_threshold = vel * 0.05  # 5% of target velocity
        response_time = None
        max_velocity = 0.0
        
        # Monitor for 2 seconds
        timeout = 2.0
        while time.time() - start_time < timeout:
            current_vel = abs(odrv0.axis0.encoder.vel_estimate)
            
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
        odrv0.axis0.controller.input_vel = 0.0
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
    print("=== ODrive Final Optimized Tuning ===")
    
    # Connect to ODrive
    odrv0 = connect_to_odrive()
    
    # Print current configuration
    print_current_config(odrv0)
    
    # Apply final optimized tuning
    odrv0 = final_optimized_tuning(odrv0)
    
    # Perform comprehensive testing
    results = comprehensive_test(odrv0)
    
    print("\nFinal optimized tuning complete. The motor should now respond immediately to all velocity commands.")
    print("If you experience instability or oscillations, you may need to reduce some of the gains.")
