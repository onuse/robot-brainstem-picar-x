"""
Hardware Interface - Abstract base class for all hardware implementations
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple
import time

@dataclass
class SensorReading:
    timestamp: float
    battery_voltage: float
    ultrasonic_distance: float
    power_source: str  # "BATTERY" or "EXTERNAL"
    motor_current: Tuple[float, float]
    camera_frame: Optional[object] = None
    line_sensors: Optional[Tuple[float, float, float]] = None

@dataclass 
class MotorCommand:
    motor_left_pwm: int = 1500
    motor_right_pwm: int = 1500
    servo_camera_pwm: int = 1500
    buzzer_active: bool = False

class HardwareInterface(ABC):
    """
    Abstract interface that all hardware implementations must follow
    """
    
    def __init__(self):
        self.is_initialized = False
        self.last_sensor_reading = None
        self.emergency_stop_active = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize hardware - returns True if successful"""
        pass
    
    @abstractmethod
    def read_sensors(self) -> SensorReading:
        """Read all sensors and return current state"""
        pass
    
    @abstractmethod
    def execute_motor_commands(self, commands: MotorCommand) -> bool:
        """Execute motor commands - returns True if successful"""
        pass
    
    @abstractmethod
    def emergency_stop(self) -> bool:
        """Immediate stop all motors - returns True if successful"""
        pass
    
    @abstractmethod
    def shutdown(self):
        """Clean shutdown of hardware"""
        pass
    
    @abstractmethod
    def get_hardware_info(self) -> dict:
        """Get hardware identification and status"""
        pass
    
    def get_status(self) -> dict:
        """Get current hardware status"""
        return {
            'initialized': self.is_initialized,
            'emergency_stop_active': self.emergency_stop_active,
            'last_reading_age': time.time() - (self.last_sensor_reading.timestamp if self.last_sensor_reading else 0)
        }