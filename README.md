# KYC LGA Crawler

Asynchronously crawls the Sri Lankan Elections Department's public KYC portal.

## Features

- Async crawler with `aiohttp`
- Retry logic (`tenacity`)
- User-agent rotation
- Proxy support
- Integrity checks
- JSON + Pickle backup
- CI/CD via GitHub Actions
- Dockerized for portability

## Usage

### Local Docker Run

```bash
docker build -t kyc-lga-crawler .
docker run --rm -v "$PWD":/app kyc-lga-crawler

```markdown
kyc-lga-crawler/
├── .github/
│   └── workflows/
│       └── crawl.yml
├── config.py
├── Dockerfile
├── entrypoint.sh
├── kyc_lga_crawler.py
├── README.md
└── requirements.txt
```
