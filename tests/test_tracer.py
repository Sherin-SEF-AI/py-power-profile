"""Tests for the tracer module."""

import pytest
from unittest.mock import Mock

from py_power_profile.backends import MockBackend
from py_power_profile.tracer import EnergyTracer, FunctionStats


class TestFunctionStats:
    """Test FunctionStats class."""
    
    def test_initialization(self):
        """Test FunctionStats initialization."""
        stats = FunctionStats()
        assert stats.calls == 0
        assert stats.total_energy_mj == 0.0
        assert stats.total_time_ms == 0.0
        assert stats.min_energy_mj == float('inf')
        assert stats.max_energy_mj == 0.0
    
    def test_update(self):
        """Test FunctionStats update method."""
        stats = FunctionStats()
        stats.update(10.0, 5.0)
        stats.update(20.0, 10.0)
        
        assert stats.calls == 2
        assert stats.total_energy_mj == 30.0
        assert stats.total_time_ms == 15.0
        assert stats.min_energy_mj == 10.0
        assert stats.max_energy_mj == 20.0
    
    def test_to_dict(self):
        """Test FunctionStats to_dict method."""
        stats = FunctionStats()
        stats.update(10.0, 5.0)
        stats.update(20.0, 10.0)
        
        result = stats.to_dict()
        assert result["calls"] == 2
        assert result["total_energy_mj"] == 30.0
        assert result["total_time_ms"] == 15.0
        assert result["avg_energy_mj"] == 15.0
        assert result["avg_time_ms"] == 7.5
        assert result["min_energy_mj"] == 10.0
        assert result["max_energy_mj"] == 20.0


class TestEnergyTracer:
    """Test EnergyTracer class."""
    
    def test_initialization(self):
        """Test EnergyTracer initialization."""
        backend = MockBackend()
        tracer = EnergyTracer(backend)
        
        assert tracer.backend == backend
        assert tracer.line_level is False
        assert len(tracer.stats) == 0
        assert len(tracer.call_stack) == 0
    
    def test_get_function_key(self):
        """Test _get_function_key method."""
        backend = MockBackend()
        tracer = EnergyTracer(backend)
        
        # Mock frame object
        frame = Mock()
        frame.f_code.co_filename = "test.py"
        frame.f_code.co_name = "test_function"
        
        key = tracer._get_function_key(frame)
        assert key == "test.py:test_function"
    
    def test_get_results(self):
        """Test get_results method."""
        backend = MockBackend()
        tracer = EnergyTracer(backend)
        
        # Add some mock stats
        stats = FunctionStats()
        stats.update(10.0, 5.0)
        tracer.stats["test.py:func1"] = stats
        
        results = tracer.get_results()
        
        assert "metadata" in results
        assert "functions" in results
        assert "summary" in results
        assert results["metadata"]["backend"] == "mock"
        assert results["metadata"]["line_level"] is False
        assert "test.py:func1" in results["functions"]
        assert results["summary"]["total_energy_mj"] == 10.0
        assert results["summary"]["function_count"] == 1 