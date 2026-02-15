#!/usr/bin/env python3
"""
Fetch pricing data from OpenAI.

Data source: https://openai.com/api/pricing/
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
    """Fetch OpenAI pricing data by scraping the pricing page."""
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    url = 'https://openai.com/api/pricing/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"✗ Error fetching OpenAI pricing page: {e}")
        raise

    soup = BeautifulSoup(response.text, 'html.parser')

    models = []
    pricing_found = False

    # OpenAI typically uses tables or structured divs for pricing
    # Look for pricing tables
    tables = soup.find_all('table')

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue

            row_text = ' '.join(cell.get_text().strip() for cell in cells)

            # Look for GPT-4o, GPT-4o mini, o1, o1-mini pricing
            model_patterns = {
                'GPT-4o': {'modelId': 'gpt-4o', 'pattern': r'gpt-?4o(?!\s*mini)'},
                'GPT-4o mini': {'modelId': 'gpt-4o-mini', 'pattern': r'gpt-?4o\s*mini'},
                'o1': {'modelId': 'o1', 'pattern': r'(?<!-)o1(?!\s*mini)(?!-)'},
                'o1-mini': {'modelId': 'o1-mini', 'pattern': r'o1-?mini'},
            }

            for model_name, model_info in model_patterns.items():
                if re.search(model_info['pattern'], row_text, re.IGNORECASE):
                    # Extract prices - look for dollar amounts
                    prices = re.findall(r'\$(\d+\.?\d+)', row_text)

                    if len(prices) >= 2:
                        input_cost = float(prices[0])
                        output_cost = float(prices[1])

                        # Skip if already added
                        if not any(m['modelId'] == model_info['modelId'] for m in models):
                            models.append({
                                'name': model_name,
                                'modelId': model_info['modelId'],
                                'pricing': {
                                    'inputTokens': input_cost,
                                    'outputTokens': output_cost,
                                    'unit': 'per 1K tokens',
                                    'currency': 'USD'
                                }
                            })
                            pricing_found = True

    # Fallback to known pricing if scraping failed
    if not pricing_found:
        print("⚠️  Could not scrape pricing from page, using known pricing as fallback")
        models = [
            {
                'name': 'GPT-4o',
                'modelId': 'gpt-4o',
                'pricing': {
                    'inputTokens': 0.0025,
                    'outputTokens': 0.01,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                }
            },
            {
                'name': 'GPT-4o mini',
                'modelId': 'gpt-4o-mini',
                'pricing': {
                    'inputTokens': 0.00015,
                    'outputTokens': 0.0006,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                }
            },
            {
                'name': 'o1',
                'modelId': 'o1',
                'pricing': {
                    'inputTokens': 0.015,
                    'outputTokens': 0.06,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                }
            },
            {
                'name': 'o1-mini',
                'modelId': 'o1-mini',
                'pricing': {
                    'inputTokens': 0.003,
                    'outputTokens': 0.012,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                }
            }
        ]

    return {
        'name': 'OpenAI',
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
