#!/usr/bin/env python3
"""
Solax X3 Hybrid Inverter Modbus TCP Emulator

Created: 2025 October 29

Self-contained emulator for testing Modbus TCP communication with Solax inverters.
Simulates input registers (telemetry) and holding registers (configuration).
"""

import logging
import time
import math
from datetime import datetime
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore.store import BaseModbusDataBlock
import threading

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Network Configuration
MODBUS_HOST = '0.0.0.0'  # Listen on all interfaces
MODBUS_PORT = 502
MODBUS_UNIT_ID = 1

# System Specifications
PV1_MAX_POWER = 3300  # Watts
PV2_MAX_POWER = 3300  # Watts
BATTERY_CAPACITY = 10000  # Watt-hours
BATTERY_VOLTAGE = 51.2  # Volts
BATTERY_MAX_CHARGE_CURRENT = 100  # Amperes
BATTERY_MAX_DISCHARGE_CURRENT = 100  # Amperes
GRID_VOLTAGE_NOMINAL = 230.0  # Volts per phase
GRID_FREQUENCY = 50.0  # Hertz

# Initial State
INITIAL_BATTERY_SOC = 75  # Percent
INITIAL_RUN_MODE = 2  # Normal operation
INITIAL_OPERATING_MODE = 0  # Self-use mode

# Simulation Parameters
UPDATE_INTERVAL = 1.0  # Seconds between state updates
PV_VARIATION_FACTOR = 0.1  # +/- 10% random variation
BATTERY_CHARGE_RATE = 500  # Watts (when charging from PV)
BATTERY_DISCHARGE_RATE = 300  # Watts (when grid import needed)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# DYNAMIC MODBUS DATA BLOCK
# ============================================================================

class DynamicModbusDataBlock(BaseModbusDataBlock):
    """Modbus data block with dynamic value updates."""
    
    def __init__(self, address, values):
        self.address = address
        self.values = list(values)
        self.default_value = self.values[0] if values else 0
        
    def validate(self, address, count=1):
        """Validate register address range."""
        return 0 <= address < len(self.values)
    
    def getValues(self, address, count=1):
        """Get register values."""
        result = []
        for i in range(count):
            idx = address + i
            if idx < len(self.values):
                result.append(self.values[idx])
            else:
                result.append(self.default_value)
        return result
    
    def setValues(self, address, values):
        """Set register values."""
        for i, value in enumerate(values):
            idx = address + i
            if idx < len(self.values):
                self.values[idx] = value

# ============================================================================
# EMULATOR STATE MANAGEMENT
# ============================================================================

