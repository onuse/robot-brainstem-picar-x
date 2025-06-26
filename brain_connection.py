"""
Brain Connection - WiFi link to neural nucleus
"""
import asyncio
import websockets
import msgpack
import time
from hardware import SensorReading, MotorCommand
from typing import Optional
import config

class BrainConnection:
    """
    Manages connection to the neural nucleus server
    """
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.websocket = None
        self.connected = False
        self.connection_attempts = 0
        self.last_successful_contact = 0
        self.message_count = 0
        
    async def connect(self) -> bool:
        """
        Attempt to connect to brain server
        """
        try:
            # Close existing connection if any
            if self.websocket:
                await self.websocket.close()
            
            # Connect with timeout
            self.websocket = await asyncio.wait_for(
                websockets.connect(self.server_url), 
                timeout=5.0
            )
            
            self.connected = True
            self.connection_attempts = 0
            self.last_successful_contact = time.time()
            
            print(f"🧠 Connected to brain: {self.server_url}")
            return True
            
        except asyncio.TimeoutError:
            self.connection_attempts += 1
            print(f"🧠 Brain connection timeout (attempt {self.connection_attempts})")
            return False
            
        except ConnectionRefusedError:
            self.connection_attempts += 1
            print(f"🧠 Brain server refused connection (attempt {self.connection_attempts})")
            return False
            
        except Exception as e:
            self.connection_attempts += 1
            print(f"🧠 Brain connection failed (attempt {self.connection_attempts}): {e}")
            return False
    
    async def send_sensors_get_commands(self, sensor_data: SensorReading) -> Optional[MotorCommand]:
        """
        Send sensor data to brain, receive motor commands
        """
        if not self.connected or not self.websocket:
            return None
        
        try:
            # Prepare sensor data message
            message = {
                'type': 'SENSOR_DATA',
                'timestamp': sensor_data.timestamp,
                'robot_id': 'brainstem_robot',
                'data': {
                    'timestamp': sensor_data.timestamp,
                    'battery_voltage': sensor_data.battery_voltage,
                    'ultrasonic_distance': sensor_data.ultrasonic_distance,
                    'power_source': sensor_data.power_source,
                    'motor_current': sensor_data.motor_current,
                    # Note: Skipping camera_frame for now (too large for initial testing)
                    'has_camera_frame': sensor_data.camera_frame is not None
                }
            }
            
            # Serialize and send
            packed_message = msgpack.packb(message)
            await self.websocket.send(packed_message)
            
            # Wait for response with timeout
            response_raw = await asyncio.wait_for(
                self.websocket.recv(), 
                timeout=0.5  # 500ms timeout
            )
            
            # Parse response
            response = msgpack.unpackb(response_raw)
            
            if response.get('type') == 'MOTOR_COMMANDS':
                motor_data = response.get('data', {})
                
                # Create motor command
                motor_commands = MotorCommand(
                    motor_left_pwm=motor_data.get('motor_left_pwm', 1500),
                    motor_right_pwm=motor_data.get('motor_right_pwm', 1500),
                    servo_camera_pwm=motor_data.get('servo_camera_pwm', 1500),
                    buzzer_active=motor_data.get('buzzer_active', False)
                )
                
                self.message_count += 1
                self.last_successful_contact = time.time()
                
                return motor_commands
                
            elif response.get('type') == 'ERROR':
                print(f"🧠 Brain error: {response.get('error', 'Unknown error')}")
                return None
                
            else:
                print(f"🧠 Unexpected response type: {response.get('type')}")
                return None
        
        except asyncio.TimeoutError:
            print("🧠 Brain response timeout")
            # Don't disconnect on timeout - might be temporary
            return None
            
        except websockets.exceptions.ConnectionClosed:
            print("🧠 Brain connection closed")
            self.connected = False
            return None
            
        except Exception as e:
            print(f"🧠 Communication error: {e}")
            self.connected = False
            return None
    
    def disconnect(self):
        """
        Disconnect from brain
        """
        if self.websocket:
            asyncio.create_task(self.websocket.close())
        self.connected = False
        print("🧠 Disconnected from brain server")
    
    def get_stats(self) -> dict:
        """
        Get connection statistics
        """
        return {
            'connected': self.connected,
            'server_url': self.server_url,
            'connection_attempts': self.connection_attempts,
            'message_count': self.message_count,
            'last_contact_age': time.time() - self.last_successful_contact if self.last_successful_contact > 0 else float('inf')
        }