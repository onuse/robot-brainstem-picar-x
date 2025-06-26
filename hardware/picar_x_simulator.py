"""
PiCar-X Simulator - For development on non-Pi systems
"""
import time
import numpy as np
import math
from .hardware_interface import HardwareInterface, SensorReading, MotorCommand

class PiCarXSimulator(HardwareInterface):
    """
    Simulated PiCar-X for development and testing
    """
    
    def __init__(self):
        super().__init__()
        
        # Simulated robot state
        self.position = [0.0, 0.0]  # x, y in meters
        self.orientation = 0.0      # radians
        self.battery_voltage = 12.0
        self.power_connected = False
        
        # Simulation parameters
        self.wheel_speed_left = 0.0
        self.wheel_speed_right = 0.0
        self.camera_angle = 0.0
        
        # Environment simulation
        self.obstacles = [(2.0, 0.0), (-1.5, 1.0), (0.5, -2.0)]  # Simulated obstacles
        self.start_time = time.time()
        
        print("🤖 PiCar-X Simulator initialized")
    
    def initialize(self) -> bool:
        """Initialize simulated hardware"""
        try:
            print("🤖 Initializing simulated PiCar-X hardware...")
            print("   📷 Camera: Simulated 640x480")
            print("   📡 Ultrasonic: Simulated range sensor")
            print("   🔋 Battery: Simulated 12V system")
            print("   ⚡ Motors: Simulated differential drive")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"🤖 Simulator initialization failed: {e}")
            return False
    
    def read_sensors(self) -> SensorReading:
        """Simulate sensor readings"""
        current_time = time.time()
        
        # Simulate battery drain
        runtime = current_time - self.start_time
        self.battery_voltage = max(10.0, 12.0 - (runtime / 3600) * 0.5)  # Drain over 1 hour
        
        # Simulate ultrasonic distance to nearest obstacle
        distance = self._simulate_ultrasonic_distance()
        
        # Simulate motor current based on speed
        motor_current = (
            abs(self.wheel_speed_left) * 0.5,
            abs(self.wheel_speed_right) * 0.5
        )
        
        # Create simulated camera frame
        camera_frame = self._simulate_camera_frame()
        
        reading = SensorReading(
            timestamp=current_time,
            battery_voltage=self.battery_voltage,
            ultrasonic_distance=distance,
            power_source="EXTERNAL" if self.power_connected else "BATTERY",
            motor_current=motor_current,
            camera_frame=camera_frame
        )
        
        self.last_sensor_reading = reading
        return reading
    
    def execute_motor_commands(self, commands: MotorCommand) -> bool:
        """Simulate motor execution and update robot state"""
        try:
            # Convert PWM to wheel speeds
            self.wheel_speed_left = (commands.motor_left_pwm - 1500) / 500.0  # -1 to 1
            self.wheel_speed_right = (commands.motor_right_pwm - 1500) / 500.0
            
            # Update camera angle
            self.camera_angle = (commands.servo_camera_pwm - 1500) / 1000.0  # -0.5 to 0.5 radians
            
            # Simulate robot movement (simple differential drive)
            dt = 0.1  # Assume 10Hz updates
            linear_velocity = (self.wheel_speed_left + self.wheel_speed_right) / 2.0
            angular_velocity = (self.wheel_speed_right - self.wheel_speed_left) / 0.15  # 15cm wheelbase
            
            # Update position and orientation
            self.position[0] += linear_velocity * math.cos(self.orientation) * dt
            self.position[1] += linear_velocity * math.sin(self.orientation) * dt
            self.orientation += angular_velocity * dt
            
            # Normalize orientation
            self.orientation = self.orientation % (2 * math.pi)
            
            return True
            
        except Exception as e:
            print(f"🤖 Simulator motor execution failed: {e}")
            return False
    
    def emergency_stop(self) -> bool:
        """Simulate emergency stop"""
        self.wheel_speed_left = 0.0
        self.wheel_speed_right = 0.0
        self.emergency_stop_active = True
        print("🚨 SIMULATOR EMERGENCY STOP")
        return True
    
    def shutdown(self):
        """Clean shutdown of simulator"""
        self.emergency_stop()
        print("🤖 PiCar-X Simulator shutdown complete")
    
    def get_hardware_info(self) -> dict:
        """Get simulated hardware info"""
        return {
            'type': 'PiCar-X Simulator',
            'platform': 'Simulated',
            'version': '1.0.0',
            'position': self.position,
            'orientation': math.degrees(self.orientation),
            'uptime': time.time() - self.start_time
        }
    
    def _simulate_ultrasonic_distance(self) -> float:
        """Simulate ultrasonic sensor reading"""
        # Find nearest obstacle in robot's forward direction
        robot_x, robot_y = self.position
        
        min_distance = 400.0  # Max sensor range in cm
        
        for obs_x, obs_y in self.obstacles:
            # Calculate distance to obstacle
            dx = obs_x - robot_x
            dy = obs_y - robot_y
            distance = math.sqrt(dx*dx + dy*dy) * 100  # Convert to cm
            
            # Check if obstacle is in front of robot (simplified)
            obstacle_angle = math.atan2(dy, dx)
            angle_diff = abs(obstacle_angle - self.orientation)
            if angle_diff < math.pi/6:  # 30 degree cone in front
                min_distance = min(min_distance, distance)
        
        # Add some noise
        noise = np.random.normal(0, 2.0)  # 2cm standard deviation
        return max(5.0, min_distance + noise)  # Minimum 5cm reading
    
    def _simulate_camera_frame(self):
        """Create a simple simulated camera frame"""
        # Create a simple colored frame (for testing)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some visual elements based on robot state
        # Green if moving forward, red if stopped, blue if turning
        if abs(self.wheel_speed_left) > 0.1 or abs(self.wheel_speed_right) > 0.1:
            if abs(self.wheel_speed_left - self.wheel_speed_right) > 0.2:
                frame[:, :, 2] = 100  # Blue for turning
            else:
                frame[:, :, 1] = 100  # Green for forward
        else:
            frame[:, :, 0] = 100  # Red for stopped
        
        return frame
    
    def connect_power(self):
        """Simulate connecting external power"""
        self.power_connected = True
        print("🔌 Simulated power connected")
    
    def disconnect_power(self):
        """Simulate disconnecting external power"""
        self.power_connected = False
        print("🔌 Simulated power disconnected")