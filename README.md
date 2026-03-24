# Forseti

A web application for searching and aggregating electronic component data across multiple sourcing sites.  
The goal is to provide specialists with a single interface to look up part numbers (MPNs), view supplier listings, and compare stock, pricing, and availability.  

## Features

- 🔍 **Search by part number (MPN)**  
- 🧩 **Aggregated results** grouped by `partNumber → website → listings`  
- 📊 **Nested supplier breakdowns** including distributor ID, links, and stock levels  
- ⏱ **Asynchronous web scraping** for faster data collection across multiple sources
- ⚡ **React/Next.js frontend** with Tailwind CSS for a clean, responsive UI
- 🖥 **Flask API backend** powered by `aiohttp` + BeautifulSoup
- 📈 **Vercel Analytics** for usage tracking and insights

## Tech Stack

**Frontend**  
- [Next.js 15](https://nextjs.org/)  
- [React](https://react.dev/)  
- [TypeScript](https://www.typescriptlang.org/)  
- [Tailwind CSS](https://tailwindcss.com/)  

**Backend**  
- [Python 3.11+](https://www.python.org/)  
- [Flask](https://flask.palletsprojects.com/)  
- [aiohttp](https://docs.aiohttp.org/)  
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)  

**Analytics**
- [@vercel/analytics](https://vercel.com/analytics)

**Deployment**
- Frontend: Vercel
- Backend: Render (Flask API)

## Roadmap

- Add UI filters (stock thresholds, distributor filters)
- Enable periodic crawling to pre-cache MPNs (where allowed)
- Forum page for community discussion
