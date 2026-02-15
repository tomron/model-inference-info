#!/usr/bin/env python3
"""
Fetch pricing data from AWS Bedrock.

Data source: AWS Price List API
Reference: https://aws.amazon.com/bedrock/pricing/
Last verified: 2026-02-15
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests


def fetch_pricing_data():
    """
    Fetch AWS Bedrock pricing data using AWS Price List API.

    The AWS Price List API provides programmatic access to pricing.
    """
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    # AWS Price List Service API endpoint
    # Note: This is a public API and doesn't require AWS credentials
    url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/index.json'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    models = []
    pricing_found = False

    try:
        print("Fetching AWS Bedrock pricing from Price List API...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Parse the AWS pricing data structure
        products = data.get('products', {})
        terms = data.get('terms', {}).get('OnDemand', {})

        # Track models we've found
        model_pricing = {}

        for product_id, product_info in products.items():
            attributes = product_info.get('attributes', {})

            # Look for Anthropic Claude models
            model_name = attributes.get('modelName', '')
            operation = attributes.get('operation', '')

            # Filter for inference operations
            if 'Inference' in operation or 'InvokeModel' in operation:
                # Get pricing from terms
                if product_id in terms:
                    price_dimensions = list(terms[product_id].values())[0].get('priceDimensions', {})

                    for dimension in price_dimensions.values():
                        price_per_unit = float(dimension.get('pricePerUnit', {}).get('USD', 0))
                        unit = dimension.get('unit', '')
                        description = dimension.get('description', '')

                        # Determine if this is input or output tokens
                        is_input = 'input' in description.lower() or 'request' in description.lower()
                        is_output = 'output' in description.lower() or 'response' in description.lower()

                        if model_name and (is_input or is_output):
                            if model_name not in model_pricing:
                                model_pricing[model_name] = {
                                    'attributes': attributes,
                                    'input': None,
                                    'output': None
                                }

                            if is_input:
                                model_pricing[model_name]['input'] = price_per_unit
                            elif is_output:
                                model_pricing[model_name]['output'] = price_per_unit

        # Convert to our format
        for model_name, pricing_info in model_pricing.items():
            if pricing_info['input'] is not None and pricing_info['output'] is not None:
                # Get model ID from attributes
                model_id = pricing_info['attributes'].get('modelId', model_name.lower().replace(' ', '-'))

                # Get regions
                location = pricing_info['attributes'].get('location', '')
                regions = []
                if location:
                    # Map AWS location names to region codes
                    region_map = {
                        'US East (N. Virginia)': 'us-east-1',
                        'US West (Oregon)': 'us-west-2',
                        'EU (Ireland)': 'eu-west-1',
                        'Asia Pacific (Singapore)': 'ap-southeast-1',
                        'Asia Pacific (Tokyo)': 'ap-northeast-1',
                    }
                    if location in region_map:
                        regions.append(region_map[location])

                models.append({
                    'name': model_name,
                    'modelId': model_id,
                    'pricing': {
                        'inputTokens': pricing_info['input'],
                        'outputTokens': pricing_info['output'],
                        'unit': 'per 1K tokens',
                        'currency': 'USD'
                    },
                    'regions': regions if regions else None
                })
                pricing_found = True

    except Exception as e:
        print(f"⚠️  Error fetching from AWS API: {e}")

    # Fallback to known pricing if API fetch failed
    if not pricing_found:
        print("⚠️  Using known pricing as fallback")
        models = [
            {
                'name': 'Claude 3.5 Sonnet',
                'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'pricing': {
                    'inputTokens': 0.003,
                    'outputTokens': 0.015,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                },
                'regions': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1']
            },
            {
                'name': 'Claude 3.5 Haiku',
                'modelId': 'anthropic.claude-3-5-haiku-20241022-v1:0',
                'pricing': {
                    'inputTokens': 0.001,
                    'outputTokens': 0.005,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                },
                'regions': ['us-east-1', 'us-west-2', 'eu-west-1']
            },
            {
                'name': 'Claude 3 Opus',
                'modelId': 'anthropic.claude-3-opus-20240229-v1:0',
                'pricing': {
                    'inputTokens': 0.015,
                    'outputTokens': 0.075,
                    'unit': 'per 1K tokens',
                    'currency': 'USD'
                },
                'regions': ['us-east-1', 'us-west-2']
            }
        ]

    return {
        'name': 'AWS Bedrock',
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
        print("Fetching AWS Bedrock pricing data...")
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