class SolaxEmulatorState:
    """Manages emulator state and dynamic updates."""
    
    def __init__(self):
        self.battery_soc = INITIAL_BATTERY_SOC
        self.run_mode = INITIAL_RUN_MODE
        self.operating_mode = INITIAL_OPERATING_MODE
        self.last_update = time.time()
        self.inverter_temp = 25  # Celsius
        self.battery_temp = 20  # Celsius
        
    def get_pv_power(self):
        """Calculate PV power based on time of day."""
        hour = datetime.now().hour
        # Simple sine curve: peak at noon, zero at night
        if 6 <= hour <= 18:
            # Normalize hour to 0-1 range (6am = 0, noon = 0.5, 6pm = 1)
            normalized = (hour - 6) / 12
            # Sine curve: 0 -> 1 -> 0
            factor = math.sin(normalized * math.pi)
            # Add random variation
            import random
            variation = 1.0 + random.uniform(-PV_VARIATION_FACTOR, PV_VARIATION_FACTOR)
            return int(PV1_MAX_POWER * factor * variation), int(PV2_MAX_POWER * factor * variation)
        return 0, 0
    
    def update_state(self):
        """Update dynamic state values."""
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        
        # Get current PV power
        pv1_power, pv2_power = self.get_pv_power()
        total_pv = pv1_power + pv2_power
        
        # Simple battery charging logic
        if total_pv > 1000 and self.battery_soc < 100:
            # Charging from excess PV
            energy_charged = BATTERY_CHARGE_RATE * dt / 3600  # Wh
            soc_increase = (energy_charged / BATTERY_CAPACITY) * 100
            self.battery_soc = min(100, self.battery_soc + soc_increase)
        elif total_pv < 500 and self.battery_soc > 10:
            # Discharging to support load
            energy_discharged = BATTERY_DISCHARGE_RATE * dt / 3600  # Wh
            soc_decrease = (energy_discharged / BATTERY_CAPACITY) * 100
            self.battery_soc = max(0, self.battery_soc - soc_decrease)
        
        # Update temperatures (simple model)
        if total_pv > 2000:
            self.inverter_temp = min(45, self.inverter_temp + 0.1)
        else:
            self.inverter_temp = max(25, self.inverter_temp - 0.1)
        
        if self.battery_soc > 90:
            self.battery_temp = min(30, self.battery_temp + 0.05)
        else:
            self.battery_temp = max(20, self.battery_temp - 0.05)
    
    def get_input_registers(self):
        """Generate input register values."""
        pv1_power, pv2_power = self.get_pv_power()
        pv1_voltage = 385 if pv1_power > 0 else 0
        pv2_voltage = 380 if pv2_power > 0 else 0
        pv1_current = int((pv1_power / pv1_voltage * 10)) if pv1_voltage > 0 else 0
        pv2_current = int((pv2_power / pv2_voltage * 10)) if pv2_voltage > 0 else 0
        
        # Battery calculations
        battery_voltage = int(BATTERY_VOLTAGE * 10)
        total_pv = pv1_power + pv2_power
        battery_power = 0
        battery_current = 0
        
        if total_pv > 1000 and self.battery_soc < 100:
            battery_power = BATTERY_CHARGE_RATE
            battery_current = int((battery_power / BATTERY_VOLTAGE) * 10)
        elif total_pv < 500 and self.battery_soc > 10:
            battery_power = -BATTERY_DISCHARGE_RATE
            battery_current = -int((abs(battery_power) / BATTERY_VOLTAGE) * 10)
        
        # Grid calculations
        grid_voltage = int(GRID_VOLTAGE_NOMINAL * 10)
        grid_power = total_pv - battery_power  # Simplified
        grid_current = int((abs(grid_power) / GRID_VOLTAGE_NOMINAL) * 10) if grid_power != 0 else 0
        if grid_power < 0:
            grid_current = -grid_current
        
        feedin_power = max(0, grid_power)  # Only positive values = export
        
        # Create register array (addresses 0x0000 to 0x0047+)
        registers = [0] * 128
        
        # Grid parameters (0x0000-0x0008)
        registers[0x00] = grid_voltage  # Phase R voltage
        registers[0x01] = grid_voltage  # Phase S voltage
        registers[0x02] = grid_voltage  # Phase T voltage
        registers[0x03] = abs(grid_current) if grid_current > 0 else 0  # Phase R current
        registers[0x04] = abs(grid_current) if grid_current > 0 else 0  # Phase S current
        registers[0x05] = abs(grid_current) if grid_current > 0 else 0  # Phase T current
        registers[0x06] = grid_power // 3 if grid_power > 0 else 0  # Phase R power
        registers[0x07] = grid_power // 3 if grid_power > 0 else 0  # Phase S power
        registers[0x08] = grid_power // 3 if grid_power > 0 else 0  # Phase T power
        
        # PV parameters (0x0009-0x000C)
        registers[0x09] = pv1_voltage
        registers[0x0A] = pv2_voltage
        registers[0x0B] = pv1_current
        registers[0x0C] = pv2_current
        
        # Battery parameters (0x0014-0x001D)
        registers[0x14] = battery_voltage
        registers[0x15] = self._to_signed_16bit(battery_current)
        registers[0x16] = self._to_signed_16bit(battery_power)
        registers[0x1C] = int(self.battery_temp)
        registers[0x1D] = int(self.battery_soc)
        
        # System status (0x0020, 0x0047)
        registers[0x20] = self._to_signed_16bit(feedin_power)
        registers[0x47] = self.run_mode
        
        return registers
    
    def get_holding_registers(self):
        """Generate holding register values."""
        registers = [0] * 128
        
        # Configuration parameters (0x001F-0x0029)
        registers[0x1F] = self.operating_mode
        registers[0x20] = 0   # Charge start hour
        registers[0x21] = 0   # Charge start minute
        registers[0x22] = 23  # Charge end hour
        registers[0x23] = 59  # Charge end minute
        registers[0x24] = 0   # Discharge start hour
        registers[0x25] = 0   # Discharge start minute
        registers[0x26] = 23  # Discharge end hour
        registers[0x27] = 59  # Discharge end minute
        registers[0x28] = BATTERY_MAX_CHARGE_CURRENT * int(BATTERY_VOLTAGE)  # Charge power limit
        registers[0x29] = BATTERY_MAX_DISCHARGE_CURRENT * int(BATTERY_VOLTAGE)  # Discharge power limit
        
        return registers
    
    @staticmethod
    def _to_signed_16bit(value):
        """Convert signed integer to 16-bit representation."""
        if value < 0:
            return (1 << 16) + value
        return value

