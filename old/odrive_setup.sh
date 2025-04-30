#!/bin/bash
# ODrive Response Time Improvement Script
# This script guides you through the process of improving ODrive response time

# Function to display a menu
show_menu() {
    clear
    echo "===== ODrive Response Time Improvement ====="
    echo "1. Backup current configuration"
    echo "2. Improve response time"
    echo "3. Test velocity commands (interactive)"
    echo "4. Run optimized response test"
    echo "5. Test first command delay fix"
    echo "6. Restore original configuration"
    echo "7. Run all steps in sequence (1-2-4)"
    echo "8. Exit"
    echo "==========================================="
    echo "Enter your choice [1-8]: "
}

# Function to backup configuration
backup_config() {
    echo "Backing up current ODrive configuration..."
    python3 backup_odrive_config.py
    echo "Press Enter to continue..."
    read
}

# Function to improve response time
improve_response() {
    echo "Improving ODrive response time..."
    python3 improve_response_time.py
    echo "Press Enter to continue..."
    read
}

# Function to test velocity commands
test_commands() {
    echo "Starting interactive velocity command tester..."
    python3 test_odrive_commands.py
    echo "Press Enter to continue..."
    read
}

# Function to run optimized response test
run_optimized_test() {
    echo "Running optimized response test..."
    python3 test_optimized_response.py
    echo "Press Enter to continue..."
    read
}

# Function to test first command delay fix
test_first_command_fix() {
    echo "Testing first command delay fix..."
    python3 fix_first_command_delay.py
    echo "Press Enter to continue..."
    read
}

# Function to restore original configuration
restore_config() {
    echo "Restoring original configuration..."
    python3 restore_original_config.py
    echo "Press Enter to continue..."
    read
}

# Function to run all steps in sequence
run_all() {
    echo "Running all steps in sequence..."
    
    echo "Step 1: Backing up current configuration"
    python3 backup_odrive_config.py
    echo "Backup complete."
    
    echo "Step 2: Improving response time"
    python3 improve_response_time.py
    echo "Response time improved."
    
    echo "Step 3: Running optimized response test"
    echo "Testing motor response with optimal velocity range..."
    python3 test_optimized_response.py
    
    echo "All steps completed."
    echo "Press Enter to continue..."
    read
}

# Main loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1) backup_config ;;
        2) improve_response ;;
        3) test_commands ;;
        4) run_optimized_test ;;
        5) test_first_command_fix ;;
        6) restore_config ;;
        7) run_all ;;
        8) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid option. Press Enter to continue..."; read ;;
    esac
done
