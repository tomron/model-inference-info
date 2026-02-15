#!/usr/bin/env python3
"""
Orchestration script to run all provider data collection scripts.

This script runs all provider fetchers and collects results.
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_name):
    """Run a provider script and return success status."""
    script_path = Path(__file__).parent / script_name
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print('='*60)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            check=True
        )
        print(f"✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {script_name} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"✗ {script_name} failed: {e}")
        return False


def main():
    """Run all provider scripts."""
    print("Starting data collection from all providers...\n")

    providers = [
        'fetch_aws.py',
        'fetch_anthropic.py',
        'fetch_openai.py',
        'fetch_github.py',
        'fetch_cursor.py',
        'fetch_gcp.py',
        'fetch_azure.py',
    ]

    results = {}
    for provider in providers:
        results[provider] = run_script(provider)

    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print('='*60)

    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful

    for provider, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {provider}")

    print(f"\nTotal: {successful}/{len(results)} successful, {failed} failed")

    # Exit with error if any failed
    if failed > 0:
        print("\n⚠️  Some providers failed - see errors above")
        return 1

    print("\n✓ All providers updated successfully")
    return 0


if __name__ == '__main__':
    sys.exit(main())
