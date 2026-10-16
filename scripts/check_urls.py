"""Record every reading URL response. Review all non-200 responses by hand."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from collections import Counter
import requests
from check import rows


def check(row):
    result = {k: row[k] for k in ('title', 'url')}
    try:
        response = requests.get(row['url'], timeout=(10, 35), headers={'User-Agent': 'Mozilla/5.0 (compatible; ReadingLinkCheck/1.0)'}, stream=True)
        result.update(status=response.status_code, final_url=response.url)
        # A short public response excerpt helps distinguish bot blocks from missing pages.
        if response.status_code != 200:
            from re import sub
            body = next(response.iter_content(12000), b'').decode('utf-8', errors='replace')
            result['response_excerpt'] = sub(r'\s+', ' ', sub(r'<[^>]+>', ' ', body))[:500]
        response.close()
    except requests.RequestException as error:
        result.update(status='ERROR', error=str(error))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('evidence/urls.json'))
    args = parser.parse_args()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, [r for r in rows('readings.yml') if r['url']]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
    print(dict(Counter(str(r['status']) for r in results)))
    for row in results:
        if row['status'] != 200:
            print(row['status'], row['title'], row['url'])
