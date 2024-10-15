# README

## Overview

This script retrieves rankings for a specific domain using the [DataForSEO API](https://www.dataforseo.com/) and exports the results to a CSV file. The script is built with `aiohttp` and `asyncio` to efficiently handle large batches of requests while adhering to API rate limits.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3.7+
- A valid [DataForSEO API account](https://www.dataforseo.com/).
- A CSV file containing a list of keywords (one keyword per row).

## Required Dependencies


   ```bash
   pip install aiohttp
   ```

## Usage

### Configuration

- Place a CSV file named `keywords.csv` in the root directory (or modify the script to point to your CSV file).
- Update the `username`, `password`, and `domain` variables in the `main()` function with your DataForSEO API credentials and target domain.

### Running the Script

To run the script, execute:

```bash
python script_name.py
```

### Script Behavior

- The script reads keywords from the CSV file.
- It sends asynchronous requests to the DataForSEO API to fetch the top 100 Google results for each keyword.
- It checks if your specified domain appears in the results, capturing the rank, URL, title, and snippet.
- The results are saved to a timestamped CSV file.

### Output

The output CSV will have the following columns:

- `Keyword`: The keyword for which rankings were fetched.
- `Position`: The rank of your domain for the keyword (1-100).
- `URL`: The URL from the search results.
- `Title`: The title of the ranked page.
- `Snippet`: The description or snippet from the search result.

### Example CSV Output

```
Keyword,Position,URL,Title,Snippet
"best laptops",1,"https://example.com/laptops","Best Laptops of 2023","Explore the best laptops of 2023..."
"cheap flights",100,"","",""
```

## Rate Limiting

The script is designed to handle up to 2000 API requests per minute, as allowed by the DataForSEO API. It pauses for 60 seconds after each batch of requests to comply with rate limits.

## Modifying Script Parameters

- **CONCURRENT_REQUESTS**: Adjust the number of concurrent requests (default is 200). Increasing this value may reduce runtime but could potentially lead to rate-limit violations.
- **MAX_REQUESTS_PER_MINUTE**: This defines the maximum API calls per minute (default is 2000).

## Error Handling

If the API request fails or no results are found, the script logs the error and moves to the next keyword. In case the domain is not found in the top 100 results, the position is marked as `100`.
