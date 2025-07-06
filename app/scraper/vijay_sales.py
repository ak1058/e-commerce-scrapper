import logging
import asyncio
import concurrent.futures
from urllib.parse import quote
from app.models import SearchResult
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def run_vijaysales_scraper(query: str, country: str) -> list[SearchResult]:
    results = []

    if country.lower() != "in":
        return results

    search_url = f"https://www.vijaysales.com/search-listing?q={quote(query)}"
    logger.info(f"Navigating to: {search_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(5000)  # Wait for content to load

        try:
            product_cards = page.query_selector_all("div.plp-vertical-products div.product-card")
            logger.info(f"Found {len(product_cards)} products on Vijay Sales")

            for card in product_cards[:10]:
                try:
                    link_el = card.query_selector("a.product-card__link")
                    name_el = card.query_selector("div.product-name")
                    price_el = card.query_selector("div.discountedPrice span:last-child")

                    if not (link_el and name_el and price_el):
                        continue

                    link = link_el.get_attribute("href")
                    full_link = link if link.startswith("http") else f"https://www.vijaysales.com{link}"
                    title = name_el.inner_text().strip()
                    price = float(price_el.inner_text().replace(",", "").strip())

                    results.append(SearchResult(
                        productName=title,
                        link=full_link,
                        price=price,
                        currency="INR"
                    ))

                except Exception as e:
                    logger.warning(f"Error parsing product: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Timeout or error fetching Vijay Sales products: {e}")

        browser.close()

    return results

# Async wrapper for FastAPI
async def fetch(query: str, country: str) -> list[SearchResult]:
    logger.info(f"Vijay Sales Scraper called with query='{query}', country='{country}'")
    loop = concurrent.futures.ThreadPoolExecutor()
    return await asyncio.get_event_loop().run_in_executor(loop, run_vijaysales_scraper, query, country)