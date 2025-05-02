USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)..."
]

HEADERS_TEMPLATE = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9"
}

BASE_URL = "https://eservices.elections.gov.lk/api/kyc-lga/search?nic="
TIMEOUT = 15
PROXIES = [None]  # Add proxy URLs if needed
REQUIRED_KEYS = ["nic", "name", "status"]
