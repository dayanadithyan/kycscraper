"""KYC LGA Crawler for https://eservices.elections.gov.lk/pages/ec_ct_KYC_LGA.aspx

This script asynchronously crawls the Sri Lankan Elections Department's public KYC portal
to retrieve information by NIC numbers. Use responsibly and in accordance with local laws.
"""

import aiohttp
import asyncio
import logging
import random
import json
import pickle
import time
import argparse
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from tqdm.asyncio import tqdm_asyncio
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from aiohttp import ClientError, ClientResponseError, ClientTimeout

# Import configuration, with environment variable support
from config import get_config

# Set up logging
logging.basicConfig(
    filename='crawler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CrawlResult:
    """Data class to store crawl results with validation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    nic: Optional[str] = None

def save_json(data: List[Dict[str, Any]], filename: str) -> None:
    """Save data to a JSON file with proper error handling"""
    try:
        output_dir = Path(os.getenv('OUTPUT_DIR', '.'))
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved data to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save JSON data to {filename}: {e}")

def save_pickle(data: List[Dict[str, Any]], filename: str) -> None:
    """Save data to a pickle file with proper error handling"""
    try:
        output_dir = Path(os.getenv('OUTPUT_DIR', '.'))
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Successfully saved data to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save pickle data to {filename}: {e}")

def validate_nic(nic: str) -> bool:
    """Validate the format of an NIC number
    
    Current supported formats:
    - Old format: 9 digits followed by V or X
    - New format: 12 digits
    """
    if len(nic) == 10 and nic[:9].isdigit() and nic[9] in ('V', 'X'):
        return True
    if len(nic) == 12 and nic.isdigit():
        return True
    return False

def validate_response(data: Dict[str, Any], required_keys: List[str]) -> bool:
    """Validate that the response contains all required keys"""
    return all(k in data for k in required_keys)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type((ClientError, asyncio.TimeoutError, ValueError))
)
async def fetch(
    session: aiohttp.ClientSession,
    nic: str,
    config: Dict[str, Any]
) -> CrawlResult:
    """Fetch data for a single NIC with improved error handling"""
    if not validate_nic(nic):
        return CrawlResult(success=False, error=f"Invalid NIC format: {nic}", nic=nic)
    
    headers = config["HEADERS_TEMPLATE"].copy()
    headers["User-Agent"] = random.choice(config["USER_AGENTS"])
    
    # Select proxy if available
    proxy = None
    if config["PROXIES"] and config["PROXIES"][0] is not None:
        proxy = random.choice(config["PROXIES"])
    
    timeout = ClientTimeout(total=config["TIMEOUT"])
    
    try:
        url = f"{config['BASE_URL']}{nic}"
        async with session.get(url, headers=headers, proxy=proxy, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                if validate_response(data, config["REQUIRED_KEYS"]):
                    return CrawlResult(success=True, data=data, nic=nic)
                else:
                    logger.warning(f"Response for NIC {nic} missing required keys")
                    return CrawlResult(success=False, error="Incomplete data", nic=nic)
            elif response.status == 404:
                logger.info(f"No data found for NIC {nic}")
                return CrawlResult(success=False, error="Not found", nic=nic)
            elif response.status == 429:
                retry_after = response.headers.get('Retry-After', '60')
                logger.warning(f"Rate limited. Retry after {retry_after}s")
                await asyncio.sleep(int(retry_after))
                raise ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limited",
                    headers=response.headers
                )
            else:
                logger.error(f"Failed to fetch NIC {nic}: HTTP {response.status}")
                return CrawlResult(
                    success=False,
                    error=f"HTTP error: {response.status}",
                    nic=nic
                )
    except asyncio.TimeoutError:
        logger.error(f"Timeout while fetching NIC {nic}")
        raise
    except Exception as e:
        logger.error(f"Error fetching NIC {nic}: {e}")
        return CrawlResult(success=False, error=str(e), nic=nic)

async def crawl_nics(nic_list: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Crawl multiple NICs asynchronously with improved concurrency control"""
    results = []
    errors = []
    
    connector = aiohttp.TCPConnector(limit=config.get("CONNECTION_LIMIT", 3))
    sem = asyncio.Semaphore(config.get("CONCURRENCY_LIMIT", 2))

    async with aiohttp.ClientSession(connector=connector) as session:
        async def bound_fetch(nic):
            async with sem:
                # Respect rate limits with randomized delay
                await asyncio.sleep(random.uniform(
                    config.get("MIN_DELAY", 1.5),
                    config.get("MAX_DELAY", 3.5)
                ))
                
                result = await fetch(session, nic, config)
                if result.success and result.data:
                    results.append(result.data)
                else:
                    errors.append({
                        "nic": nic,
                        "error": result.error
                    })

        # Show progress bar
        tasks = [bound_fetch(nic) for nic in nic_list]
        await tqdm_asyncio.gather(*tasks)

    # Log error statistics
    if errors:
        logger.warning(f"Encountered {len(errors)} errors out of {len(nic_list)} requests")
        error_counts = {}
        for err in errors:
            error_type = err.get("error", "Unknown")
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        logger.warning(f"Error distribution: {error_counts}")
        
        # Save errors for analysis
        save_json(errors, "crawl_errors.json")

    return results

def generate_nic_list(pattern: str, start: int, count: int) -> List[str]:
    """Generate a list of NICs based on pattern and range"""
    nic_list = []
    for i in range(start, start + count):
        nic = pattern.format(str(i).zfill(6))
        if validate_nic(nic):
            nic_list.append(nic)
    return nic_list

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="KYC LGA Crawler")
    parser.add_argument(
        "--pattern",
        default="1990{0}V",
        help="Pattern for generating NICs, e.g., '1990{0}V'"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting number for NIC generation"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of NICs to generate and crawl"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Maximum concurrent requests"
    )
    parser.add_argument(
        "--output",
        default="kyc_lga_all_data.json",
        help="Output filename for JSON data"
    )
    return parser.parse_args()

async def main_async(args):
    """Async main function with improved structure"""
    start = time.time()
    
    # Load configuration
    config = get_config()
    
    # Update config with command line arguments
    config["CONCURRENCY_LIMIT"] = args.concurrency
    
    # Generate NIC list
    logger.info(f"Generating {args.count} NICs with pattern {args.pattern} starting from {args.start}")
    nic_list = generate_nic_list(args.pattern, args.start, args.count)
    
    # Crawl NICs
    logger.info(f"Starting crawl of {len(nic_list)} NICs with concurrency {config['CONCURRENCY_LIMIT']}")
    data = await crawl_nics(nic_list, config)
    
    # Save results
    save_json(data, args.output)
    save_pickle(data, "kyc_lga_backup.pkl")
    
    # Log summary
    elapsed = time.time() - start
    logger.info(f"Crawling completed in {elapsed:.2f} seconds")
    logger.info(f"Retrieved {len(data)} records out of {len(nic_list)} attempts")
    
    return data

def main():
    """Entry point with proper exception handling"""
    try:
        args = parse_arguments()
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(main_async(args))
        return 0
    except KeyboardInterrupt:
        logger.info("Crawling interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)