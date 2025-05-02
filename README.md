# KYC LGA Crawler

An asynchronous crawler for the Sri Lankan Elections Department's public KYC portal.

## ⚠️ Legal and Ethical Considerations

Before using this crawler, consider the following:

1. **Terms of Service**: Ensure you comply with the website's terms of service.
2. **Rate Limiting**: This tool implements rate limiting to avoid overloading the server.
3. **Data Privacy**: The information retrieved may contain personal data subject to data protection laws.
4. **Authorization**: Confirm you have legal authorization to access and store the retrieved data.

**This tool is provided for educational purposes only. Use at your own risk and responsibility.**

## Features

- Asynchronous HTTP requests with `aiohttp`
- Robust retry logic with `tenacity`
- Configurable rate limiting and concurrency
- User-agent rotation
- Proxy support
- Comprehensive error handling and logging
- Input and output validation
- Command-line interface for flexible usage
- Environment variable configuration
- Docker containerization
- CI/CD pipeline with GitHub Actions

## Requirements

- Python 3.10+
- Docker (optional)

## Installation

### Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/kyc-lga-crawler.git
cd kyc-lga-crawler

# Install dependencies
pip install -r requirements.txt
