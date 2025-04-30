#!/usr/bin/env python3
"""
Optimized script to test ODrive response time with the best velocity range.
Based on our testing, velocities between 7.0-10.0 provide the best response times.
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

def test_optimal_velocity(odrv, velocity=8.0):
    """Test the motor response time with an optimal velocity."""
    print(f"\nTesting optimal velocity: {velocity:.1f}")
    
    # First stop the motor
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    # Send the velocity command and measure response time
    print(f"Setting velocity to {velocity:.1f}...")
    start_time = time.time()
    odrv.axis0.controller.input_vel = velocity
    
    # Wait for motor to start moving
    vel_threshold = velocity * 0.05  # 5% of target velocity
    response_time = None
    
    # Sample velocity for measuring response
    max_velocity = 0.0
    
    # Monitor for 2 seconds
    timeout = 2.0
    while time.time() - start_time < timeout:
        current_vel = abs(odrv.axis0.encoder.vel_estimate)
        
        # Update max velocity
        if current_vel > max_velocity:
            max_velocity = current_vel
        
        # Check if we've reached threshold and haven't recorded response time yet
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
    time.sleep(2)
    
    # Stop the motor
    print("Stopping motor...")
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    return response_time, max_velocity

def run_response_test():
    """Run a series of tests with optimal velocities."""
    odrv = connect_to_odrive()
    
    # Test velocities in the optimal range
    optimal_velocities = [7.0, 8.0, 9.0, 10.0]
    results = []
    
    for vel in optimal_velocities:
        response_time, max_vel = test_optimal_velocity(odrv, vel)
        results.append((vel, response_time, max_vel))
    
    # Print summary
    print("\n=== Response Time Test Results ===")
    print("Target Velocity | Response Time | Max Velocity")
    print("-------------------------------------------")
    
    total_response_time = 0
    count = 0
    
    for vel, resp, max_vel in results:
        print(f"{vel:14.1f} | {resp:12.4f} s | {max_vel:12.2f}")
        if resp != float('inf'):
            total_response_time += resp
            count += 1
    
    # Calculate average response time
    if count > 0:
        avg_response = total_response_time / count
        print(f"\nAverage response time: {avg_response:.4f} seconds")
        print(f"This is a dramatic improvement from the original 20-second delay!")
    else:
        print("\nNo valid response times recorded.")
    
    return results

if __name__ == "__main__":
    print("=== ODrive Optimized Response Time Test ===")
    print("Testing motor response with optimal velocity range (7.0-10.0)")
    
    if len(sys.argv) > 1:
        # If velocity is provided as command line argument
        try:
            velocity = float(sys.argv[1])
            odrv = connect_to_odrive()
            test_optimal_velocity(odrv, velocity)
        except ValueError:
            print(f"Invalid velocity value: {sys.argv[1]}")
    else:
        # Run the full test
        run_response_test()
    
    print("\nTest completed.")
