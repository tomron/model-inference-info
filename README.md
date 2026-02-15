# AI Model Inference Cost Comparison

[![Build and Test](https://github.com/tomron/model-inference-info/actions/workflows/build-test.yml/badge.svg)](https://github.com/tomron/model-inference-info/actions/workflows/build-test.yml)
[![Deploy to GitHub Pages](https://github.com/tomron/model-inference-info/actions/workflows/deploy.yml/badge.svg)](https://github.com/tomron/model-inference-info/actions/workflows/deploy.yml)
[![Update Pricing Data](https://github.com/tomron/model-inference-info/actions/workflows/update-pricing.yml/badge.svg)](https://github.com/tomron/model-inference-info/actions/workflows/update-pricing.yml)

> Compare AI model inference costs across different providers at a glance

**Live Site:** https://tomron.github.io/model-inference-info/

Inspired by [instances.vantage.sh](https://instances.vantage.sh/), this site provides an easy way to compare pricing for AI inference across major providers including AWS Bedrock, Anthropic, OpenAI, GitHub Copilot, Cursor, GCP Vertex AI, and Azure OpenAI.

## Features

- 📊 **Side-by-side comparison** of model pricing across providers
- 🔍 **Filter by provider, region, or search** for specific models
- ↕️ **Sortable columns** for easy comparison
- 🏆 **Highlights lowest costs** for input and output tokens
- 📱 **Responsive design** for mobile and desktop
- 🤖 **Automatically updated daily** via GitHub Actions
- 🌍 **Regional pricing** where applicable

## Supported Providers

- **AWS Bedrock** - Claude, Titan, and other models via AWS
- **Anthropic** - Direct API pricing for Claude models
- **OpenAI** - GPT-4o, o1, and other OpenAI models
- **GitHub Copilot** - Subscription-based AI assistance
- **Cursor** - AI-powered code editor
- **GCP Vertex AI** - Gemini and other Google models
- **Azure OpenAI** - Azure-hosted OpenAI models

## Development

### Prerequisites

- Node.js 20+
- Python 3.11+

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/tomron/model-inference-info.git
   cd model-inference-info
   ```

2. **Install dependencies**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   npm run preview
   ```

### Project Structure

```
.
├── data/
│   ├── pricing.json      # Pricing data (auto-updated)
│   └── schema.json       # JSON schema for validation
├── scripts/
│   ├── fetch_*.py        # Provider-specific data collectors
│   ├── collect_all.py    # Orchestration script
│   └── validate_data.py  # Data validation
├── src/
│   ├── main.js           # Application entry point
│   ├── data.js           # Data loading and management
│   ├── table.js          # Table rendering
│   ├── filters.js        # Filtering logic
│   ├── sort.js           # Sorting logic
│   ├── utils.js          # Utility functions
│   └── style.css         # Styles
├── .github/workflows/
│   ├── deploy.yml        # GitHub Pages deployment
│   ├── update-pricing.yml # Daily pricing updates
│   └── build-test.yml    # PR validation
└── index.html            # Main HTML file
```

## Data Updates

Pricing data is automatically updated daily at 6:00 AM UTC via GitHub Actions. The workflow:

1. Runs data collection scripts for all providers
2. Validates the collected data against the schema
3. Commits and pushes changes if validation passes
4. Triggers a deployment to GitHub Pages

You can also manually trigger an update from the [Actions tab](https://github.com/tomron/model-inference-info/actions/workflows/update-pricing.yml).

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Adding new providers
- Improving data collection scripts
- Enhancing the UI
- Reporting pricing inaccuracies

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by [Vantage.sh's Instance Comparison](https://instances.vantage.sh/)
- Built with [Vite](https://vitejs.dev/)
- Deployed on [GitHub Pages](https://pages.github.com/)

## Disclaimer

Pricing information is collected from publicly available sources and updated automatically. While we strive for accuracy, prices may change without notice. Always verify pricing on the official provider websites before making decisions.

---

**Last Updated:** Automatically updated daily via GitHub Actions
