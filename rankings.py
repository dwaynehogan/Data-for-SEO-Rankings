import aiohttp
import asyncio
import csv
import base64
import math
import time
import os
from datetime import datetime
from urllib.parse import urlparse

# Constants
MAX_REQUESTS_PER_MINUTE = 2000  # Maximum allowed requests per minute
CONCURRENT_REQUESTS = 200       # Number of concurrent requests (tunable parameter)

async def fetch(session, url, headers, payload):
    async with session.post(url, json=payload, headers=headers) as response:
        status_code = response.status
        if status_code in [200, 201]:
            data = await response.json()
            return data
        else:
            text = await response.text()
            print(f'Error fetching data - Status code: {status_code}')
            print(f'Response: {text}')
            return None

async def get_top_100_results_async(keywords, username, password, domain):
    url = 'https://api.dataforseo.com/v3/serp/google/organic/live/advanced'
    auth_str = f'{username}:{password}'
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/json'
    }

    results = []
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def bound_fetch(sem, session, keyword):
        async with sem:
            print(f'Fetching results for keyword: {keyword}')
            payload = [
                {
                    "keyword": keyword,
                    "location_code": 2840,  # United States
                    "language_code": "en",
                    "device": "desktop",
                    "os": "windows",
                    "depth": 100
                }
            ]
            data = await fetch(session, url, headers, payload)
            if data and 'tasks' in data and len(data['tasks']) > 0:
                task = data['tasks'][0]
                if 'result' in task and len(task['result']) > 0:
                    items = task['result'][0]['items']
                    found = False
                    for item in items:
                        position = item.get('rank_absolute')
                        result_url = item.get('url')

                        # Ensure result_url is a string
                        if isinstance(result_url, bytes):
                            result_url = result_url.decode('utf-8')

                        # Parse the domain from the result_url
                        parsed_url = urlparse(result_url)
                        result_domain = parsed_url.netloc

                        # Ensure result_domain is a string
                        if isinstance(result_domain, bytes):
                            result_domain = result_domain.decode('utf-8')

                        # Remove www. prefix if present
                        if result_domain.startswith('www.'):
                            result_domain = result_domain[4:]

                        # Check if the domains match
                        if result_domain == domain:
                            title = item.get('title')
                            snippet = item.get('description')
                            results.append([keyword, position, result_url, title, snippet])
                            found = True
                            break  # Assuming we only need the first occurrence
                    if not found:
                        # Domain not found in top 100 results
                        results.append([keyword, 100, '', '', ''])
                else:
                    print(f'No results found for keyword: {keyword}')
                    # Domain not found in top 100 results
                    results.append([keyword, 100, '', '', ''])
            else:
                print(f'Error in task data for keyword: {keyword}')
                # Domain not found in top 100 results
                results.append([keyword, 100, '', '', ''])

    async with aiohttp.ClientSession() as session:
        tasks = []
        for keyword in keywords:
            tasks.append(asyncio.create_task(bound_fetch(semaphore, session, keyword)))

        # Rate limiting to ensure we don't exceed 2000 requests per minute
        total_keywords = len(keywords)
        total_batches = math.ceil(total_keywords / MAX_REQUESTS_PER_MINUTE)
        batch_size = math.ceil(total_keywords / total_batches)
        for i in range(0, total_keywords, batch_size):
            batch_tasks = tasks[i:i + batch_size]
            await asyncio.gather(*batch_tasks)
            if i + batch_size < total_keywords:
                print('Sleeping for 60 seconds to comply with rate limits...')
                await asyncio.sleep(60)

    return results

def read_keywords_from_csv(input_file):
    keywords = []
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Assuming each row contains one keyword
            if row:
                keywords.append(row[0])
    return keywords

def write_results_to_csv(output_file, results):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write headers
        writer.writerow(['Keyword', 'Position', 'URL', 'Title', 'Snippet'])
        # Write data rows
        writer.writerows(results)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'keywords.csv')  # Replace with your input CSV file
    username = 'username'  # Replace with your DataForSEO username
    password = 'password'  # Replace with your DataForSEO password

    # Provide the domain name here (without subdomain or www)
    domain = 'example.com'  # Replace with your domain

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(script_dir, f'rankings_{domain}_{timestamp}.csv')

    # Read keywords from CSV
    keywords = read_keywords_from_csv(input_file)
    print(f'Total keywords to process: {len(keywords)}')

    # Fetch results asynchronously
    start_time = time.time()
    results = asyncio.run(get_top_100_results_async(keywords, username, password, domain))
    end_time = time.time()

    print(f'Fetched data for all keywords in {end_time - start_time:.2f} seconds.')

    # Write results to CSV
    write_results_to_csv(output_file, results)
    print(f'Results written to {output_file}')

if __name__ == '__main__':
    main()
