#!/usr/bin/env python3
"""
Script to restore the original ODrive configuration from a backup file.
This can be used if you want to revert the changes made by improve_response_time.py.
"""
import odrive
import json
import sys
import glob
import os

def find_latest_backup():
    """Find the most recent backup file."""
    backup_files = glob.glob("odrive_backup_*.json")
    if not backup_files:
        print("No backup files found. Make sure you've run backup_odrive_config.py first.")
        sys.exit(1)
    
    # Sort by modification time (newest first)
    backup_files.sort(key=os.path.getmtime, reverse=True)
    return backup_files[0]

def restore_from_backup(backup_file=None):
    """Restore ODrive configuration from a backup file."""
    if backup_file is None:
        backup_file = find_latest_backup()
    
    print(f"Using backup file: {backup_file}")
    
    # Load the backup file
    try:
        with open(backup_file, 'r') as f:
            backup = json.load(f)
    except Exception as e:
        print(f"Error loading backup file: {e}")
        sys.exit(1)
    
    # Connect to ODrive
    print("Looking for ODrive...")
    try:
        odrv = odrive.find_any()
        print(f"Found ODrive: {str(odrv.serial_number)}")
    except:
        print("Failed to find ODrive. Make sure it's connected and powered on.")
        sys.exit(1)
    
    # Print current parameters
    print("\nCurrent parameters:")
    print(f"Input filter bandwidth: {odrv.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv.axis0.controller.config.vel_integrator_gain}")
    
    # Restore key parameters
    print("\nRestoring original parameters...")
    
    # Input filter bandwidth
    if 'axis0.controller.config.input_filter_bandwidth' in backup:
        odrv.axis0.controller.config.input_filter_bandwidth = backup['axis0.controller.config.input_filter_bandwidth']
    
    # Velocity ramp rate
    if 'axis0.controller.config.vel_ramp_rate' in backup:
        odrv.axis0.controller.config.vel_ramp_rate = backup['axis0.controller.config.vel_ramp_rate']
    
    # Velocity gain
    if 'axis0.controller.config.vel_gain' in backup:
        odrv.axis0.controller.config.vel_gain = backup['axis0.controller.config.vel_gain']
    
    # Velocity integrator gain
    if 'axis0.controller.config.vel_integrator_gain' in backup:
        odrv.axis0.controller.config.vel_integrator_gain = backup['axis0.controller.config.vel_integrator_gain']
    
    # Save configuration
    print("Saving configuration...")
    odrv.save_configuration()
    
    # Print restored parameters
    print("\nRestored parameters:")
    print(f"Input filter bandwidth: {odrv.axis0.controller.config.input_filter_bandwidth} Hz")
    print(f"Velocity ramp rate: {odrv.axis0.controller.config.vel_ramp_rate}")
    print(f"Velocity gain: {odrv.axis0.controller.config.vel_gain}")
    print(f"Velocity integrator gain: {odrv.axis0.controller.config.vel_integrator_gain}")
    
    print("\nOriginal configuration has been restored.")
    return odrv

if __name__ == "__main__":
    # If a backup file is specified as a command line argument, use that
    if len(sys.argv) > 1:
        backup_file = sys.argv[1]
        if not os.path.exists(backup_file):
            print(f"Backup file not found: {backup_file}")
            sys.exit(1)
        restore_from_backup(backup_file)
    else:
        # Otherwise use the most recent backup
        restore_from_backup()
