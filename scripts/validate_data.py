#!/usr/bin/env python3
"""
Validate pricing data against JSON schema.

This script validates that the pricing.json file conforms to the defined schema
and checks for data integrity issues.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from jsonschema import validate, ValidationError, Draft7Validator


def load_json(file_path):
    """Load JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def validate_timestamps(data):
    """Validate that timestamps are in ISO 8601 format and reasonable."""
    issues = []

    # Check global timestamp
    try:
        datetime.fromisoformat(data['lastUpdated'].replace('Z', '+00:00'))
    except (ValueError, KeyError) as e:
        issues.append(f"Invalid global lastUpdated timestamp: {e}")

    # Check provider timestamps
    for provider in data.get('providers', []):
        try:
            datetime.fromisoformat(provider['lastUpdated'].replace('Z', '+00:00'))
        except (ValueError, KeyError) as e:
            issues.append(f"Invalid timestamp for provider '{provider.get('name', 'Unknown')}': {e}")

    return issues


def validate_required_fields(data):
    """Check that all required fields are present and non-empty."""
    issues = []

    for provider in data.get('providers', []):
        provider_name = provider.get('name', 'Unknown')

        if not provider.get('models'):
            issues.append(f"Provider '{provider_name}' has no models")
            continue

        for model in provider['models']:
            model_name = model.get('name', 'Unknown')

            # Check required pricing fields
            pricing = model.get('pricing', {})
            if 'inputTokens' not in pricing:
                issues.append(f"Model '{model_name}' ({provider_name}) missing inputTokens")
            if 'outputTokens' not in pricing:
                issues.append(f"Model '{model_name}' ({provider_name}) missing outputTokens")
            if 'unit' not in pricing:
                issues.append(f"Model '{model_name}' ({provider_name}) missing unit")
            if 'currency' not in pricing:
                issues.append(f"Model '{model_name}' ({provider_name}) missing currency")

            # Check for negative prices
            if pricing.get('inputTokens', 0) < 0:
                issues.append(f"Model '{model_name}' ({provider_name}) has negative inputTokens price")
            if pricing.get('outputTokens', 0) < 0:
                issues.append(f"Model '{model_name}' ({provider_name}) has negative outputTokens price")

    return issues


def main():
    """Main validation function."""
    # Get paths relative to script location
    script_dir = Path(__file__).parent.parent
    schema_path = script_dir / 'data' / 'schema.json'
    data_path = script_dir / 'data' / 'pricing.json'

    print("Loading schema and data...")
    schema = load_json(schema_path)
    data = load_json(data_path)

    # Validate against JSON schema
    print("Validating against JSON schema...")
    try:
        validate(instance=data, schema=schema, cls=Draft7Validator)
        print("✓ Schema validation passed")
    except ValidationError as e:
        print(f"✗ Schema validation failed: {e.message}")
        print(f"  Path: {' -> '.join(str(p) for p in e.path)}")
        sys.exit(1)

    # Additional validation checks
    print("Running additional validation checks...")
    issues = []

    issues.extend(validate_timestamps(data))
    issues.extend(validate_required_fields(data))

    if issues:
        print(f"✗ Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)

    print("✓ All validation checks passed")
    print(f"\nSummary:")
    print(f"  Providers: {len(data['providers'])}")
    total_models = sum(len(p['models']) for p in data['providers'])
    print(f"  Total models: {total_models}")
    print(f"  Last updated: {data['lastUpdated']}")


if __name__ == '__main__':
    main()