# ============================================================================
# STATE UPDATE THREAD
# ============================================================================

def state_update_loop(state, input_block, holding_block):
    """Background thread to update emulator state."""
    logger.info("State update thread started")
    
    while True:
        try:
            # Update state
            state.update_state()
            
            # Update input registers
            input_registers = state.get_input_registers()
            input_block.setValues(0, input_registers)
            
            # Update holding registers (configuration can change)
            holding_registers = state.get_holding_registers()
            holding_block.setValues(0, holding_registers)
            
            time.sleep(UPDATE_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in state update loop: {e}")
            time.sleep(UPDATE_INTERVAL)

# ============================================================================
# MAIN EMULATOR
# ============================================================================

def run_emulator():
    """Start Modbus TCP emulator server."""
    logger.info("=" * 60)
    logger.info("Solax X3 Hybrid Inverter Modbus TCP Emulator")
    logger.info("=" * 60)
    logger.info(f"Host: {MODBUS_HOST}")
    logger.info(f"Port: {MODBUS_PORT}")
    logger.info(f"Unit ID: {MODBUS_UNIT_ID}")
    logger.info(f"PV Capacity: {PV1_MAX_POWER + PV2_MAX_POWER}W")
    logger.info(f"Battery: {BATTERY_CAPACITY}Wh @ {BATTERY_VOLTAGE}V")
    logger.info(f"Initial SOC: {INITIAL_BATTERY_SOC}%")
    logger.info("=" * 60)
    
    # Initialize state
    state = SolaxEmulatorState()
    
    # Create data blocks
    input_block = DynamicModbusDataBlock(0, state.get_input_registers())
    holding_block = DynamicModbusDataBlock(0, state.get_holding_registers())
    
    # Create datastore
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),  # Discrete Inputs
        co=ModbusSequentialDataBlock(0, [0]*100),  # Coils
        hr=holding_block,  # Holding Registers
        ir=input_block     # Input Registers
    )
    context = ModbusServerContext(slaves={MODBUS_UNIT_ID: store}, single=False)
    
    # Device identification
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Solax'
    identity.ProductCode = 'X3-Hybrid-6.0-D'
    identity.VendorUrl = 'http://www.solaxpower.com'
    identity.ProductName = 'Solax X3 Hybrid Inverter (Emulator)'
    identity.ModelName = 'X3-Hybrid-6.0-D'
    identity.MajorMinorRevision = '3.21'
    
    # Start state update thread
    update_thread = threading.Thread(
        target=state_update_loop,
        args=(state, input_block, holding_block),
        daemon=True
    )
    update_thread.start()
    
    # Start server
    logger.info("Starting Modbus TCP server...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        StartTcpServer(
            context=context,
            identity=identity,
            address=(MODBUS_HOST, MODBUS_PORT)
        )
    except KeyboardInterrupt:
        logger.info("\nShutting down emulator...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    
    logger.info("Emulator stopped")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    run_emulator()
