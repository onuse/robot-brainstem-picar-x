"""
Hardware Factory - Automatically chooses real vs simulated hardware
"""
import platform
import sys
from .hardware_interface import HardwareInterface
from .picar_x_simulator import PiCarXSimulator

def create_picar_x_hardware() -> HardwareInterface:
    """
    Factory function to create appropriate hardware interface
    """
    
    # Check if we're on a Raspberry Pi
    if platform.machine().startswith('arm') and platform.system() == 'Linux':
        try:
            # Test if Pi libraries are available
            #import RPi.GPIO
            
            # Try to create real hardware
            from .picar_x_real import PiCarXReal
            hardware = PiCarXReal()
            
            if hardware.initialize():
                print("🤖 Using REAL PiCar-X hardware")
                return hardware
            else:
                print("🤖 Real hardware initialization failed, falling back to simulator")
                
        except ImportError as e:
            print(f"🤖 Pi libraries not available ({e}), using simulator")
    else:
        print("🤖 Not on Raspberry Pi platform")
    
    # Default to simulator
    print("🤖 Using PiCar-X SIMULATOR")
    hardware = PiCarXSimulator()
    hardware.initialize()
    return hardware

def get_hardware_info():
    """Get information about available hardware"""
    return {
        'platform': platform.platform(),
        'machine': platform.machine(),
        'system': platform.system(),
        'python_version': sys.version,
        'can_use_real_hardware': platform.machine().startswith('arm') and platform.system() == 'Linux'
    }