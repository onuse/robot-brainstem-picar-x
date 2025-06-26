"""
Autonomous Fallback - Survive when brain is disconnected
"""
from hardware import HardwareInterface, SensorReading, MotorCommand
import time
import random

class AutonomousFallback:
    """
    Basic survival behaviors when brain is unavailable
    """
    
    def __init__(self, hardware: HardwareInterface):
        self.hardware = hardware
        self.isolation_start_time = None
        self.exploration_target = None
        
    def decide_action(self, sensors: SensorReading) -> MotorCommand:
        """
        Simple hardcoded behaviors for survival
        """
        
        if self.isolation_start_time is None:
            self.isolation_start_time = time.time()
            print("🤖 Entering autonomous survival mode")
        
        # Basic obstacle avoidance
        if sensors.ultrasonic_distance < 30:
            return self._avoid_obstacle()
        
        # Low battery - seek power source (very basic)
        if sensors.battery_voltage < 11.5:
            return self._seek_power()
        
        # Random exploration
        return self._explore()
    
    def _avoid_obstacle(self) -> MotorCommand:
        """Turn away from obstacle"""
        return MotorCommand(
            motor_left_pwm=1400,   # Slower
            motor_right_pwm=1600   # Faster = turn left
        )
    
    def _seek_power(self) -> MotorCommand:
        """Very basic power seeking"""
        return MotorCommand(
            motor_left_pwm=1500,
            motor_right_pwm=1500
        )
    
    def _explore(self) -> MotorCommand:
        """Random exploration"""
        return MotorCommand(
            motor_left_pwm=1530,
            motor_right_pwm=1530  # Slow forward
        )