"""
Core Life Loop - The robot's eternal consciousness cycle
"""
import asyncio
import time
from hardware import HardwareInterface, SensorReading, MotorCommand
from brain_connection import BrainConnection
from safety_reflexes import SafetyReflexes
from autonomous_fallback import AutonomousFallback
import config

class LifeLoop:
    """
    The robot's eternal consciousness - never stops running
    """
    
    def __init__(self, hardware: HardwareInterface, brain_link: BrainConnection):
        self.hardware = hardware
        self.brain_link = brain_link
        self.safety = SafetyReflexes(hardware)
        self.autonomous = AutonomousFallback(hardware)
        
        # Loop state
        self.loop_count = 0
        self.brain_connected = False
        self.last_brain_contact = 0
        self.isolation_start_time = None
        
        # Performance metrics
        self.brain_response_times = []
        self.communication_errors = 0
        
    async def eternal_consciousness(self):
        """
        The robot's eternal life loop - runs until shutdown
        """
        print("🧠 Life loop starting - robot consciousness active")
        
        # Initial brain connection attempt
        await self._attempt_brain_connection()
        
        while True:
            loop_start = time.time()
            self.loop_count += 1
            
            try:
                # PHASE 1: SENSE
                sensor_data = self.hardware.read_sensors()
                
                # PHASE 2: SAFETY CHECK (always local, immediate)
                if self.safety.immediate_danger(sensor_data):
                    print(f"🚨 Safety override triggered at loop {self.loop_count}")
                    self.hardware.emergency_stop()
                    await asyncio.sleep(1.0)  # Wait before trying again
                    continue
                
                # PHASE 3: BRAIN COMMUNICATION OR AUTONOMOUS MODE
                if self.brain_connected:
                    motor_commands = await self._brain_interaction(sensor_data)
                    if motor_commands:
                        # Brain responded successfully
                        self.hardware.execute_motor_commands(motor_commands)
                        self.last_brain_contact = time.time()
                        self._reset_isolation_timer()
                    else:
                        # Brain communication failed
                        await self._handle_brain_disconnect()
                        motor_commands = self.autonomous.decide_action(sensor_data)
                        self.hardware.execute_motor_commands(motor_commands)
                else:
                    # No brain connection - autonomous survival mode
                    motor_commands = self.autonomous.decide_action(sensor_data)
                    self.hardware.execute_motor_commands(motor_commands)
                    
                    # Periodically try to reconnect to brain
                    await self._periodic_brain_reconnection()
                
                # PHASE 4: STATUS REPORTING
                await self._periodic_status_report(sensor_data)
                
                # PHASE 5: LOOP TIMING
                await self._maintain_loop_timing(loop_start)
                
            except Exception as e:
                print(f"🧠 Life loop error: {e}")
                self.hardware.emergency_stop()
                self.communication_errors += 1
                await asyncio.sleep(0.5)
    
    async def _brain_interaction(self, sensor_data: SensorReading) -> MotorCommand:
        """
        Communicate with brain server and get motor commands
        """
        try:
            brain_start = time.time()
            
            # Send sensor data to brain and get commands
            motor_commands = await self.brain_link.send_sensors_get_commands(sensor_data)
            
            # Track performance
            response_time = time.time() - brain_start
            self.brain_response_times.append(response_time)
            
            # Keep only recent response times (last 100)
            if len(self.brain_response_times) > 100:
                self.brain_response_times.pop(0)
            
            # Warn about slow responses
            if response_time > 0.2:  # 200ms
                print(f"🧠 Slow brain response: {response_time*1000:.1f}ms")
            
            return motor_commands
            
        except asyncio.TimeoutError:
            print(f"🧠 Brain timeout at loop {self.loop_count}")
            return None
            
        except ConnectionError:
            print(f"🧠 Brain connection lost at loop {self.loop_count}")
            return None
            
        except Exception as e:
            print(f"🧠 Brain communication error: {e}")
            self.communication_errors += 1
            return None
    
    async def _attempt_brain_connection(self):
        """
        Try to establish initial brain connection
        """
        print("🧠 Attempting initial brain connection...")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                success = await self.brain_link.connect()
                if success:
                    self.brain_connected = True
                    self.last_brain_contact = time.time()
                    print(f"🧠 Brain connected successfully!")
                    return
                else:
                    print(f"🧠 Connection attempt {attempt + 1}/{max_attempts} failed")
                    
            except Exception as e:
                print(f"🧠 Connection attempt {attempt + 1} error: {e}")
            
            if attempt < max_attempts - 1:
                await asyncio.sleep(2.0)  # Wait between attempts
        
        print("🧠 Initial brain connection failed - starting in autonomous mode")
        self.brain_connected = False
    
    async def _handle_brain_disconnect(self):
        """
        Handle brain disconnection
        """
        if self.brain_connected:
            print("🧠 Brain disconnected - switching to autonomous mode")
            self.brain_connected = False
            self.brain_link.disconnect()
            
            # Start isolation timer
            if self.isolation_start_time is None:
                self.isolation_start_time = time.time()
    
    async def _periodic_brain_reconnection(self):
        """
        Periodically attempt to reconnect to brain
        """
        # Try to reconnect every 30 seconds
        if self.loop_count % (30 * config.LIFE_LOOP_FREQUENCY) == 0:
            print("🧠 Attempting brain reconnection...")
            
            try:
                success = await self.brain_link.connect()
                if success:
                    self.brain_connected = True
                    self.last_brain_contact = time.time()
                    isolation_duration = time.time() - (self.isolation_start_time or time.time())
                    print(f"🧠 Brain reconnected after {isolation_duration:.1f}s isolation!")
                    self._reset_isolation_timer()
                else:
                    print("🧠 Reconnection attempt failed")
                    
            except Exception as e:
                print(f"🧠 Reconnection error: {e}")
    
    def _reset_isolation_timer(self):
        """Reset isolation tracking"""
        self.isolation_start_time = None
    
    async def _periodic_status_report(self, sensor_data: SensorReading):
        """
        Periodic status reporting
        """
        # Report every 5 seconds (50 loops at 10Hz)
        if self.loop_count % 50 == 0:
            await self._log_status(sensor_data)
        
        # Detailed report every 30 seconds
        if self.loop_count % 300 == 0:
            await self._detailed_status_report()
    
    async def _log_status(self, sensor_data: SensorReading):
        """
        Log current status
        """
        hw_info = self.hardware.get_hardware_info()
        brain_status = "🧠 CONNECTED" if self.brain_connected else "🤖 AUTONOMOUS"
        
        # Calculate isolation duration
        isolation_info = ""
        if not self.brain_connected and self.isolation_start_time:
            isolation_duration = time.time() - self.isolation_start_time
            isolation_info = f" (isolated {isolation_duration:.1f}s)"
        
        print(f"🤖 Loop {self.loop_count}: {hw_info.get('type', 'Unknown')} - "
              f"Battery: {sensor_data.battery_voltage:.1f}V, "
              f"Distance: {sensor_data.ultrasonic_distance:.1f}cm - "
              f"{brain_status}{isolation_info}")
    
    async def _detailed_status_report(self):
        """
        Detailed status report
        """
        uptime = self.loop_count / config.LIFE_LOOP_FREQUENCY
        
        # Calculate average brain response time
        avg_response_time = 0
        if self.brain_response_times:
            avg_response_time = sum(self.brain_response_times) / len(self.brain_response_times)
        
        print(f"\n📊 BRAINSTEM STATUS REPORT:")
        print(f"   Uptime: {uptime:.1f}s ({self.loop_count} loops)")
        print(f"   Brain connected: {self.brain_connected}")
        print(f"   Communication errors: {self.communication_errors}")
        
        if self.brain_response_times:
            print(f"   Avg brain response: {avg_response_time*1000:.1f}ms")
            print(f"   Recent responses: {len(self.brain_response_times)}")
        
        if self.isolation_start_time:
            isolation_duration = time.time() - self.isolation_start_time
            print(f"   Isolation duration: {isolation_duration:.1f}s")
        
        print(f"   Hardware status: {self.hardware.get_status()}")
        print()
    
    async def _maintain_loop_timing(self, loop_start):
        """
        Maintain consistent loop timing
        """
        loop_time = time.time() - loop_start
        target_time = 1.0 / config.LIFE_LOOP_FREQUENCY
        
        if loop_time < target_time:
            await asyncio.sleep(target_time - loop_time)
        elif loop_time > target_time * 1.5:  # Warn if loop is running slow
            print(f"⚠️ Slow loop: {loop_time*1000:.1f}ms (target: {target_time*1000:.1f}ms)")
    
    def get_performance_stats(self) -> dict:
        """
        Get performance statistics
        """
        uptime = self.loop_count / config.LIFE_LOOP_FREQUENCY if self.loop_count > 0 else 0
        avg_response_time = sum(self.brain_response_times) / len(self.brain_response_times) if self.brain_response_times else 0
        
        return {
            'uptime_seconds': uptime,
            'total_loops': self.loop_count,
            'brain_connected': self.brain_connected,
            'communication_errors': self.communication_errors,
            'avg_brain_response_ms': avg_response_time * 1000,
            'isolation_duration': time.time() - self.isolation_start_time if self.isolation_start_time else 0
        }