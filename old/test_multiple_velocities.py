#!/usr/bin/env python3
"""
Script to test multiple velocity commands on ODrive and measure response times.
This script automatically tests a range of velocities to verify consistent fast response.
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

def test_velocity(odrv, velocity, wait_time=5.0):
    """Test a velocity command and measure response time."""
    print(f"\nTesting velocity: {velocity:.2f}")
    
    # First stop the motor
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    # Send the velocity command and measure response time
    start_time = time.time()
    odrv.axis0.controller.input_vel = velocity
    
    # Wait for motor to start moving
    vel_threshold = abs(velocity) * 0.05  # Consider motor responding when it reaches 5% of target velocity
    response_time = None
    
    # Sample velocity for plotting
    times = []
    velocities = []
    start_sample_time = time.time()
    
    while time.time() - start_time < wait_time:
        current_vel = abs(odrv.axis0.encoder.vel_estimate)
        current_time = time.time() - start_sample_time
        
        # Record for plotting
        times.append(current_time)
        velocities.append(current_vel)
        
        # Check if we've reached threshold and haven't recorded response time yet
        if response_time is None and current_vel >= vel_threshold:
            response_time = time.time() - start_time
            print(f"Response time: {response_time:.3f} seconds")
        
        time.sleep(0.01)  # Sample at 100Hz
    
    # If we never reached the threshold
    if response_time is None:
        response_time = float('inf')
        print("Motor did not reach threshold velocity within timeout period.")
    
    # Get the maximum velocity reached
    max_velocity = max(velocities) if velocities else 0
    print(f"Maximum velocity reached: {max_velocity:.2f}")
    
    # Stop the motor
    odrv.axis0.controller.input_vel = 0.0
    time.sleep(1)
    
    return response_time, times, velocities, max_velocity

def test_velocity_range(odrv, min_vel=4.0, max_vel=10.0, steps=7):
    """Test a range of velocities and measure response times."""
    # Check velocity limit in ODrive configuration
    vel_limit = odrv.axis0.controller.config.vel_limit
    print(f"ODrive velocity limit: {vel_limit}")
    
    # Adjust max_vel if it exceeds the ODrive velocity limit
    if max_vel > vel_limit:
        print(f"Adjusting max velocity from {max_vel} to {vel_limit} (ODrive limit)")
        max_vel = vel_limit
    # Generate velocity values
    velocities = []
    step_size = (max_vel - min_vel) / (steps - 1) if steps > 1 else 0
    for i in range(steps):
        velocities.append(min_vel + i * step_size)
    
    response_times = []
    all_times = []
    all_velocities = []
    
    print(f"Testing {steps} different velocities from {min_vel} to {max_vel}...")
    
    max_velocities_reached = []
    
    for vel in velocities:
        response_time, times, vels, max_vel = test_velocity(odrv, vel)
        response_times.append(response_time)
        all_times.append(times)
        all_velocities.append(vels)
        max_velocities_reached.append(max_vel)
    
    return velocities, response_times, all_times, all_velocities, max_velocities_reached

def save_results(velocities, response_times, max_velocities_reached):
    """Save the test results to a CSV file."""
    # Save the data as CSV
    with open('velocity_test_results.csv', 'w') as f:
        f.write('Target Velocity,Response Time (seconds),Max Velocity Reached\n')
        for vel, resp, max_vel in zip(velocities, response_times, max_velocities_reached):
            f.write(f'{vel:.2f},{resp:.4f},{max_vel:.2f}\n')
    print("Data saved to velocity_test_results.csv")

if __name__ == "__main__":
    # Connect to ODrive
    odrv = connect_to_odrive()
    
    # Parse command line arguments
    if len(sys.argv) > 3:
        min_vel = float(sys.argv[1])
        max_vel = float(sys.argv[2])
        steps = int(sys.argv[3])
        velocities, response_times, all_times, all_velocities, max_velocities_reached = test_velocity_range(odrv, min_vel, max_vel, steps)
    else:
        # Default test range
        velocities, response_times, all_times, all_velocities, max_velocities_reached = test_velocity_range(odrv)
    
    # Save results
    save_results(velocities, response_times, max_velocities_reached)
    
    # Print summary
    print("\nTest Summary:")
    print("Velocity | Response Time | Max Velocity")
    print("---------------------------------------")
    for vel, resp, max_vel in zip(velocities, response_times, max_velocities_reached):
        print(f"{vel:7.2f} | {resp:12.4f} seconds | {max_vel:7.2f}")
    
    # Calculate average response time
    avg_response = sum(response_times) / len(response_times)
    print(f"\nAverage response time: {avg_response:.4f} seconds")
    
    # Stop the motor
    print("\nStopping motor...")
    odrv.axis0.controller.input_vel = 0.0
