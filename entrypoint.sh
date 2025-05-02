#!/bin/bash
set -eo pipefail

# Default parameters
PATTERN=${PATTERN:-"1990{0}V"}
START=${START:-1}
COUNT=${COUNT:-100}
CONCURRENCY=${CONCURRENCY:-2}
OUTPUT=${OUTPUT:-"kyc_lga_all_data.json"}

echo "Starting crawler with the following configuration:"
echo "Pattern: $PATTERN"
echo "Start: $START"
echo "Count: $COUNT"
echo "Concurrency: $CONCURRENCY"
echo "Output: $OUTPUT"

# Check if we need to fetch robots.txt first
if [ "${RESPECT_ROBOTS_TXT}" = "true" ]; then
    echo "Checking robots.txt before crawling..."
    python3 -c "
import requests
import sys
import re
import time

try:
    robots_url = 'https://eservices.elections.gov.lk/robots.txt'
    response = requests.get(robots_url, timeout=10)
    
    if response.status_code == 200:
        content = response.text
        disallowed = re.findall(r'Disallow:\s*(.*)', content)
        
        # Check if our API endpoint is disallowed
        api_path = '/api/kyc-lga/search'
        if any(api_path.startswith(d.strip()) for d in disallowed):
            print(f'Error: Crawling {api_path} is disallowed by robots.txt')
            sys.exit(1)
        
        # Check for Crawl-delay directive
        delay_match = re.search(r'Crawl-delay:\s*(\d+)', content)
        if delay_match:
            delay = int(delay_match.group(1))
            print(f'Found Crawl-delay: {delay}s in robots.txt')
            if delay > int(float(\"${MIN_DELAY}\")):
                print(f'Adjusting MIN_DELAY to respect robots.txt')
                export MIN_DELAY=$delay
                export MAX_DELAY=$(($delay + 1))
    else:
        print(f'Warning: Could not fetch robots.txt (status code: {response.status_code})')
        
except Exception as e:
    print(f'Warning: Error checking robots.txt: {e}')
"
fi

# Run the crawler with parameters
python3 kyc_lga_crawler.py \
    --pattern "$PATTERN" \
    --start "$START" \
    --count "$COUNT" \
    --concurrency "$CONCURRENCY" \
    --output "$OUTPUT"

# Check exit status
if [ $? -eq 0 ]; then
    echo "Crawler completed successfully."
    exit 0
else
    echo "Crawler failed with error code $?."
    exit 1
fi