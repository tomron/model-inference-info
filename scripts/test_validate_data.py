#!/usr/bin/env python3
"""
Unit tests for data validation script.
"""

import json
import pytest
from pathlib import Path
from validate_data import validate_timestamps, validate_required_fields


def test_validate_timestamps_valid():
    """Test timestamp validation with valid data."""
    data = {
        'lastUpdated': '2026-02-15T10:00:00Z',
        'providers': [
            {
                'name': 'Test Provider',
                'lastUpdated': '2026-02-15T10:00:00Z',
                'models': []
            }
        ]
    }
    issues = validate_timestamps(data)
    assert len(issues) == 0


def test_validate_timestamps_invalid_global():
    """Test timestamp validation with invalid global timestamp."""
    data = {
        'lastUpdated': 'invalid-timestamp',
        'providers': []
    }
    issues = validate_timestamps(data)
    assert len(issues) > 0
    assert 'global lastUpdated' in issues[0]


def test_validate_timestamps_invalid_provider():
    """Test timestamp validation with invalid provider timestamp."""
    data = {
        'lastUpdated': '2026-02-15T10:00:00Z',
        'providers': [
            {
                'name': 'Test Provider',
                'lastUpdated': 'invalid',
                'models': []
            }
        ]
    }
    issues = validate_timestamps(data)
    assert len(issues) > 0
    assert 'Test Provider' in issues[0]


def test_validate_required_fields_valid():
    """Test required fields validation with valid data."""
    data = {
        'providers': [
            {
                'name': 'Test Provider',
                'models': [
                    {
                        'name': 'Test Model',
                        'modelId': 'test-model',
                        'pricing': {
                            'inputTokens': 0.001,
                            'outputTokens': 0.002,
                            'unit': 'per 1K tokens',
                            'currency': 'USD'
                        }
                    }
                ]
            }
        ]
    }
    issues = validate_required_fields(data)
    assert len(issues) == 0


def test_validate_required_fields_missing_pricing():
    """Test required fields validation with missing pricing fields."""
    data = {
        'providers': [
            {
                'name': 'Test Provider',
                'models': [
                    {
                        'name': 'Test Model',
                        'modelId': 'test-model',
                        'pricing': {
                            'inputTokens': 0.001,
                            # missing outputTokens, unit, currency
                        }
                    }
                ]
            }
        ]
    }
    issues = validate_required_fields(data)
    assert len(issues) >= 3  # Should have issues for missing fields


def test_validate_required_fields_negative_prices():
    """Test required fields validation with negative prices."""
    data = {
        'providers': [
            {
                'name': 'Test Provider',
                'models': [
                    {
                        'name': 'Test Model',
                        'modelId': 'test-model',
                        'pricing': {
                            'inputTokens': -0.001,
                            'outputTokens': -0.002,
                            'unit': 'per 1K tokens',
                            'currency': 'USD'
                        }
                    }
                ]
            }
        ]
    }
    issues = validate_required_fields(data)
    assert len(issues) >= 2  # Should have issues for negative prices


def test_validate_required_fields_empty_models():
    """Test required fields validation with no models."""
    data = {
        'providers': [
            {
                'name': 'Test Provider',
                'models': []
            }
        ]
    }
    issues = validate_required_fields(data)
    assert len(issues) > 0
    assert 'no models' in issues[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
