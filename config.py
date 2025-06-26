"""
PiCar-X Brainstem Configuration
"""

# Brain connection
#BRAIN_SERVER_URL = "ws://192.168.1.100:9977"
BRAIN_SERVER_URL = "ws://localhost:9977"
BRAIN_RECONNECT_INTERVAL = 5  # seconds

# Hardware settings
LIFE_LOOP_FREQUENCY = 10  # Hz
SENSOR_UPDATE_RATE = 10   # Hz

# PiCar-X specific motor settings
MOTOR_PWM_RANGE = (1000, 2000)
MOTOR_NEUTRAL = 1500
SERVO_PWM_RANGE = (500, 2500)
SERVO_NEUTRAL = 1500

# Safety limits
BATTERY_CRITICAL = 10.5    # Volts
BATTERY_LOW = 11.0         # Volts
OBSTACLE_CRITICAL = 10     # cm
TILT_CRITICAL = 45         # degrees

# Sensor settings
CAMERA_RESOLUTION = (640, 480)
CAMERA_FPS = 30
ULTRASONIC_TIMEOUT = 0.3   # seconds

# Fallback behavior settings
AUTONOMOUS_MODE_TIMEOUT = 60  # seconds before seeking brain
EXPLORATION_RADIUS = 2.0      # meters when autonomous

print("🧠 Configuration loaded:")
print(f"   Brain server: {BRAIN_SERVER_URL}")
print(f"   Life loop: {LIFE_LOOP_FREQUENCY} Hz")
print(f"   Battery critical: {BATTERY_CRITICAL}V")