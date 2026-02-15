#!/usr/bin/env python3
"""
Fetch pricing data from Azure OpenAI.

Data source: https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/
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
    """Fetch Azure OpenAI pricing by scraping the pricing page."""
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    url = 'https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    models = []
    pricing_found = False

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for tables containing pricing
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue

                row_text = ' '.join(cell.get_text().strip() for cell in cells)

                # Look for GPT-4o pricing
                if 'gpt-4o' in row_text.lower() and 'mini' not in row_text.lower():
                    prices = re.findall(r'\$(\d+\.?\d*)', row_text)

                    if len(prices) >= 2 and not any(m['modelId'] == 'gpt-4o' for m in models):
                        models.append({
                            'name': 'GPT-4o',
                            'modelId': 'gpt-4o',
                            'pricing': {
                                'inputTokens': float(prices[0]),
                                'outputTokens': float(prices[1]),
                                'unit': 'per 1K tokens',
                                'currency': 'USD'
                            },
                            'regions': ['eastus', 'westus', 'westeurope', 'japaneast']
                        })
                        pricing_found = True

                # Look for GPT-4o mini pricing
                elif 'gpt-4o' in row_text.lower() and 'mini' in row_text.lower():
                    prices = re.findall(r'\$(\d+\.?\d*)', row_text)

                    if len(prices) >= 2 and not any(m['modelId'] == 'gpt-4o-mini' for m in models):
                        models.append({
                            'name': 'GPT-4o mini',
                            'modelId': 'gpt-4o-mini',
                            'pricing': {
                                'inputTokens': float(prices[0]),
                                'outputTokens': float(prices[1]),
                                'unit': 'per 1K tokens',
                                'currency': 'USD'
                            },
                            'regions': ['eastus', 'westus', 'westeurope']
                        })
                        pricing_found = True

    except Exception as e:
        print(f"⚠️  Error scraping Azure OpenAI pricing: {e}")

    # Fallback to known pricing
    if not pricing_found:
        print("⚠️  Using known pricing as fallback")
        models = [
            {
                'name': 'GPT-4o',
                'modelId': 'gpt-4o',
                'pricing': {
                    'inputTokens': 0.005,
                    'outputTokens': 0.015,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                },
                'regions': ['eastus', 'westus', 'westeurope', 'japaneast']
            },
            {
                'name': 'GPT-4o mini',
                'modelId': 'gpt-4o-mini',
                'pricing': {
                    'inputTokens': 0.00015,
                    'outputTokens': 0.0006,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                },
                'regions': ['eastus', 'westus', 'westeurope']
            }
        ]

    return {
        'name': 'Azure OpenAI',
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
        print("Fetching Azure OpenAI pricing data...")
        provider_data = fetch_pricing_data()
        update_pricing_file(provider_data)
        print("✓ Success")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
