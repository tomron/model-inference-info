#!/usr/bin/env python3
"""
Fetch pricing data from OpenAI.

Data source: https://openai.com/api/pricing/
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def fetch_pricing_data():
    """Fetch OpenAI pricing data."""
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    # TODO: Implement scraping from https://openai.com/api/pricing/
    return {
        "name": "OpenAI",
        "lastUpdated": current_time,
        "models": [
            {
                "name": "GPT-4o",
                "modelId": "gpt-4o",
                "pricing": {
                    "inputTokens": 0.0025,
                    "outputTokens": 0.01,
                    "unit": "per 1K tokens",
                    "currency": "USD"
                }
            },
            {
                "name": "GPT-4o mini",
                "modelId": "gpt-4o-mini",
                "pricing": {
                    "inputTokens": 0.00015,
                    "outputTokens": 0.0006,
                    "unit": "per 1K tokens",
                    "currency": "USD"
                }
            },
            {
                "name": "o1",
                "modelId": "o1",
                "pricing": {
                    "inputTokens": 0.015,
                    "outputTokens": 0.06,
                    "unit": "per 1K tokens",
                    "currency": "USD"
                }
            },
            {
                "name": "o1-mini",
                "modelId": "o1-mini",
                "pricing": {
                    "inputTokens": 0.003,
                    "outputTokens": 0.012,
                    "unit": "per 1K tokens",
                    "currency": "USD"
                }
            }
        ]
    }


def get_current_timestamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def update_pricing_file(provider_data):
    script_dir = Path(__file__).parent.parent
    pricing_path = script_dir / 'data' / 'pricing.json'

    try:
        with open(pricing_path, 'r') as f:
            pricing_data = json.load(f)
    except FileNotFoundError:
        pricing_data = {'lastUpdated': get_current_timestamp(), 'providers': []}

    pricing_data['lastUpdated'] = get_current_timestamp()

    provider_found = False
    for i, provider in enumerate(pricing_data['providers']):
        if provider['name'] == provider_data['name']:
            pricing_data['providers'][i] = provider_data
            provider_found = True
            break

    if not provider_found:
        pricing_data['providers'].append(provider_data)

    pricing_data['providers'].sort(key=lambda p: p['name'])

    with open(pricing_path, 'w') as f:
        json.dump(pricing_data, f, indent=2)
        f.write('\n')

    print(f"✓ Updated pricing data for {provider_data['name']}")
    print(f"  Models: {len(provider_data['models'])}")


def main():
    try:
        print("Fetching OpenAI pricing data...")
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
