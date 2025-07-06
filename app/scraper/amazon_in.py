import logging
import asyncio
import concurrent.futures
from app.models import SearchResult
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def run_playwright_sync(query: str, country: str) -> list[SearchResult]:
    results = []

    if country.upper() != "IN":
        return results

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        logger.info(f"Navigating to: {search_url}")
        page.goto(search_url, timeout=60000)

        items = page.query_selector_all("div[data-component-type='s-search-result']")
        logger.info(f"Found {len(items)} results on Amazon")

        for item in items[:15]:
            try:
                link_el = item.query_selector("a.a-link-normal.s-link-style")
                title_el = link_el.query_selector("span") if link_el else None
                price_el = item.query_selector("span.a-price > span.a-offscreen")

                if not (title_el and link_el and price_el):
                    continue

                title = title_el.inner_text().strip()

               
                blacklist_keywords = [
                    "case", "cover", "charger", "accessory", "screen guard",
                    "protector", "cable", "adapter", "stand", "mount", "glass"
                ]
                if any(bad_word in title.lower() for bad_word in blacklist_keywords):
                    continue

                relative_link = link_el.get_attribute("href")
                full_link = "https://www.amazon.in" + relative_link

                raw_price = price_el.inner_text().strip()  
                clean_price = raw_price.replace("₹", "").replace(",", "").strip()
                price = float(clean_price)

                results.append(SearchResult(
                    productName=title,
                    link=full_link,
                    price=price,
                    currency="INR"
                ))

            except Exception as e:
                logger.warning(f"Error parsing item: {e}")
                continue

        browser.close()
    return results

# Async wrapper for FastAPI
async def fetch(query: str, country: str) -> list[SearchResult]:
    logger.info(f"Amazon India Scraper called with query='{query}', country='{country}'")

    loop = concurrent.futures.ThreadPoolExecutor()
    return await asyncio.get_event_loop().run_in_executor(loop, run_playwright_sync, query, country)
