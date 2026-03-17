from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from scraper.scraper import scrape_async
from scraper.config import SCRAPE_URLS, COMMON_SUFFIXES
import asyncio
import re
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:3000",
    "https://component-scraper--forseti-305ad.europe-west4.hosted.app"
    ]}})

cache = Cache(app, config={
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6379"),
    "CACHE_DEFAULT_TIMEOUT": 1200  # 20 minutes
})

def run_scraper(queries):
    result = asyncio.run(scrape_async(queries))
    return result

def generate_variants(query):
    """Generate search query variants by progressively stripping ordering-code suffixes.

    Example: BTN7960BAUMA1 -> [BTN7960BAUMA1, BTN7960BAUM, BTN7960B]
      - BTN7960BAUM: stripped tape/reel code A1 (letter + digit pattern)
      - BTN7960B:    stripped packaging code AUM (all-letter suffix after digit+optional letter)
    """
    query = query.strip()
    seen = set()
    variants = []

    def add(v):
        if v and len(v) >= 4 and v not in seen:
            seen.add(v)
            variants.append(v)

    add(query)
    current = re.sub(r'[\s\-_]', '', query.upper())
    add(current)

    # Strip known tape/reel/packaging suffixes (e.g. TR, REEL, PBF)
    changed = True
    while changed:
        changed = False
        for suf in COMMON_SUFFIXES:
            if current.endswith(suf) and len(current) - len(suf) >= 4:
                current = current[:-(len(suf))]
                add(current)
                changed = True
                break

    # Strip trailing letter+digit(s) tape/reel codes not in COMMON_SUFFIXES (e.g. A1, B2)
    m = re.match(r'^(.{4,})([A-Z]\d{1,2})$', current)
    if m:
        current = m.group(1)
        add(current)

    # Strip trailing all-letter packaging code after a digit+optional-letter base
    # e.g. BTN7960BAUM -> group(1)=BTN7960B  group(2)=AUM
    m = re.match(r'^(.*\d[A-Z]?)([A-Z]{2,4})$', current)
    if m and len(m.group(1)) >= 4:
        add(m.group(1))

    return variants

@app.route('/api/search', methods=['GET'])
def search():
    searchQuery = request.args.get('q')
    queries = generate_variants(searchQuery)
    cache_key = queries[-1]  # most-stripped variant as the canonical key
    print(f"Received search query: {searchQuery}, searching variants: {queries}, cache key: {cache_key}")

    data = cache.get(cache_key)
    if data is None:
        data = run_scraper(queries)
        cache.set(cache_key, data)
    else:
        print(f"Cache hit for: {cache_key}")

    return jsonify({"searchQuery": searchQuery, "data": data})

if __name__ == '__main__':
    app.run(debug=True, port=8000)


