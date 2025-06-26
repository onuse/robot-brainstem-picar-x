"""
Brainstem Bootstrap - Brings the robot to life
"""
import asyncio
import sys
import signal
from config import *
from life_loop import LifeLoop
from hardware import create_picar_x_hardware, get_hardware_info
from brain_connection import BrainConnection

def signal_handler(signum, frame):
    """Handle shutdown gracefully"""
    print("\n🧠 Brainstem shutting down...")
    sys.exit(0)

def main():
    print("🧠 Brainstem initializing...")
    
    # Show hardware detection info
    hw_info = get_hardware_info()
    print(f"   Platform: {hw_info['machine']} ({hw_info['system']})")
    print(f"   Can use real hardware: {hw_info['can_use_real_hardware']}")
    
    # Initialize hardware (auto-detects real vs simulated)
    hardware = create_picar_x_hardware()
    
    # Initialize brain connection
    brain_link = BrainConnection(BRAIN_SERVER_URL)
    
    # Start life loop
    life_loop = LifeLoop(hardware, brain_link)
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        print(f"🧠 Starting eternal consciousness...")
        asyncio.run(life_loop.eternal_consciousness())
    except KeyboardInterrupt:
        print("🧠 Brainstem shutting down...")
        hardware.shutdown()

if __name__ == "__main__":
    main()