#!/usr/bin/env python3
"""
ODrive Calibration Utilities.
This script provides functions for properly calibrating and saving ODrive configuration
based on the official ODrive firmware implementation.
"""
import odrive
import time
import sys

def connect_to_odrive():
    """Connect to the ODrive."""
    print("Connecting to ODrive...")
    try:
        odrv = odrive.find_any()
        print(f"Found ODrive: {str(odrv.serial_number)}")
        return odrv
    except:
        print("Failed to find ODrive. Make sure it's connected and powered on.")
        sys.exit(1)

def wait_for_odrive(timeout=30):
    """Wait for ODrive to come back online after reboot."""
    print("Waiting for ODrive to come back online...")
    max_attempts = timeout
    for attempt in range(max_attempts):
        try:
            time.sleep(1.0)
            odrv = odrive.find_any()
            print(f"\nReconnected to ODrive: {str(odrv.serial_number)}")
            return odrv
        except:
            print(".", end="", flush=True)
    
    print("\nFailed to reconnect to ODrive after multiple attempts.")
    print("Please check the connection and restart the program.")
    sys.exit(1)

def check_errors(odrv, axis_num=None):
    """Check for errors and print them."""
    has_errors = False
    
    axes = []
    if axis_num is None:
        axes = [(0, odrv.axis0), (1, odrv.axis1)]
    elif axis_num == 0:
        axes = [(0, odrv.axis0)]
    elif axis_num == 1:
        axes = [(1, odrv.axis1)]
    
    for i, axis in axes:
        if axis.error != 0:
            print(f"Axis{i} error: {axis.error}")
            has_errors = True
        
        if axis.motor.error != 0:
            print(f"Motor{i} error: {axis.motor.error}")
            has_errors = True
        
        if axis.encoder.error != 0:
            print(f"Encoder{i} error: {axis.encoder.error}")
            has_errors = True
        
        if axis.controller.error != 0:
            print(f"Controller{i} error: {axis.controller.error}")
            has_errors = True
    
    return has_errors

def clear_errors(odrv, axis_num=None):
    """Clear all errors on the ODrive."""
    print("Clearing errors...")
    odrv.clear_errors()
    
    axes = []
    if axis_num is None:
        axes = [(0, odrv.axis0), (1, odrv.axis1)]
    elif axis_num == 0:
        axes = [(0, odrv.axis0)]
    elif axis_num == 1:
        axes = [(1, odrv.axis1)]
    
    for i, axis in axes:
        axis.error = 0
        axis.motor.error = 0
        axis.encoder.error = 0
        axis.controller.error = 0
    
    print("Errors cleared.")

def calibrate_motor_and_encoder(odrv, axis_num=None, force=False):
    """
    Calibrate motor and encoder for specified axis or both.
    
    WARNING: This will cause the motor to move! Make sure the robot is in a safe position
    before calibration.
    
    Args:
        odrv: ODrive object
        axis_num: Axis number to calibrate (None for both axes)
        force: Force calibration even if already calibrated
    
    Returns:
        Tuple of (success, odrv)
    """
    # Safety warning
    print("\n⚠️ WARNING: Calibration will cause the motor to move! ⚠️")
    print("Make sure the robot is in a safe position before continuing.")
    
    if not force:
        confirmation = input("Continue with calibration? (y/n): ").strip().lower()
        if confirmation != 'y':
            print("Calibration aborted.")
            return False, odrv
    
    # First, make sure motors are disarmed
    axes = []
    if axis_num is None:
        print("Calibrating both axes...")
        axes = [(0, odrv.axis0), (1, odrv.axis1)]
    elif axis_num == 0:
        print("Calibrating axis0...")
        axes = [(0, odrv.axis0)]
    elif axis_num == 1:
        print("Calibrating axis1...")
        axes = [(1, odrv.axis1)]
    
    # Set to idle state first
    for i, axis in axes:
        axis.requested_state = 1  # AXIS_STATE_IDLE
    
    time.sleep(1.0)  # Wait for motors to disarm
    
    # Clear any errors first
    if check_errors(odrv, axis_num):
        clear_errors(odrv, axis_num)
    
    success = True
    
    # Perform calibration for each axis
    for i, axis in axes:
        # Check if already calibrated
        if not force and axis.motor.is_calibrated and axis.encoder.is_ready:
            print(f"Axis{i} is already calibrated. Use --force to recalibrate.")
            continue
        
        print(f"Starting full calibration sequence for axis{i}...")
        axis.requested_state = 3  # AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        
        # Wait for calibration to complete
        start_time = time.time()
        timeout = 60.0  # 60 seconds timeout
        
        while axis.current_state != 1:  # AXIS_STATE_IDLE
            time.sleep(0.5)
            print(".", end="", flush=True)
            
            # Check for errors
            if axis.error != 0 or axis.motor.error != 0 or axis.encoder.error != 0:
                print(f"\nCalibration failed for axis{i} with errors:")
                if axis.error != 0:
                    print(f"  Axis error: {axis.error}")
                if axis.motor.error != 0:
                    print(f"  Motor error: {axis.motor.error}")
                if axis.encoder.error != 0:
                    print(f"  Encoder error: {axis.encoder.error}")
                success = False
                break
            
            # Check for timeout
            if time.time() - start_time > timeout:
                print(f"\nCalibration timed out for axis{i}.")
                success = False
                break
        
        if success:
            if axis.motor.is_calibrated and axis.encoder.is_ready:
                print(f"\nCalibration completed successfully for axis{i}.")
                
                # Set pre-calibrated flags
                axis.motor.config.pre_calibrated = True
                axis.encoder.config.pre_calibrated = True
            else:
                print(f"\nCalibration completed but axis{i} is not fully calibrated.")
                if not axis.motor.is_calibrated:
                    print("  Motor is not calibrated.")
                if not axis.encoder.is_ready:
                    print("  Encoder is not ready.")
                success = False
    
    # Save configuration if calibration was successful
    if success:
        print("\nCalibration successful for all requested axes.")
        print("Saving configuration...")
        try:
            # Make sure all motors are idle before saving
            for i, axis in axes:
                if axis.current_state != 1:  # AXIS_STATE_IDLE
                    axis.requested_state = 1  # AXIS_STATE_IDLE
                    time.sleep(0.5)
            
            # Save configuration
            odrv.save_configuration()
            print("Configuration saved. ODrive will reboot.")
            
            # Wait for ODrive to come back online
            odrv = wait_for_odrive()
            
            # Verify calibration after reboot
            all_calibrated = True
            for i, axis in [(0, odrv.axis0), (1, odrv.axis1)]:
                if axis_num is not None and i != axis_num:
                    continue
                if not axis.motor.is_calibrated or not axis.encoder.is_ready:
                    all_calibrated = False
                    print(f"Warning: Axis{i} is not showing as calibrated after reboot.")
            
            if all_calibrated:
                print("Calibration verified after reboot.")
            else:
                print("Some axes are not showing as calibrated after reboot.")
                success = False
            
        except Exception as e:
            print(f"Exception during save: {e}")
            print("ODrive disconnected during save as expected.")
            
            # Wait for ODrive to come back online
            odrv = wait_for_odrive()
    else:
        print("\nCalibration failed. Not saving configuration.")
    
    return success, odrv

