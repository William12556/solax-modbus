#!/usr/bin/env python3
"""
Unit tests for Solax X3 Hybrid 6.0-D Inverter Monitoring Script
Tests core functionality with mocked Modbus communication
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch, call
from pymodbus.exceptions import ModbusException

# Import from src directory
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from solax_poll import SolaxInverterClient, InverterDisplay


class TestSolaxInverterClient:
    """Test suite for SolaxInverterClient class."""
    
    @pytest.fixture
    def client(self):
        """Create a client instance for testing."""
        return SolaxInverterClient('192.168.1.100', port=502, unit_id=1)
    
    def test_initialization(self, client):
        """Test client initialization with correct parameters."""
        assert client.ip == '192.168.1.100'
        assert client.port == 502
        assert client.unit_id == 1
        assert client.client is None
        assert client.max_retries == 3
        assert client.retry_delay == 1
    
    @patch('solax_poll.ModbusTcpClient')
    def test_connect_success(self, mock_modbus_class, client):
        """Test successful connection to inverter."""
        mock_modbus = Mock()
        mock_modbus.connect.return_value = True
        mock_modbus_class.return_value = mock_modbus
        
        result = client.connect()
        
        assert result is True
        assert client.client == mock_modbus
        mock_modbus_class.assert_called_once_with('192.168.1.100', port=502)
        mock_modbus.connect.assert_called_once()
    
    @patch('solax_poll.ModbusTcpClient')
    @patch('solax_poll.time.sleep')
    def test_connect_with_retry(self, mock_sleep, mock_modbus_class, client):
        """Test connection retry with exponential backoff."""
        mock_modbus = Mock()
        # Fail twice, succeed on third attempt
        mock_modbus.connect.side_effect = [False, False, True]
        mock_modbus_class.return_value = mock_modbus
        
        result = client.connect()
        
        assert result is True
        assert mock_modbus.connect.call_count == 3
        # Check exponential backoff delays
        assert mock_sleep.call_args_list == [call(1), call(2)]
    
    @patch('solax_poll.ModbusTcpClient')
    @patch('solax_poll.time.sleep')
    def test_connect_failure_after_retries(self, mock_sleep, mock_modbus_class, client):
        """Test connection failure after max retries."""
        mock_modbus = Mock()
        mock_modbus.connect.return_value = False
        mock_modbus_class.return_value = mock_modbus
        
        result = client.connect()
        
        assert result is False
        assert mock_modbus.connect.call_count == 3
        # Two sleep calls between three attempts
        assert mock_sleep.call_count == 2
    
    def test_disconnect(self, client):
        """Test safe disconnection from inverter."""
        mock_client = Mock()
        client.client = mock_client
        
        client.disconnect()
        
        mock_client.close.assert_called_once()
    
    def test_disconnect_with_error(self, client):
        """Test disconnect handles errors gracefully."""
        mock_client = Mock()
        mock_client.close.side_effect = Exception("Connection error")
        client.client = mock_client
        
        # Should not raise exception
        client.disconnect()
        mock_client.close.assert_called_once()
    
    def test_to_signed_positive(self, client):
        """Test conversion of positive values."""
        assert client._to_signed(100) == 100
        assert client._to_signed(32767) == 32767
    
    def test_to_signed_negative(self, client):
        """Test conversion of negative values."""
        assert client._to_signed(32768) == -32768
        assert client._to_signed(65535) == -1
    
    def test_to_signed_32_positive(self, client):
        """Test 32-bit signed conversion for positive values."""
        result = client._to_signed_32(0x1234, 0x0001)
        assert result == 0x00011234
    
    def test_to_signed_32_negative(self, client):
        """Test 32-bit signed conversion for negative values."""
        result = client._to_signed_32(0xFFFF, 0xFFFF)
        assert result == -1
    
    def test_to_unsigned_32(self, client):
        """Test 32-bit unsigned conversion."""
        result = client._to_unsigned_32(0x1234, 0x5678)
        assert result == 0x56781234
    
    def test_read_registers_success(self, client):
        """Test successful register reading."""
        mock_modbus = Mock()
        mock_result = Mock()
        mock_result.isError.return_value = False
        mock_result.registers = [100, 200, 300]
        mock_modbus.read_input_registers.return_value = mock_result
        client.client = mock_modbus
        
        result = client.read_registers(0x0003, 3, "test registers")
        
        assert result == [100, 200, 300]
        mock_modbus.read_input_registers.assert_called_once_with(
            address=0x0003,
            count=3,
            unit=1
        )
    
    def test_read_registers_modbus_error(self, client):
        """Test register reading with Modbus error."""
        mock_modbus = Mock()
        mock_result = Mock()
        mock_result.isError.return_value = True
        mock_modbus.read_input_registers.return_value = mock_result
        client.client = mock_modbus
        
        result = client.read_registers(0x0003, 3, "test registers")
        
        assert result is None
    
    def test_read_registers_exception(self, client):
        """Test register reading with exception."""
        mock_modbus = Mock()
        mock_modbus.read_input_registers.side_effect = ModbusException("Test error")
        client.client = mock_modbus
        
        result = client.read_registers(0x0003, 3, "test registers")
        
        assert result is None
    
    def test_process_grid_data(self, client):
        """Test processing of three-phase grid data."""
        regs = [2302, 42, 966, 5001,  # R phase
                2298, 38, 873, 5002,   # S phase
                2311, 45, 1040, 5003]  # T phase
        
        result = client._process_grid_data(regs)
        
        assert result['grid_voltage_r'] == pytest.approx(230.2, 0.01)
        assert result['grid_current_r'] == pytest.approx(4.2, 0.01)
        assert result['grid_power_r'] == 966
        assert result['grid_frequency_r'] == pytest.approx(50.01, 0.001)
    
    def test_process_pv_data(self, client):
        """Test processing of PV generation data."""
        vc_regs = [3854, 3821, 82, 78]  # Voltages and currents
        power_regs = [3160, 2980]       # Power values
        
        result = client._process_pv_data(vc_regs, power_regs)
        
        assert result['pv1_voltage'] == pytest.approx(385.4, 0.01)
        assert result['pv2_voltage'] == pytest.approx(382.1, 0.01)
        assert result['pv1_current'] == pytest.approx(8.2, 0.01)
        assert result['pv2_current'] == pytest.approx(7.8, 0.01)
        assert result['pv1_power'] == 3160
        assert result['pv2_power'] == 2980
    
    def test_process_battery_data(self, client):
        """Test processing of battery system data."""
        regs = [2705, 124, 3354, 0, 24, 0, 0, 0, 78]  # Battery data
        
        result = client._process_battery_data(regs)
        
        assert result['battery_voltage'] == pytest.approx(270.5, 0.01)
        assert result['battery_current'] == pytest.approx(12.4, 0.01)
        assert result['battery_power'] == 3354
        assert result['battery_temperature'] == 24
        assert result['battery_soc'] == 78
    
    @patch.object(SolaxInverterClient, 'read_registers')
    def test_poll_inverter_complete(self, mock_read_registers, client):
        """Test complete polling cycle with all data."""
        # Setup mock responses for different register groups
        mock_responses = {
            (0x006A, 12): [2302, 42, 966, 5001, 2298, 38, 873, 5002, 
                          2311, 45, 1040, 5003],  # Grid data
            (0x0003, 4): [3854, 3821, 82, 78],    # PV voltage/current
            (0x000A, 2): [3160, 2980],             # PV power
            (0x0014, 9): [2705, 124, 3354, 0, 24, 0, 0, 0, 78],  # Battery
            (0x0046, 2): [0, 0],                   # Feed-in power
            (0x0050, 1): [284],                    # Energy today
            (0x0052, 2): [18473, 0],               # Energy total
            (0x0008, 2): [42, 2],                  # Inverter status
        }
        
        def side_effect(address, count, description):
            return mock_responses.get((address, count))
        
        mock_read_registers.side_effect = side_effect
        
        result = client.poll_inverter()
        
        # Verify key data points
        assert 'timestamp' in result
        assert result['grid_voltage_r'] == pytest.approx(230.2, 0.01)
        assert result['pv1_power'] == 3160
        assert result['battery_soc'] == 78
        assert result['energy_today'] == pytest.approx(28.4, 0.01)
        assert result['run_mode'] == 'Normal'


class TestInverterDisplay:
    """Test suite for InverterDisplay class."""
    
    def test_display_with_no_data(self, capsys):
        """Test display with no data."""
        display = InverterDisplay()
        display.display_statistics({})
        
        captured = capsys.readouterr()
        assert "No data available" in captured.out
    
    def test_display_with_complete_data(self, capsys):
        """Test display with complete data set."""
        display = InverterDisplay()
        data = {
            'timestamp': '2025-10-22 14:32:15',
            'run_mode': 'Normal',
            'grid_voltage_r': 230.2,
            'grid_current_r': 4.2,
            'grid_power_r': 966,
            'grid_voltage_s': 229.8,
            'grid_current_s': 3.8,
            'grid_power_s': 873,
            'grid_voltage_t': 231.1,
            'grid_current_t': 4.5,
            'grid_power_t': 1040,
            'grid_frequency_r': 50.01,
            'pv1_voltage': 385.4,
            'pv1_current': 8.2,
            'pv1_power': 3160,
            'pv2_voltage': 382.1,
            'pv2_current': 7.8,
            'pv2_power': 2980,
            'battery_voltage': 270.5,
            'battery_current': 12.4,
            'battery_power': 3354,
            'battery_soc': 78,
            'battery_temperature': 24,
            'feed_in_power': 0,
            'energy_today': 28.4,
            'energy_total': 1847.3,
            'inverter_temperature': 42
        }
        
        display.display_statistics(data)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify key information is displayed
        assert "Solax X3 Hybrid 6.0-D Inverter Statistics" in output
        assert "System Status: Normal" in output
        assert "Grid (Three-Phase AC)" in output
        assert "Solar PV Generation" in output
        assert "Battery System" in output
        assert "State of Charge: 78%" in output
        assert "Solar Generation Today: 28.4kWh" in output
    
    def test_display_power_flow_exporting(self, capsys):
        """Test power flow display when exporting."""
        display = InverterDisplay()
        data = {'feed_in_power': 1500}
        
        display.display_statistics(data)
        
        captured = capsys.readouterr()
        assert "EXPORTING 1500W" in captured.out
    
    def test_display_power_flow_importing(self, capsys):
        """Test power flow display when importing."""
        display = InverterDisplay()
        data = {'feed_in_power': -800}
        
        display.display_statistics(data)
        
        captured = capsys.readouterr()
        assert "IMPORTING 800W" in captured.out


class TestMainExecution:
    """Test suite for main execution logic."""
    
    @patch('solax_poll.argparse.ArgumentParser.parse_args')
    @patch('solax_poll.SolaxInverterClient')
    @patch('solax_poll.InverterDisplay')
    @patch('solax_poll.time.sleep')
    def test_main_loop_keyboard_interrupt(self, mock_sleep, mock_display_class, 
                                         mock_client_class, mock_parse_args):
        """Test main loop handles keyboard interrupt gracefully."""
        # Setup argument parser mock
        mock_args = Mock()
        mock_args.ip = '192.168.1.100'
        mock_args.port = 502
        mock_args.unit_id = 1
        mock_args.interval = 5
        mock_args.debug = False
        mock_parse_args.return_value = mock_args
        
        # Setup client mock
        mock_client = Mock()
        mock_client.client = Mock()
        mock_client.client.is_socket_open.return_value = True
        mock_client.connect.return_value = True
        mock_client.poll_inverter.return_value = {'test': 'data'}
        mock_client_class.return_value = mock_client
        
        # Setup display mock
        mock_display = Mock()
        mock_display_class.return_value = mock_display
        
        # Simulate KeyboardInterrupt after one iteration
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Import and run main
        from solax_poll import main
        
        # Should exit gracefully without raising exception
        try:
            main()
        except SystemExit:
            pass  # Expected behavior
        
        # Verify cleanup was called
        mock_client.disconnect.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
