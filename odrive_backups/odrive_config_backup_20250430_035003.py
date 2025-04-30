#!/usr/bin/env python3
"""
ODrive configuration backup as commands - 20250430_035003
Copy and paste these commands into odrivetool to restore the configuration.
"""

# Connect to ODrive
import odrive
import time
odrv0 = odrive.find_any()

# Clear any errors before configuration
print("Clearing errors...")
odrv0.clear_errors()

# Axis 0 configuration
print("Configuring axis 0...")

# Motor configuration
odrv0.axis0.motor.config.pole_pairs = 3
odrv0.axis0.motor.config.resistance_calib_max_voltage = 2.0
odrv0.axis0.motor.config.requested_current_range = 60.0
odrv0.axis0.motor.config.current_control_bandwidth = 4000.0
odrv0.axis0.motor.config.torque_constant = 0.03999999910593033
odrv0.axis0.motor.config.motor_type = 0
odrv0.axis0.motor.config.calibration_current = 10.0
odrv0.axis0.motor.config.current_lim = 40.0
odrv0.axis0.motor.config.pre_calibrated = False

# Encoder configuration
odrv0.axis0.encoder.config.mode = 0
odrv0.axis0.encoder.config.use_index = False
odrv0.axis0.encoder.config.cpr = 4000
odrv0.axis0.encoder.config.bandwidth = 4000.0
odrv0.axis0.encoder.config.calib_range = 0.019999999552965164
odrv0.axis0.encoder.config.calib_scan_distance = 50.26548385620117
odrv0.axis0.encoder.config.calib_scan_omega = 12.566370964050293
odrv0.axis0.encoder.config.pre_calibrated = False

# Controller configuration
odrv0.axis0.controller.config.control_mode = 2
odrv0.axis0.controller.config.input_mode = 1
odrv0.axis0.controller.config.pos_gain = 50.0
odrv0.axis0.controller.config.vel_gain = 0.10000000149011612
odrv0.axis0.controller.config.vel_integrator_gain = 0.20000000298023224
odrv0.axis0.controller.config.vel_limit = 50.0
odrv0.axis0.controller.config.vel_ramp_rate = 200.0
odrv0.axis0.controller.config.input_filter_bandwidth = 200.0
odrv0.axis0.controller.config.enable_vel_limit = False
odrv0.axis0.controller.config.enable_torque_mode_vel_limit = True
odrv0.axis0.controller.config.enable_gain_scheduling = False
odrv0.axis0.controller.config.enable_overspeed_error = True

# Axis configuration
odrv0.axis0.config.startup_motor_calibration = False
odrv0.axis0.config.startup_encoder_index_search = False
odrv0.axis0.config.startup_encoder_offset_calibration = False
odrv0.axis0.config.startup_closed_loop_control = True
odrv0.axis0.config.enable_step_dir = False
odrv0.axis0.config.enable_watchdog = False
odrv0.axis0.config.watchdog_timeout = 0.0

# Save configuration
print("Saving configuration...")
try:
    odrv0.save_configuration()
    print("Configuration saved. ODrive will reboot.")
except Exception as e:
    print(f"Exception during save: {e}")
    print("ODrive disconnected during save as expected.")
