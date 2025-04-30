#!/usr/bin/env python3
"""
Script to back up ODrive configuration and save it to a file.
"""
import odrive
import json
import time
from datetime import datetime

def get_nested_attributes(obj, prefix=""):
    """Recursively get all attributes of an object and their values."""
    attributes = {}
    
    # Get all attributes that don't start with '_'
    for attr_name in dir(obj):
        if attr_name.startswith('_'):
            continue
            
        try:
            attr_value = getattr(obj, attr_name)
            full_name = f"{prefix}.{attr_name}" if prefix else attr_name
            
            # Check if this is a property or method
            if callable(attr_value) or isinstance(attr_value, property):
                continue
                
            # If it's a simple type, add it directly
            if isinstance(attr_value, (int, float, bool, str, type(None))):
                attributes[full_name] = attr_value
            # If it's an enum, convert to int
            elif hasattr(attr_value, 'value') and isinstance(attr_value.value, int):
                attributes[full_name] = int(attr_value.value)
            # If it's an object with attributes, recurse
            elif hasattr(attr_value, '__dict__') or hasattr(attr_value, '__slots__'):
                nested_attrs = get_nested_attributes(attr_value, full_name)
                attributes.update(nested_attrs)
        except:
            # Skip attributes that can't be accessed
            continue
            
    return attributes

def backup_odrive_config():
    print("Looking for ODrive...")
    odrv = odrive.find_any()
    print(f"Found ODrive: {str(odrv.serial_number)}")
    
    print("Backing up configuration...")
    config = get_nested_attributes(odrv)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"odrive_backup_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration backed up to {filename}")
    return odrv, config, filename

if __name__ == "__main__":
    odrv, config, filename = backup_odrive_config()
    print("Backup complete. You can now make changes to improve response time.")
