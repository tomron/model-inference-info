#!/usr/bin/env python3
"""
Fetch pricing data from Anthropic.

Data source: https://www.anthropic.com/pricing
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
    """Fetch Anthropic pricing data by scraping the pricing page."""
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    url = 'https://www.anthropic.com/pricing'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"✗ Error fetching Anthropic pricing page: {e}")
        raise

    soup = BeautifulSoup(response.text, 'html.parser')

    models = []
    found_models = {}  # Track models by name to avoid duplicates

    # Strategy 1: Look for pricing tables
    tables = soup.find_all('table')

    for table in tables:
        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:  # Need at least model name, input price, output price
                continue

            row_text = ' '.join(cell.get_text().strip() for cell in cells)

            # Skip header rows
            if 'model' in row_text.lower() and 'input' in row_text.lower():
                continue

            # Look for rows that contain "Claude" and pricing
            if 'claude' in row_text.lower():
                # Extract all prices from the row
                prices = re.findall(r'\$?(\d+\.?\d+)', row_text)

                if len(prices) >= 2:
                    # Try to extract model name from first cell
                    model_name_cell = cells[0].get_text().strip()

                    # Clean up model name
                    model_name = re.sub(r'\s+', ' ', model_name_cell).strip()

                    # Skip if empty or looks like a header
                    if not model_name or len(model_name) < 3:
                        continue

                    # Create model ID from name
                    model_id = model_name.lower().replace(' ', '-').replace('.', '-')

                    # Parse prices
                    try:
                        input_cost = float(prices[0])
                        output_cost = float(prices[1])

                        # Add to found models
                        if model_name not in found_models:
                            found_models[model_name] = {
                                'name': model_name,
                                'modelId': model_id,
                                'pricing': {
                                    'inputTokens': input_cost,
                                    'outputTokens': output_cost,
                                    'unit': 'per 1K tokens',
                                    'currency': 'USD'
                                }
                            }
                    except (ValueError, IndexError):
                        continue

    # Strategy 2: Look for structured data or JSON-LD
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            # Parse structured data if it contains pricing info
            # This is a placeholder - structure varies by site
        except:
            pass

    # Strategy 3: Look for divs/sections with pricing information
    # Search for any element containing "claude" and price patterns
    all_text = soup.get_text()

    # Find all mentions of Claude models with nearby pricing
    claude_pattern = r'(Claude\s+[\d.]+\s+\w+(?:\s+\w+)?)[^\$]*?\$(\d+\.?\d+)[^\$]*?\$(\d+\.?\d+)'
    matches = re.finditer(claude_pattern, all_text, re.IGNORECASE | re.MULTILINE)

    for match in matches:
        model_name = match.group(1).strip()
        input_cost = float(match.group(2))
        output_cost = float(match.group(3))

        # Normalize model name
        model_name = re.sub(r'\s+', ' ', model_name)
        model_id = model_name.lower().replace(' ', '-').replace('.', '-')

        if model_name not in found_models:
            found_models[model_name] = {
                'name': model_name,
                'modelId': model_id,
                'pricing': {
                    'inputTokens': input_cost,
                    'outputTokens': output_cost,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                }
            }

    models = list(found_models.values())

    # If no models found, use fallback
    if not models:
        print("⚠️  Could not scrape pricing from page, using known pricing as fallback")
        models = [
            {
                'name': 'Claude 3.5 Sonnet',
                'modelId': 'claude-3-5-sonnet-20241022',
                'pricing': {
                    'inputTokens': 0.003,
                    'outputTokens': 0.015,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                }
            },
            {
                'name': 'Claude 3.5 Haiku',
                'modelId': 'claude-3-5-haiku-20241022',
                'pricing': {
                    'inputTokens': 0.001,
                    'outputTokens': 0.005,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                }
            },
            {
                'name': 'Claude 3 Opus',
                'modelId': 'claude-3-opus-20240229',
                'pricing': {
                    'inputTokens': 0.015,
                    'outputTokens': 0.075,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                }
            }
        ]
    else:
        print(f"✓ Discovered {len(models)} models from pricing page")

    return {
        'name': 'Anthropic',
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
        print("Fetching Anthropic pricing data...")
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
