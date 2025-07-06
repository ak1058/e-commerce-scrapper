import logging
import asyncio
import concurrent.futures
from urllib.parse import quote
from app.models import SearchResult
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def run_reliance_scraper(query: str, country: str) -> list[SearchResult]:
    results = []

    if country.lower() != "in":
        return results

    search_url = f"https://www.reliancedigital.in/products?q={quote(query)}"
    logger.info(f"Navigating to: {search_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(3000)

        product_cards = page.query_selector_all("div.product-card")
        logger.info(f"Found {len(product_cards)} product cards on Reliance Digital")

        for card in product_cards[:10]:  
            try:
                detail_div = card.query_selector(".product-card-details")
                if not detail_div:
                    continue

                a_tag = detail_div.query_selector("a.details-container")
                title_el = a_tag.query_selector(".product-card-title") if a_tag else None
                price_el = a_tag.query_selector(".price") if a_tag else None

                if not (a_tag and title_el and price_el):
                    continue

                title = title_el.inner_text().strip()
                price_text = price_el.inner_text().replace("₹", "").replace(",", "").strip()
                price = float(price_text)

                relative_link = a_tag.get_attribute("href")
                full_link = f"https://www.reliancedigital.in{relative_link}"

                results.append(SearchResult(
                    productName=title,
                    link=full_link,
                    price=price,
                    currency="INR"
                ))
            except Exception as e:
                logger.warning(f"Error parsing product card: {e}")
                continue

        browser.close()

    return results

# Async wrapper for FastAPI
async def fetch(query: str, country: str) -> list[SearchResult]:
    logger.info(f"Reliance Digital Scraper called with query='{query}', country='{country}'")
    loop = concurrent.futures.ThreadPoolExecutor()
    return await asyncio.get_event_loop().run_in_executor(loop, run_reliance_scraper, query, country)
