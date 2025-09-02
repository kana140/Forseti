from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper.scraper import scrape_async
from scraper.config import SCRAPE_URLS
import asyncio

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:3000",
    "https://*.web.app",
    "https://*.firebaseapp.com"
    ]}})

def run_scraper(searchQuery):
    searchQuery = searchQuery.strip()
    result = asyncio.run(scrape_async(searchQuery))
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


