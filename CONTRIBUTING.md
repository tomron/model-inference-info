# Contributing to AI Model Inference Cost Comparison

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Add new providers** - Expand coverage to more AI providers
- **Improve data collection** - Enhance scraping accuracy and reliability
- **Report pricing issues** - Flag outdated or incorrect pricing
- **Enhance UI/UX** - Improve the user interface and experience
- **Add features** - Propose and implement new functionality
- **Fix bugs** - Identify and fix issues

## Adding a New Provider

To add support for a new AI provider, follow these steps:

### 1. Create a Data Collection Script

Copy the provider template:

```bash
cp scripts/provider_template.py scripts/fetch_newprovider.py
```

### 2. Implement the `fetch_pricing_data()` Function

Edit `scripts/fetch_newprovider.py` and implement data fetching logic:

```python
def fetch_pricing_data():
    """
    Fetch pricing data from the provider.

    Returns:
        dict: Provider data following the schema
    """
    current_time = get_current_timestamp()

    # TODO: Implement your scraping/API logic here
    # Options:
    # - Use requests + BeautifulSoup for static pages
    # - Use Selenium/Playwright for dynamic content
    # - Call provider API if available

    return {
        "name": "New Provider",
        "lastUpdated": current_time,
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
                "regions": ["us-east-1"]  # Optional
            }
        ]
    }
```

### 3. Add to Orchestration Script

Edit `scripts/collect_all.py` and add your provider to the list:

```python
providers = [
    'fetch_aws.py',
    'fetch_anthropic.py',
    # ... existing providers ...
    'fetch_newprovider.py',  # Add your script here
]
```

### 4. Test Locally

Run your script to verify it works:

```bash
python scripts/fetch_newprovider.py
python scripts/validate_data.py
```

### 5. Update Documentation

Add the provider to the README.md list of supported providers.

### 6. Submit a Pull Request

Create a PR with:
- Your new provider script
- Updated `scripts/collect_all.py`
- Updated README.md
- Sample output in the PR description

## Data Collection Best Practices

### Respect Rate Limits

- Add delays between requests
- Use appropriate User-Agent headers
- Follow the provider's robots.txt

### Handle Errors Gracefully

```python
try:
    # Fetch data
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"✗ Error fetching data: {e}")
    raise
```

### Use Caching During Development

```python
import os
from pathlib import Path

cache_file = Path(__file__).parent / '.cache' / 'provider_data.json'

# Use cached data during development
if os.getenv('USE_CACHE') and cache_file.exists():
    with open(cache_file) as f:
        return json.load(f)
```

### Document Data Sources

Add a comment at the top of your script:

```python
"""
Fetch pricing data from New Provider.

Data source: https://newprovider.com/pricing
Last verified: 2026-02-15
"""
```

## Development Workflow

### Setting Up Your Environment

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feat/add-new-provider`
4. Install dependencies: `npm install && pip install -r requirements.txt`

### Making Changes

1. Make your changes
2. Test locally: `npm run dev`
3. Run validation: `python scripts/validate_data.py`
4. Build: `npm run build`

### Submitting Changes

1. Commit with clear messages: `git commit -m "feat: add NewProvider support"`
2. Push to your fork: `git push origin feat/add-new-provider`
3. Open a Pull Request

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Reporting Issues

### Pricing Inaccuracies

If you notice incorrect pricing data:

1. Open an issue with the title: "Pricing Issue: [Provider] [Model]"
2. Include:
   - Current pricing shown on the site
   - Correct pricing (with source link)
   - Date you verified the pricing

### Bugs

When reporting bugs, include:

- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Browser/environment details
- Screenshots if applicable

## Code Style

### JavaScript

- Use ES6+ features
- Use meaningful variable names
- Add JSDoc comments for functions
- Avoid `innerHTML` - use safe DOM methods

### Python

- Follow PEP 8
- Use type hints where appropriate
- Add docstrings for functions
- Handle errors explicitly

### CSS

- Use CSS variables for theming
- Follow mobile-first approach
- Use semantic class names

## Testing

### Manual Testing Checklist

Before submitting a PR:

- [ ] Site builds without errors (`npm run build`)
- [ ] Data validation passes (`python scripts/validate_data.py`)
- [ ] Filters work correctly
- [ ] Sorting works on all columns
- [ ] Responsive design works on mobile
- [ ] No console errors in browser

### Adding Tests

If you're adding significant functionality, consider adding tests:

- Python: Add to `scripts/test_validate_data.py`
- JavaScript: (Future) Add to test suite

## Questions?

If you have questions about contributing:

1. Check existing issues and PRs
2. Open a new issue with the "question" label
3. Reach out in discussions

Thank you for contributing! 🎉
