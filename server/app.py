from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper.scraper import scrape_async
from scraper.config import SCRAPE_URLS
import asyncio

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:3000",
    "https://component-scraper--forseti-305ad.europe-west4.hosted.app"
    ]}})

def run_scraper(searchQuery):
    searchQuery = searchQuery.strip()
    result = asyncio.run(scrape_async(searchQuery))
cache = Cache(app, config={
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6379"),
    "CACHE_DEFAULT_TIMEOUT": 1200  # 20 minutes
})

def run_scraper(queries):
    result = asyncio.run(scrape_async(queries))
    return result


@app.route('/api/search', methods=['GET'])
def search():
    searchQuery = request.args.get('q')
    print(f"Received search query: {searchQuery}")
    data = run_scraper(searchQuery)

    results = {
        "searchQuery": searchQuery,
        "data": data
        }
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=8000)


