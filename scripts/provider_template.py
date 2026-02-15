#!/usr/bin/env python3
"""
Template for provider data collection scripts.

Copy this file to create a new provider script (e.g., fetch_provider_name.py)
and implement the fetch_pricing_data() function.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def fetch_pricing_data() -> Dict:
    """
    Fetch pricing data from the provider.

    Returns:
        dict: Provider data in the format:
        {
            "name": "Provider Name",
            "lastUpdated": "2026-02-15T10:00:00Z",
            "models": [
                {
                    "name": "Model Name",
                    "modelId": "model-id",
                    "pricing": {
                        "inputTokens": 0.001,
                        "outputTokens": 0.002,
                        "unit": "per 1K tokens",
                        "currency": "USD"
                    },
                    "regions": ["us-east-1", "us-west-2"]  # Optional
                }
            ]
        }
    """
    # TODO: Implement data fetching logic
    # Options:
    # 1. Scrape from provider website using BeautifulSoup
    # 2. Call provider API if available
    # 3. Use Selenium/Playwright for dynamic content

    raise NotImplementedError("Implement fetch_pricing_data() function")


def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def update_pricing_file(provider_data: Dict):
    """
    Update the pricing.json file with new provider data.

    Args:
        provider_data: Provider data dictionary from fetch_pricing_data()
    """
    # Get path to pricing.json
    script_dir = Path(__file__).parent.parent
    pricing_path = script_dir / 'data' / 'pricing.json'

    # Load existing data
    try:
        with open(pricing_path, 'r') as f:
            pricing_data = json.load(f)
    except FileNotFoundError:
        # Initialize if file doesn't exist
        pricing_data = {
            'lastUpdated': get_current_timestamp(),
            'providers': []
        }

    # Update global timestamp
    pricing_data['lastUpdated'] = get_current_timestamp()

    # Find and update or append provider
    provider_name = provider_data['name']
    provider_found = False

    for i, provider in enumerate(pricing_data['providers']):
        if provider['name'] == provider_name:
            pricing_data['providers'][i] = provider_data
            provider_found = True
            break

    if not provider_found:
        pricing_data['providers'].append(provider_data)

    # Sort providers alphabetically for consistency
    pricing_data['providers'].sort(key=lambda p: p['name'])

    # Write back to file
    with open(pricing_path, 'w') as f:
        json.dump(pricing_data, f, indent=2)
        f.write('\n')  # Add trailing newline

    print(f"✓ Updated pricing data for {provider_name}")
    print(f"  Models: {len(provider_data['models'])}")


def main():
    """Main execution function."""
    try:
        print("Fetching pricing data...")
        provider_data = fetch_pricing_data()

        print("Updating pricing file...")
        update_pricing_file(provider_data)

        print("✓ Success")
        return 0

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
