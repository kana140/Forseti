import azure.functions as func
import asyncio
import re
import os
import json
import redis

from scraper.scraper import scrape_async
from scraper.config import COMMON_SUFFIXES

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = 1200  # 20 minutes

r = redis.from_url(REDIS_URL)


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


@app.route(route="api/search", methods=["GET"])
def search(req: func.HttpRequest) -> func.HttpResponse:
    search_query = req.params.get("q")
    if not search_query:
        return func.HttpResponse(
            json.dumps({"error": "Missing query parameter"}),
            status_code=400,
            mimetype="application/json"
        )

    queries = generate_variants(search_query)
    cache_key = queries[-1]  # most-stripped variant as the canonical key
    print(f"Received search query: {search_query}, searching variants: {queries}, cache key: {cache_key}")

    cached = r.get(cache_key)
    if cached is not None:
        print(f"Cache hit for: {cache_key}")
        data = json.loads(cached)
    else:
        try:
            data = asyncio.run(scrape_async(queries))
            r.setex(cache_key, CACHE_TTL, json.dumps(data))
        except Exception as e:
            print(f"Scraper error: {e}")
            return func.HttpResponse(
                json.dumps({"searchQuery": search_query, "data": {}}),
                status_code=200,
                mimetype="application/json"
            )

    try:
        r.zincrby("popular_searches", 1, cache_key)
    except Exception as e:
        print(f"Redis popularity tracking failed: {e}")

    return func.HttpResponse(
        json.dumps({"searchQuery": search_query, "data": data}),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="api/popular", methods=["GET"])
def popular(req: func.HttpRequest) -> func.HttpResponse:
    try:
        top = r.zrevrange("popular_searches", 0, 4)
        return func.HttpResponse(
            json.dumps({"queries": [q.decode() for q in top]}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        print(f"Redis popular queries failed: {e}")
        return func.HttpResponse(
            json.dumps({"queries": []}),
            status_code=200,
            mimetype="application/json"
        )