def safe_save_configuration(odrv):
    """
    Safely save ODrive configuration following the official firmware approach.
    
    Args:
        odrv: ODrive object
    
    Returns:
        Tuple of (success, odrv)
    """
    print("Preparing to save configuration...")
    
    # Check if any motors are armed
    any_armed = False
    for axis in [odrv.axis0, odrv.axis1]:
        if axis.current_state != 1:  # AXIS_STATE_IDLE
            print(f"Setting axis to idle state...")
            axis.requested_state = 1  # AXIS_STATE_IDLE
            any_armed = True
    
    if any_armed:
        print("Waiting for motors to disarm...")
        time.sleep(1.0)
    
    # Clear any errors
    if check_errors(odrv):
        clear_errors(odrv)
    
    # Save configuration
    print("Saving configuration...")
    try:
        odrv.save_configuration()
        print("Configuration saved. ODrive will reboot.")
        
        # Wait for ODrive to come back online
        odrv = wait_for_odrive()
        return True, odrv
    except Exception as e:
        print(f"Exception during save: {e}")
        print("ODrive disconnected during save as expected.")
        
        # Wait for ODrive to come back online
        odrv = wait_for_odrive()
        return True, odrv

if __name__ == "__main__":
    # Example usage
    odrv = connect_to_odrive()
    
    # Check calibration status
    print("\nChecking calibration status:")
    for i, axis in [(0, odrv.axis0), (1, odrv.axis1)]:
        motor_calibrated = axis.motor.is_calibrated
        encoder_ready = axis.encoder.is_ready
        print(f"Axis{i}:")
        print(f"  Motor calibrated: {motor_calibrated}")
        print(f"  Encoder ready: {encoder_ready}")
        print(f"  Pre-calibrated flags:")
        print(f"    Motor: {axis.motor.config.pre_calibrated}")
        print(f"    Encoder: {axis.encoder.config.pre_calibrated}")
    
    # Ask if user wants to calibrate
    print("\nOptions:")
    print("1. Calibrate both axes")
    print("2. Calibrate axis0 only")
    print("3. Calibrate axis1 only")
    print("4. Save configuration only")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        success, odrv = calibrate_motor_and_encoder(odrv)
    elif choice == "2":
        success, odrv = calibrate_motor_and_encoder(odrv, axis_num=0)
    elif choice == "3":
        success, odrv = calibrate_motor_and_encoder(odrv, axis_num=1)
    elif choice == "4":
        success, odrv = safe_save_configuration(odrv)
    else:
        print("Exiting without calibration.")
        sys.exit(0)
    
    if success:
        print("Operation completed successfully.")
    else:
        print("Operation failed.")
