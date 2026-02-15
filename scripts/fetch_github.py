#!/usr/bin/env python3
"""
Fetch pricing data from GitHub Copilot.

Data source: https://github.com/features/copilot/plans
Last verified: 2026-02-15
"""

import json
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup


def fetch_pricing_data():
    """Fetch GitHub Copilot pricing by scraping the pricing page."""
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    url = 'https://github.com/features/copilot/plans'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    models = []
    pricing_found = False

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for pricing information in the page
        text = soup.get_text().lower()

        # Extract monthly pricing for Individual plan
        individual_price_match = re.search(r'individual.*?\$(\d+).*?(?:month|mo)', text, re.DOTALL)

        if individual_price_match:
            individual_price = float(individual_price_match.group(1))
            models.append({
                'name': 'GitHub Copilot (Individual)',
                'modelId': 'github-copilot-individual',
                'pricing': {
                    'inputTokens': 0,
                    'outputTokens': 0,
                    'unit': 'per month',
                    'currency': 'USD'
                },
                'notes': f'${individual_price}/month subscription, unlimited usage'
            })
            pricing_found = True

        # Also try to find Business plan
        business_price_match = re.search(r'business.*?\$(\d+).*?(?:month|mo)', text, re.DOTALL)

        if business_price_match:
            business_price = float(business_price_match.group(1))
            models.append({
                'name': 'GitHub Copilot (Business)',
                'modelId': 'github-copilot-business',
                'pricing': {
                    'inputTokens': 0,
                    'outputTokens': 0,
                    'unit': 'per user/month',
                    'currency': 'USD'
                },
                'notes': f'${business_price}/user/month subscription'
            })
            pricing_found = True

    except Exception as e:
        print(f"⚠️  Error scraping GitHub Copilot pricing: {e}")

    # Fallback to known pricing
    if not pricing_found:
        print("⚠️  Using known pricing as fallback")
        models = [
            {
                'name': 'GitHub Copilot (Individual)',
                'modelId': 'github-copilot-individual',
                'pricing': {
                    'inputTokens': 0,
                    'outputTokens': 0,
                    'unit': 'per month',
                    'currency': 'USD'
                },
                'notes': '$10/month subscription, unlimited usage'
            }
        ]

    return {
        'name': 'GitHub Copilot',
        'lastUpdated': current_time,
        'models': models
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


def main():
    try:
        print("Fetching GitHub Copilot pricing data...")
        provider_data = fetch_pricing_data()
        update_pricing_file(provider_data)
        print("✓ Success")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
