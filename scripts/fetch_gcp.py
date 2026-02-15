#!/usr/bin/env python3
"""
Fetch pricing data from GCP Vertex AI.

Data source: https://cloud.google.com/vertex-ai/generative-ai/pricing
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
    """Fetch GCP Vertex AI pricing by scraping the pricing page."""
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    url = 'https://cloud.google.com/vertex-ai/generative-ai/pricing'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    models = []
    found_models = {}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for tables containing Gemini pricing
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue

                row_text = ' '.join(cell.get_text().strip() for cell in cells)

                # Skip header rows
                if 'model' in row_text.lower() and 'price' in row_text.lower():
                    continue

                # Look for any model with pricing (Gemini, PaLM, etc.)
                if any(keyword in row_text.lower() for keyword in ['gemini', 'palm', 'bison', 'gecko']):
                    prices = re.findall(r'\$(\d+\.?\d*)', row_text)

                    if len(prices) >= 2:
                        # Extract model name from first cell
                        model_name_cell = cells[0].get_text().strip()
                        model_name = re.sub(r'\s+', ' ', model_name_cell).strip()

                        # Skip if empty or too short
                        if not model_name or len(model_name) < 3:
                            continue

                        # Create model ID from name
                        model_id = model_name.lower().replace(' ', '-').replace('.', '-')

                        try:
                            input_cost = float(prices[0])
                            output_cost = float(prices[1])

                            # GCP pricing often in per 1M tokens, convert to per 1K if needed
                            if 'million' in row_text.lower() or '1m' in row_text.lower() or '1,000,000' in row_text:
                                input_cost /= 1000
                                output_cost /= 1000

                            if model_name not in found_models:
                                found_models[model_name] = {
                                    'name': model_name,
                                    'modelId': model_id,
                                    'pricing': {
                                        'inputTokens': input_cost,
                                        'outputTokens': output_cost,
                                        'unit': 'per 1K tokens',
                                        'currency': 'USD'
                                    },
                                    'regions': ['us-central1', 'us-east4', 'europe-west1', 'asia-southeast1']
                                }
                        except (ValueError, IndexError):
                            continue

        # Also scan page text for model patterns
        all_text = soup.get_text()

        # Pattern for Gemini models with pricing
        gemini_pattern = r'(Gemini[\s\w.-]+?)\s+.*?\$(\d+\.?\d+).*?\$(\d+\.?\d+)'
        matches = re.finditer(gemini_pattern, all_text, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            model_name = match.group(1).strip()
            model_name = re.sub(r'\s+', ' ', model_name)

            if model_name not in found_models and len(model_name) > 3:
                try:
                    input_cost = float(match.group(2))
                    output_cost = float(match.group(3))

                    model_id = model_name.lower().replace(' ', '-').replace('.', '-')

                    found_models[model_name] = {
                        'name': model_name,
                        'modelId': model_id,
                        'pricing': {
                            'inputTokens': input_cost,
                            'outputTokens': output_cost,
                            'unit': 'per 1K tokens',
                            'currency': 'USD'
                        },
                        'regions': ['us-central1', 'europe-west1']
                    }
                except (ValueError, IndexError):
                    continue

        models = list(found_models.values())

    except Exception as e:
        print(f"⚠️  Error scraping GCP pricing: {e}")

    # Fallback to known pricing
    if not models:
        print("⚠️  Using known pricing as fallback")
        models = [
            {
                'name': 'Gemini 1.5 Pro',
                'modelId': 'gemini-1.5-pro',
                'pricing': {
                    'inputTokens': 0.00125,
                    'outputTokens': 0.005,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                },
                'regions': ['us-central1', 'us-east4', 'europe-west1', 'asia-southeast1']
            },
            {
                'name': 'Gemini 1.5 Flash',
                'modelId': 'gemini-1.5-flash',
                'pricing': {
                    'inputTokens': 0.000075,
                    'outputTokens': 0.0003,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                },
                'regions': ['us-central1', 'europe-west1']
            }
        ]
    else:
        print(f"✓ Discovered {len(models)} models from pricing page")

    return {
        'name': 'GCP Vertex AI',
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
        print("Fetching GCP Vertex AI pricing data...")
        provider_data = fetch_pricing_data()
        update_pricing_file(provider_data)
        print("✓ Success")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
