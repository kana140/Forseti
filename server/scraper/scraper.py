import json
import bs4
from email.message import EmailMessage
import random
import re
from scraper.config import USER_AGENTS, SCRAPE_URLS, HEADERS
import aiohttp
import asyncio

# TO DO:
# refactor scraping code for modularity

async def fetch(session, url, headers):
    try:
        async with session.get(url, headers=headers) as response:
            return await response.text()
    except Exception as e:
        print(f"Scraping failed for {url}: {e}")
        return None

async def scrape_async(searchQuery):
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
        for key, value in SCRAPE_URLS.items():
            url = value[0] + searchQuery
            scrape_function = globals().get(value[1])
            if scrape_function:
                tasks.append(process_scrape(session, url, headers, key, scrape_function))
        results = await asyncio.gather(*tasks)
        
    # Combine into final format
    combined_data = {}
    for source, result in results:
        if not result:
            continue
        products = result.get("products", {})
        for part_number, entries in products.items():
            if part_number not in combined_data:
                combined_data[part_number] = {}
            combined_data[part_number][source] = {
                "productData": entries,
                "websiteLink": result["websiteLink"]
            }

    return combined_data

async def process_scrape(session, url, headers, key, scrape_function):
    html = await fetch(session, url, headers)
    if not html:
        return key, None
    
    soup = bs4.BeautifulSoup(html, 'lxml')
    jsonResult = clean_data(scrape_function(soup))
    return key, {
        "products": jsonResult,
        "websiteLink": url
    }

def clean_data(data):
    print(f"Data scraped before cleaning: {data}")
    if (data != None and isinstance(data, list)):
        filteredData = []
        # Removes data with 0 stock and removes non numerical characters 
        dictKey = list(data.keys())[0]
        items = data[dictKey]
        for part in items:
            stock = part["stock"]
            if stock.isnumeric() != True:
                part["stock"] = re.sub(r'\D', '', stock)
            if part["stock"] != "":
                if int(part["stock"]) != 0: 
                    filteredData.append(part)
            # makes sure price has $ in front of it 
            # if "price" in part:
            #     price = part["price"]
            #     if price != "":
            #         if price[0] != "$":
            #             if price[0].isnumeric():
            #                 part["price"] = "$" + price
            #             else:
            #                 part["price"] = "$" + price[1:]
        data[dictKey] = filteredData
    return data

def scrape_all(data):
    partsDictionary = {}
    return partsDictionary

def scrape_oemtrade(data):
    partsDictionary = {}
    partElems = data.find_all('div', class_='distributor-results')
    for part in partElems:
        offers = part.find_all("tr", class_="row")
        if (len(offers) != 0):
            for offer in offers:
                partNumber = offer.get('data-part')
                if partNumber not in partsDictionary:
                    partsDictionary[partNumber] = []
                distributor = offer.get('data-distributor_name')
                manufacturer = offer.get('data-mfr')
                stock = offer.get('data-instock')
                price = offer.get('data-price')

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
    return partsDictionary

def scrape_octopart(data):
    partsDictionary = {}
    partElems = data.find_all('div', attrs={'data-sentry-component':'Part'})
    for part in partElems:
        offers = part.find_all('tr', attrs={'data-testid':'offer-row'})
        if (len(offers) != 0):
            manufacturer = part.select_one('[data-testid="serp-part-header-manufacturer"]').get_text(strip=True)
            partNumber = part.select_one('[data-testid="serp-part-header-mpn"]').get_text(strip=True)
            if partNumber not in partsDictionary:
                partsDictionary[partNumber] = []
            for offer in offers:
                distributor = offer.select_one('[data-sentry-component="Distributor"]').get_text(strip=True)
                stock = offer.select_one('[data-sentry-component="Stock"]').get_text(strip=True)
                prices = offer.select('[data-sentry-component="PriceAtQty"]')[:3]
                price = offer.select_one('[data-sentry-component="PriceAtQty"]').get_text(strip=True)
                priceRange = [1, 10, 100]
                
                formattedPrices = [
                    {"quantity": priceRange[i], "price": f"${p.get_text(strip=True)}"}
                    for i, (p) in enumerate(prices)
                ]    
                link = offer.select_one('[data-sentry-component="Sku"]').find('a')['href']
                partsDictionary[partNumber].append({
                "distributor": distributor,
                "stock": stock,
                "prices": formattedPrices,
                "link": link,
                "manufacturer": manufacturer
                })
    return partsDictionary

def scrape_icsource(data):
    jsonResult = []
    partElems = data.find_all('tr', class_='rgRow')
    for part in partElems:
        cells = part.find_all("td")
        jsonResult.append({
        "Part Number": cells[0].get_text(strip=True),
        "manufacturer": cells[1].get_text(strip=True),
        "year": cells[2].get_text(strip=True),
        "stock": cells[3].get_text(strip=True),
        })
    icsourceJSON = {}
    icsourceJSON["ICSource.com"] = jsonResult
    return icsourceJSON


def scrape_findchips(data):
    partsDictionary = {}
    #for every unique part number, add to dictionary,
    distributorResults = data.find_all('div', class_='distributor-results')
    for distributor in distributorResults:
        distributorName = distributor.get('data-distributor_name')
        parts = distributor.find_all('tr', class_='row')
        if len(parts) != 0:
            for part in parts:
                partNumber = part.get('data-mfrpartnumber')
                if partNumber not in partsDictionary:
                    partsDictionary[partNumber] = []

                # price = part.select('td.td-price-range')[0].get_text(strip=True)
                price = part.get('data-price')
                stock = part.get('data-stock')
                manufacturer = part.get('data-mfr')
                distributorNo = part.get('data-distino')
                link = part.select_one('td.td-buy').find('a')['href']

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
    return partsDictionary

