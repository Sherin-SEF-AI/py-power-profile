"""Tests for the badge generator."""

import pytest
import tempfile
from pathlib import Path

from py_power_profile.badge import BadgeGenerator


class TestBadgeGenerator:
    """Test BadgeGenerator class."""
    
    def test_initialization(self):
        """Test BadgeGenerator initialization."""
        generator = BadgeGenerator()
        assert "green" in generator.colors
        assert "red" in generator.colors
        assert "yellow" in generator.colors
    
    def test_generate_badge_green(self):
        """Test badge generation for green (pass) case."""
        generator = BadgeGenerator()
        results = {
            "summary": {"total_energy_mj": 50.0}
        }
        
        svg = generator.generate_badge(results, 80.0)
        
        assert "svg" in svg
        assert "50mJ" in svg
        assert "#4c1" in svg  # green color
    
    def test_generate_badge_red(self):
        """Test badge generation for red (fail) case."""
        generator = BadgeGenerator()
        results = {
            "summary": {"total_energy_mj": 110.0}
        }
        
        svg = generator.generate_badge(results, 80.0)
        
        assert "svg" in svg
        assert "110mJ" in svg
        assert "#e05d44" in svg  # red color
    
    def test_generate_badge_yellow(self):
        """Test badge generation for yellow (warn) case."""
        generator = BadgeGenerator()
        results = {
            "summary": {"total_energy_mj": 90.0}
        }
        
        svg = generator.generate_badge(results, 80.0)
        
        assert "svg" in svg
        assert "90mJ" in svg
        assert "#dfb317" in svg  # yellow color
    
    def test_generate_status_badge_pass(self):
        """Test status badge generation for pass case."""
        generator = BadgeGenerator()
        results = {
            "summary": {"total_energy_mj": 50.0}
        }
        
        svg = generator.generate_status_badge(results, 80.0)
        
        assert "svg" in svg
        assert "PASS" in svg
        assert "#4c1" in svg  # green color
    
    def test_generate_status_badge_fail(self):
        """Test status badge generation for fail case."""
        generator = BadgeGenerator()
        results = {
            "summary": {"total_energy_mj": 100.0}
        }
        
        svg = generator.generate_status_badge(results, 80.0)
        
        assert "svg" in svg
        assert "FAIL" in svg
        assert "#e05d44" in svg  # red color
    
    def test_write_badge(self):
        """Test writing badge to file."""
        generator = BadgeGenerator()
        results = {
            "summary": {"total_energy_mj": 50.0}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            temp_file = f.name
        
        try:
            generator.write_badge(results, 80.0, temp_file)
            
            # Check file was created and contains SVG
            assert Path(temp_file).exists()
            with open(temp_file, 'r') as f:
                content = f.read()
                assert "svg" in content
                assert "50mJ" in content
        finally:
            Path(temp_file).unlink(missing_ok=True)
    
    def test_write_status_badge(self):
        """Test writing status badge to file."""
        generator = BadgeGenerator()
        results = {
            "summary": {"total_energy_mj": 50.0}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            temp_file = f.name
        
        try:
            generator.write_badge(results, 80.0, temp_file, status_only=True)
            
            # Check file was created and contains SVG
            assert Path(temp_file).exists()
            with open(temp_file, 'r') as f:
                content = f.read()
                assert "svg" in content
                assert "PASS" in content
        finally:
            Path(temp_file).unlink(missing_ok=True) 