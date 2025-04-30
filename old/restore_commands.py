#!/usr/bin/env python3
"""
ODrive restoration commands.
This script contains commands to restore the ODrive to its original configuration.
Copy and paste these commands into odrivetool to execute them.
"""

# Connect to ODrive
import odrive
odrv0 = odrive.find_any()

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

# Save configuration (this will cause the ODrive to reboot)
odrv0.save_configuration()

# Verification commands (run these after ODrive reboots)
"""
# Check controller parameters
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
