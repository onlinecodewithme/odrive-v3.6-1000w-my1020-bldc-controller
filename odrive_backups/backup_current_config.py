#!/usr/bin/env python3
"""
ODrive current configuration backup as commands.
This script connects to the ODrive device, reads the current configuration,
and saves it as odrivetool commands that can be copied and pasted.
"""
import odrive
import time
import datetime
import os

def backup_odrive_config():
    print("Connecting to ODrive...")
    try:
        odrv = odrive.find_any()
        print(f"Found ODrive: {str(odrv.serial_number)}")
    except:
        print("Failed to find ODrive. Make sure it's connected and powered on.")
        return
    
    # Create timestamp for the backup file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"odrive_config_backup_{timestamp}.py"
    backup_path = os.path.join("odrive_backups", backup_file)
    
    print(f"Creating backup file: {backup_path}")
    
    with open(backup_path, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""\n')
        f.write(f'ODrive configuration backup as commands - {timestamp}\n')
        f.write('Copy and paste these commands into odrivetool to restore the configuration.\n')
        f.write('"""\n\n')
        
        f.write('# Connect to ODrive\n')
        f.write('import odrive\n')
        f.write('import time\n')
        f.write('odrv0 = odrive.find_any()\n\n')
        
        f.write('# Clear any errors before configuration\n')
        f.write('print("Clearing errors...")\n')
        f.write('odrv0.clear_errors()\n\n')
        
        # Axis 0 configuration
        f.write('# Axis 0 configuration\n')
        f.write('print("Configuring axis 0...")\n\n')
        
        # Motor configuration
        f.write('# Motor configuration\n')
        f.write(f'odrv0.axis0.motor.config.pole_pairs = {odrv.axis0.motor.config.pole_pairs}\n')
        f.write(f'odrv0.axis0.motor.config.resistance_calib_max_voltage = {odrv.axis0.motor.config.resistance_calib_max_voltage}\n')
        f.write(f'odrv0.axis0.motor.config.requested_current_range = {odrv.axis0.motor.config.requested_current_range}\n')
        f.write(f'odrv0.axis0.motor.config.current_control_bandwidth = {odrv.axis0.motor.config.current_control_bandwidth}\n')
        f.write(f'odrv0.axis0.motor.config.torque_constant = {odrv.axis0.motor.config.torque_constant}\n')
        f.write(f'odrv0.axis0.motor.config.motor_type = {odrv.axis0.motor.config.motor_type}\n')
        f.write(f'odrv0.axis0.motor.config.calibration_current = {odrv.axis0.motor.config.calibration_current}\n')
        f.write(f'odrv0.axis0.motor.config.current_lim = {odrv.axis0.motor.config.current_lim}\n')
        f.write(f'odrv0.axis0.motor.config.pre_calibrated = {odrv.axis0.motor.config.pre_calibrated}\n\n')
        
        # Encoder configuration
        f.write('# Encoder configuration\n')
        f.write(f'odrv0.axis0.encoder.config.mode = {odrv.axis0.encoder.config.mode}\n')
        f.write(f'odrv0.axis0.encoder.config.use_index = {odrv.axis0.encoder.config.use_index}\n')
        f.write(f'odrv0.axis0.encoder.config.cpr = {odrv.axis0.encoder.config.cpr}\n')
        f.write(f'odrv0.axis0.encoder.config.bandwidth = {odrv.axis0.encoder.config.bandwidth}\n')
        f.write(f'odrv0.axis0.encoder.config.calib_range = {odrv.axis0.encoder.config.calib_range}\n')
        f.write(f'odrv0.axis0.encoder.config.calib_scan_distance = {odrv.axis0.encoder.config.calib_scan_distance}\n')
        f.write(f'odrv0.axis0.encoder.config.calib_scan_omega = {odrv.axis0.encoder.config.calib_scan_omega}\n')
        f.write(f'odrv0.axis0.encoder.config.pre_calibrated = {odrv.axis0.encoder.config.pre_calibrated}\n\n')
        
        # Controller configuration
        f.write('# Controller configuration\n')
        f.write(f'odrv0.axis0.controller.config.control_mode = {odrv.axis0.controller.config.control_mode}\n')
        f.write(f'odrv0.axis0.controller.config.input_mode = {odrv.axis0.controller.config.input_mode}\n')
        f.write(f'odrv0.axis0.controller.config.pos_gain = {odrv.axis0.controller.config.pos_gain}\n')
        f.write(f'odrv0.axis0.controller.config.vel_gain = {odrv.axis0.controller.config.vel_gain}\n')
        f.write(f'odrv0.axis0.controller.config.vel_integrator_gain = {odrv.axis0.controller.config.vel_integrator_gain}\n')
        f.write(f'odrv0.axis0.controller.config.vel_limit = {odrv.axis0.controller.config.vel_limit}\n')
        f.write(f'odrv0.axis0.controller.config.vel_ramp_rate = {odrv.axis0.controller.config.vel_ramp_rate}\n')
        f.write(f'odrv0.axis0.controller.config.input_filter_bandwidth = {odrv.axis0.controller.config.input_filter_bandwidth}\n')
        f.write(f'odrv0.axis0.controller.config.enable_vel_limit = {odrv.axis0.controller.config.enable_vel_limit}\n')
        f.write(f'odrv0.axis0.controller.config.enable_torque_mode_vel_limit = {odrv.axis0.controller.config.enable_torque_mode_vel_limit}\n')
        f.write(f'odrv0.axis0.controller.config.enable_gain_scheduling = {odrv.axis0.controller.config.enable_gain_scheduling}\n')
        f.write(f'odrv0.axis0.controller.config.enable_overspeed_error = {odrv.axis0.controller.config.enable_overspeed_error}\n\n')
        
        # Axis configuration
        f.write('# Axis configuration\n')
        f.write(f'odrv0.axis0.config.startup_motor_calibration = {odrv.axis0.config.startup_motor_calibration}\n')
        f.write(f'odrv0.axis0.config.startup_encoder_index_search = {odrv.axis0.config.startup_encoder_index_search}\n')
        f.write(f'odrv0.axis0.config.startup_encoder_offset_calibration = {odrv.axis0.config.startup_encoder_offset_calibration}\n')
        f.write(f'odrv0.axis0.config.startup_closed_loop_control = {odrv.axis0.config.startup_closed_loop_control}\n')
        f.write(f'odrv0.axis0.config.enable_step_dir = {odrv.axis0.config.enable_step_dir}\n')
        f.write(f'odrv0.axis0.config.enable_watchdog = {odrv.axis0.config.enable_watchdog}\n')
        f.write(f'odrv0.axis0.config.watchdog_timeout = {odrv.axis0.config.watchdog_timeout}\n\n')
        
        # Save configuration
        f.write('# Save configuration\n')
        f.write('print("Saving configuration...")\n')
        f.write('try:\n')
        f.write('    odrv0.save_configuration()\n')
        f.write('    print("Configuration saved. ODrive will reboot.")\n')
        f.write('except Exception as e:\n')
        f.write('    print(f"Exception during save: {e}")\n')
        f.write('    print("ODrive disconnected during save as expected.")\n')
    
    print(f"Backup completed and saved to {backup_path}")
    print("You can copy and paste the commands from this file into odrivetool to restore the configuration.")

if __name__ == "__main__":
    backup_odrive_config()
