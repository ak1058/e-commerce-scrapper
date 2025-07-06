import logging
import asyncio
import concurrent.futures
from urllib.parse import quote
from app.models import SearchResult
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def run_tata_croma_scraper(query: str, country: str) -> list[SearchResult]:
    results = []

    if country.lower() != "in":
        return results

    encoded_query = quote(query)
    search_url = f"https://www.croma.com/searchB?q={encoded_query}%3Arelevance&text={encoded_query}"
    logger.info(f"Navigating to: {search_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-IN",
            java_script_enabled=True
        )
        page = context.new_page()

     
        page.set_extra_http_headers({
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": '"Chromium";v="114", "Google Chrome";v="114", "Not:A-Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "upgrade-insecure-requests": "1",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document"
        })

      
        try:
            response = page.goto(search_url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Navigation failed: {e}")
            return []

      
        # with open("a.html", "w", encoding="utf-8") as f:
        #     f.write(page.content())

    
        if "Access Denied" in page.title() or "You don't have permission" in page.content():
            logger.warning("Access Denied by Tata Croma")
            return []

        try:
            page.wait_for_selector("ul.product-list li.product-item", timeout=10000)
        except Exception as e:
            logger.warning(f"Timeout waiting for product list: {e}")
            return []

        product_items = page.query_selector_all("ul.product-list li.product-item")
        logger.info(f"Found {len(product_items)} products on Tata Croma")

        for item in product_items[:10]:
            try:
                title_el = item.query_selector("h3.product-title a")
                price_el = item.query_selector("span[data-testid='new-price']")

                if not (title_el and price_el):
                    continue

                title = title_el.inner_text().strip()
                relative_link = title_el.get_attribute("href")
                full_link = "https://www.croma.com" + relative_link

                price_text = price_el.inner_text().replace("₹", "").replace(",", "").strip()
                price = float(price_text)

                results.append(SearchResult(
                    productName=title,
                    link=full_link,
                    price=price,
                    currency="INR"
                ))
            except Exception as e:
                logger.warning(f"Error parsing product: {e}")
                continue

        browser.close()

    return results


# Async wrapper for FastAPI
async def fetch(query: str, country: str) -> list[SearchResult]:
    logger.info(f"Tata Croma Scraper called with query='{query}', country='{country}'")
    loop = concurrent.futures.ThreadPoolExecutor()
    return await asyncio.get_event_loop().run_in_executor(loop, run_tata_croma_scraper, query, country)
