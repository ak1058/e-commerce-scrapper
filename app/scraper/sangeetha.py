import logging
import asyncio
import concurrent.futures
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from app.models import SearchResult

logger = logging.getLogger(__name__)

def run_sangeetha_playwright(query: str, country: str) -> list[SearchResult]:
    results = []

    if country.lower() != "in":
        return results

    formatted_query = quote(query)  # encode spaces to %20
    url = f"https://www.sangeethamobiles.com/search-result/{formatted_query}"
    logger.info(f"Navigating to: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(2000)

        items = page.query_selector_all("div.product-wrapper div.product-list")
        logger.info(f"Found {len(items)} results on Sangeetha")

        for item in items[:2]:
            try:
                product_details = item.query_selector("div.product-details")
                if not product_details:
                    continue

                a_tag = product_details.query_selector("a")
                title_el = a_tag.query_selector("h2") if a_tag else None

                price_container = item.query_selector(".product-list-page-effective-price-background")
                if not price_container:
                    continue

                price_spans = price_container.query_selector_all("span.ml-1")
                if len(price_spans) < 2:
                    continue

                # Second span has the deal price
                price_text = price_spans[1].inner_text().replace("₹", "").replace(",", "").strip()
                price = float(price_text)

                if not (a_tag and title_el):
                    continue

                title = title_el.inner_text().strip()
                relative_link = a_tag.get_attribute("href")
                full_link = "https://www.sangeethamobiles.com" + relative_link

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

# Async wrapper
async def fetch(query: str, country: str) -> list[SearchResult]:
    logger.info(f"Sangeetha Scraper called with query='{query}', country='{country}'")
    loop = concurrent.futures.ThreadPoolExecutor()
    return await asyncio.get_event_loop().run_in_executor(loop, run_sangeetha_playwright, query, country)
