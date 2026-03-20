import json
import bs4
import random
import re
from scraper.config import USER_AGENTS, SCRAPE_URLS, HEADERS
import aiohttp
import asyncio

async def fetch(session, url, headers):
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.get(url, headers=headers, timeout=timeout) as response:
            return await response.text()
    except Exception as e:
        print(f"Scraping failed for {url}: {e}")
        return None

async def scrape_async(queries):
    if isinstance(queries, str):
        queries = [queries]

    headers = {
        "authority": HEADERS["authority"],
        "accept": HEADERS["accept"],
        "accept-language": HEADERS["acceptLanguage"],
        "cache-control": HEADERS["cacheControl"],
        "Content-Type": HEADERS["contentType"],
        "User-Agent": random.choice(USER_AGENTS)
    }

    async with aiohttp.ClientSession() as session:
        tasks = []
        for query in queries:
            for key, value in SCRAPE_URLS.items():
                url = value[0] + query
                scrape_function = globals().get(value[1])
                if scrape_function:
                    tasks.append(process_scrape(session, url, headers, key, scrape_function))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Combine into final format; if the same (part_number, source) appears across
    # multiple query variants, keep the first result (don't overwrite with duplicates)
    combined_data = {}
    for result in results:
        if isinstance(result, Exception):
            print(f"Scrape task failed: {result}")
            continue
        source, data = result
        if not data:
            continue
        products = data.get("products", {})
        for part_number, entries in products.items():
            if part_number not in combined_data:
                combined_data[part_number] = {}
            if source not in combined_data[part_number]:
                combined_data[part_number][source] = {
                    "productData": entries,
                    "websiteLink": data["websiteLink"]
                }

    return combined_data

async def process_scrape(session, url, headers, key, scrape_function):
    html = await fetch(session, url, headers)
    if not html:
        return key, None

    try:
        soup = bs4.BeautifulSoup(html, 'lxml')
        jsonResult = clean_data(scrape_function(soup))
        return key, {
            "products": jsonResult,
            "websiteLink": url
        }
    except Exception as e:
        print(f"Parsing failed for {url}: {e}")
        return key, None

def clean_data(data):
    if not isinstance(data, dict):
        return data
    for part_number, offers in list(data.items()):
        cleaned = []
        for offer in offers:
            stock = offer.get("stock", "") or ""
            stock = str(stock)
            if not stock.isnumeric():
                stock = re.sub(r'\D', '', stock)
            if stock and int(stock) != 0:
                offer["stock"] = stock
                cleaned.append(offer)
        if cleaned:
            data[part_number] = cleaned
        else:
            del data[part_number]
    return data

def scrape_all(data):
    return {}

def scrape_oemtrade(data):
    partsDictionary = {}
    partElems = data.find_all('section', class_='distributor-results')
    for part in partElems:
        offers = part.find_all("tr", class_="row")
        for offer in offers:
            try:
                partNumber = offer.get('data-part')
                if not partNumber:
                    continue
                if partNumber not in partsDictionary:
                    partsDictionary[partNumber] = []
                distributor = offer.get('data-distributor_name')
                manufacturer = offer.get('data-mfr')
                stock = offer.get('data-instock')
                price = offer.get('data-price')
                if not price:
                    continue

                priceList = json.loads(price)
                formattedPrices = [
                    {"quantity": qty, "price": f"${float(p):.3f}"}
                    for qty, currency, p in priceList
                ]

                partsDictionary[partNumber].append({
                    "distributor": distributor,
                    "manufacturer": manufacturer,
                    "stock": stock,
                    "prices": formattedPrices
                })
            except Exception as e:
                print(f"[oemtrade] skipping offer: {e}")
                continue
    return partsDictionary

def scrape_octopart(data):
    partsDictionary = {}
    partElems = data.find_all('div', attrs={'data-sentry-component': 'Part'})
    for part in partElems:
        offers = part.find_all('tr', attrs={'data-testid': 'offer-row'})
        if not offers:
            continue
        try:
            manufacturer = part.select_one('[data-testid="serp-part-header-manufacturer"]').get_text(strip=True)
            partNumber = part.select_one('[data-testid="serp-part-header-mpn"]').get_text(strip=True)
        except Exception as e:
            print(f"[octopart] skipping part, missing header: {e}")
            continue
        if partNumber not in partsDictionary:
            partsDictionary[partNumber] = []
        for offer in offers:
            try:
                distributor = offer.select_one('[data-sentry-component="Distributor"]').get_text(strip=True)
                stock = offer.select_one('[data-sentry-component="Stock"]').get_text(strip=True)
                prices = offer.select('[data-sentry-component="PriceAtQty"]')[:3]
                priceRange = [1, 10, 100]
                formattedPrices = [
                    {"quantity": priceRange[i], "price": f"${p.get_text(strip=True)}"}
                    for i, p in enumerate(prices)
                ]
                link = offer.select_one('[data-sentry-component="Sku"]').find('a')['href']
                partsDictionary[partNumber].append({
                    "distributor": distributor,
                    "stock": stock,
                    "prices": formattedPrices,
                    "link": link,
                    "manufacturer": manufacturer
                })
            except Exception as e:
                print(f"[octopart] skipping offer: {e}")
                continue
    return partsDictionary

def scrape_icsource(data):
    jsonResult = []
    partElems = data.find_all('tr', class_='rgRow')
    for part in partElems:
        try:
            cells = part.find_all("td")
            if len(cells) < 4:
                continue
            jsonResult.append({
                "Part Number": cells[0].get_text(strip=True),
                "manufacturer": cells[1].get_text(strip=True),
                "year": cells[2].get_text(strip=True),
                "stock": cells[3].get_text(strip=True),
            })
        except Exception as e:
            print(f"[icsource] skipping row: {e}")
            continue
    return {"ICSource.com": jsonResult}

def scrape_findchips(data):
    partsDictionary = {}
    distributorResults = data.find_all('div', class_='distributor-results')
    for distributor in distributorResults:
        distributorName = distributor.get('data-distributor_name')
        parts = distributor.find_all('tr', class_='row')
        for part in parts:
            try:
                partNumber = part.get('data-mfrpartnumber')
                if not partNumber:
                    continue
                if partNumber not in partsDictionary:
                    partsDictionary[partNumber] = []

                price = part.get('data-price')
                stock = part.get('data-stock')
                manufacturer = part.get('data-mfr')
                distributorNo = part.get('data-distino')

                buy_cell = part.select_one('td.td-buy')
                link_tag = buy_cell.find('a') if buy_cell else None
                link = link_tag['href'] if link_tag else '#'

                if not price:
                    continue
                priceList = json.loads(price)
                formattedPrices = [
                    {"quantity": qty, "price": f"${float(p):.3f}"}
                    for qty, currency, p in priceList
                ]

                partsDictionary[partNumber].append({
                    "manufacturer": manufacturer,
                    "stock": stock,
                    "prices": formattedPrices,
                    "distributor": distributorName,
                    "distributorNo": distributorNo,
                    "link": link
                })
            except Exception as e:
                print(f"[findchips] skipping part: {e}")
                continue
    return partsDictionary
