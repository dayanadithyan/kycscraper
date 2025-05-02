"""KYC LGA Crawler for https://eservices.elections.gov.lk/pages/ec_ct_KYC_LGA.aspx"""

import aiohttp
import asyncio
import async_timeout
import logging
import random
import json
import pickle
import time
from tqdm.asyncio import tqdm_asyncio
from tenacity import retry, wait_exponential, stop_after_attempt
from config import USER_AGENTS, HEADERS_TEMPLATE, BASE_URL, TIMEOUT, PROXIES, REQUIRED_KEYS

logging.basicConfig(filename='crawler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_pickle(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
async def fetch(session, nic):
    headers = HEADERS_TEMPLATE.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)
    proxy = random.choice(PROXIES)
    async with async_timeout.timeout(TIMEOUT):
        async with session.get(BASE_URL + nic, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to fetch NIC {nic}: HTTP {response.status}")

async def crawl_nics(nic_list):
    results = []
    connector = aiohttp.TCPConnector(limit=3)
    sem = asyncio.Semaphore(2)

    async with aiohttp.ClientSession(connector=connector) as session:
        async def bound_fetch(nic):
            async with sem:
                try:
                    await asyncio.sleep(random.uniform(1.5, 3.5))
                    data = await fetch(session, nic)
                    if data and all(k in data for k in REQUIRED_KEYS):
                        results.append(data)
                    else:
                        logging.warning(f"Incomplete data for NIC {nic}")
                except Exception as e:
                    logging.error(f"Error fetching NIC {nic}: {e}")

        await tqdm_asyncio.gather(*(bound_fetch(nic) for nic in nic_list))

    return results

def main():
    start = time.time()
    nic_list = [f"1990{str(i).zfill(6)}V" for i in range(1, 100)]  # demo set

    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(crawl_nics(nic_list))

    save_json(data, 'kyc_lga_all_data.json')
    save_pickle(data, 'kyc_lga_backup.pkl')
    logging.info(f"Crawling completed in {time.time() - start:.2f} seconds with {len(data)} records")

if __name__ == '__main__':
    main()
