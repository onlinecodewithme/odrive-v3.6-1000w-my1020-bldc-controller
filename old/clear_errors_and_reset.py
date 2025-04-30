#!/usr/bin/env python3
"""
ODrive error clearing and reset script.
This script clears all errors and properly resets the ODrive.
Copy and paste these commands into odrivetool to execute them.
"""

# Connect to ODrive
import odrive
odrv0 = odrive.find_any()

# Function to dump errors
def dump_errors(odrv):
    print("System errors:")
    print(f"  {odrv.error}")
    
    print("\nAxis 0 errors:")
    print(f"  axis: {odrv.axis0.error}")
    print(f"  motor: {odrv.axis0.motor.error}")
    print(f"  encoder: {odrv.axis0.encoder.error}")
    print(f"  controller: {odrv.axis0.controller.error}")
    
    print("\nAxis 1 errors:")
    print(f"  axis: {odrv.axis1.error}")
    print(f"  motor: {odrv.axis1.motor.error}")
    print(f"  encoder: {odrv.axis1.encoder.error}")
    print(f"  controller: {odrv.axis1.controller.error}")

# Print current errors
print("Current errors:")
dump_errors(odrv0)

# Clear all errors
print("\nClearing all errors...")

# Clear system error
odrv0.clear_errors()

# Clear axis 0 errors
odrv0.axis0.error = 0
odrv0.axis0.motor.error = 0
odrv0.axis0.encoder.error = 0
odrv0.axis0.controller.error = 0

# Clear axis 1 errors
odrv0.axis1.error = 0
odrv0.axis1.motor.error = 0
odrv0.axis1.encoder.error = 0
odrv0.axis1.controller.error = 0

# Print errors after clearing
print("\nErrors after clearing:")
dump_errors(odrv0)

# Reset to idle state
print("\nSetting axes to idle state...")
odrv0.axis0.requested_state = 1  # AXIS_STATE_IDLE
odrv0.axis1.requested_state = 1  # AXIS_STATE_IDLE

# Restore original configuration
print("\nRestoring original configuration...")

# Restore controller parameters
odrv0.axis0.controller.config.input_filter_bandwidth = 2.0  # Original value
odrv0.axis0.controller.config.vel_ramp_rate = 1.0  # Original value
odrv0.axis0.controller.config.vel_gain = 0.2  # Original value
odrv0.axis0.controller.config.vel_integrator_gain = 0.1  # Original value

# Restore velocity limit settings
odrv0.axis0.controller.config.enable_vel_limit = True  # Original value
odrv0.axis0.controller.config.vel_limit = 10.0  # Original value

# Restore startup behavior
odrv0.axis0.config.startup_closed_loop_control = False  # Original value

# Restore motor and encoder bandwidth settings
odrv0.axis0.motor.config.current_control_bandwidth = 1000.0  # Original value
odrv0.axis0.encoder.config.bandwidth = 1000.0  # Original value

# Restore encoder configuration
odrv0.axis0.encoder.config.mode = 0  # MODE_INCREMENTAL
odrv0.axis0.encoder.config.cpr = 4000  # Original value

# Save configuration
print("\nSaving configuration...")
odrv0.save_configuration()
print("Configuration saved. ODrive will reboot.")

# After reboot, run these commands to verify
"""
# Connect to ODrive again after reboot
import odrive
odrv0 = odrive.find_any()

# Check for errors
dump_errors(odrv0)

# Check configuration
print(f"Input filter bandwidth: {odrv0.axis0.controller.config.input_filter_bandwidth} Hz")
print(f"Velocity ramp rate: {odrv0.axis0.controller.config.vel_ramp_rate}")
print(f"Velocity gain: {odrv0.axis0.controller.config.vel_gain}")
print(f"Velocity integrator gain: {odrv0.axis0.controller.config.vel_integrator_gain}")
print(f"Enable velocity limit: {odrv0.axis0.controller.config.enable_vel_limit}")
print(f"Velocity limit: {odrv0.axis0.controller.config.vel_limit}")
print(f"Startup closed loop control: {odrv0.axis0.config.startup_closed_loop_control}")
print(f"Current control bandwidth: {odrv0.axis0.motor.config.current_control_bandwidth} Hz")
print(f"Encoder bandwidth: {odrv0.axis0.encoder.config.bandwidth} Hz")
print(f"Encoder CPR: {odrv0.axis0.encoder.config.cpr}")
"""
