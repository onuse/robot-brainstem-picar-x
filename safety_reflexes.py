"""
Safety Reflexes - Hardcoded protective responses
"""
from hardware import HardwareInterface, SensorReading
import config

class SafetyReflexes:
    """
    Hardcoded safety responses - never learned, always active
    """
    
    def __init__(self, hardware: HardwareInterface):
        self.hardware = hardware
        self.emergency_count = 0
        
    def immediate_danger(self, sensors: SensorReading) -> bool:
        """
        Check for immediate threats requiring emergency action
        """
        
        # Battery critical
        if sensors.battery_voltage < config.BATTERY_CRITICAL:
            print(f"🚨 CRITICAL BATTERY: {sensors.battery_voltage}V")
            return True
        
        # Obstacle too close
        if sensors.ultrasonic_distance < config.OBSTACLE_CRITICAL:
            print(f"🚨 COLLISION IMMINENT: {sensors.ultrasonic_distance}cm")
            return True
        
        return False
    
    def emergency_action(self, sensors: SensorReading):
        """
        Execute emergency response
        """
        self.emergency_count += 1
        self.hardware.emergency_stop()
        
        # Log emergency for learning (send to brain later)
        print(f"🚨 Emergency #{self.emergency_count} triggered")