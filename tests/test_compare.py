"""Tests for comparison functionality."""

import pytest
import tempfile
import json
from pathlib import Path

from py_power_profile.reporter import Reporter
from rich.console import Console


class TestReporterComparison:
    """Test Reporter comparison methods."""
    
    def test_compare_results_no_changes(self):
        """Test comparison with no significant changes."""
        reporter = Reporter()
        
        old_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 100.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 100.0}
        }
        
        new_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 105.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 105.0}
        }
        
        comparison = reporter.compare_results(old_results, new_results)
        
        assert comparison["total_change_percent"] == 5.0
        assert len(comparison["regressions"]) == 0
        assert len(comparison["improvements"]) == 0
    
    def test_compare_results_regression(self):
        """Test comparison with regression (>10% increase)."""
        reporter = Reporter()
        
        old_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 100.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 100.0}
        }
        
        new_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 120.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 120.0}
        }
        
        comparison = reporter.compare_results(old_results, new_results)
        
        assert comparison["total_change_percent"] == 20.0
        assert len(comparison["regressions"]) == 1
        assert "test.py:func1" in comparison["regressions"]
        assert len(comparison["improvements"]) == 0
    
    def test_compare_results_improvement(self):
        """Test comparison with improvement (>10% decrease)."""
        reporter = Reporter()
        
        old_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 100.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 100.0}
        }
        
        new_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 80.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 80.0}
        }
        
        comparison = reporter.compare_results(old_results, new_results)
        
        assert comparison["total_change_percent"] == -20.0
        assert len(comparison["regressions"]) == 0
        assert len(comparison["improvements"]) == 1
        assert "test.py:func1" in comparison["improvements"]
    
    def test_compare_results_new_function(self):
        """Test comparison with new function added."""
        reporter = Reporter()
        
        old_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 100.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 100.0}
        }
        
        new_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 100.0,
                    "calls": 10
                },
                "test.py:func2": {
                    "total_energy_mj": 50.0,
                    "calls": 5
                }
            },
            "summary": {"total_energy_mj": 150.0}
        }
        
        comparison = reporter.compare_results(old_results, new_results)
        
        assert comparison["total_change_percent"] == 50.0
        assert "test.py:func2" in comparison["changes"]
        assert comparison["changes"]["test.py:func2"]["change_percent"] == float('inf')
    
    def test_compare_results_removed_function(self):
        """Test comparison with function removed."""
        reporter = Reporter()
        
        old_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 100.0,
                    "calls": 10
                },
                "test.py:func2": {
                    "total_energy_mj": 50.0,
                    "calls": 5
                }
            },
            "summary": {"total_energy_mj": 150.0}
        }
        
        new_results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 100.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 100.0}
        }
        
        comparison = reporter.compare_results(old_results, new_results)
        
        assert comparison["total_change_percent"] == -33.33333333333333
        assert "test.py:func2" in comparison["changes"]
        assert comparison["changes"]["test.py:func2"]["change_percent"] == -100.0
    
    def test_write_json(self):
        """Test writing results to JSON."""
        reporter = Reporter()
        results = {
            "functions": {
                "test.py:func1": {
                    "total_energy_mj": 100.0,
                    "calls": 10
                }
            },
            "summary": {"total_energy_mj": 100.0}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                reporter.write_json(results, f)
            
            # Check file was created and contains correct JSON
            assert Path(temp_file).exists()
            with open(temp_file, 'r') as f:
                loaded_results = json.load(f)
                assert loaded_results == results
        finally:
            Path(temp_file).unlink(missing_ok=True) 