from playwright.async_api import async_playwright
from app.models import SearchResult
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.flipkart.com"

async def fetch(query: str, country: str) -> list[SearchResult]:
    logger.info(f"Flipkart Scraper called with query='{query}', country='{country}'")

    results = []
    search_url = f"{BASE_URL}/search?q={query.replace(' ', '+')}"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            logger.info(f"Navigating to: {search_url}")
            await page.goto(search_url, timeout=60000)

            items = await page.query_selector_all("a.CGtC98")  
            logger.info(f"Found {len(items)} results on Flipkart")

            for item in items[:2]:  
                try:
                    title_el = await item.query_selector("div.KzDlHZ")
                    price_el = await item.query_selector("div.Nx9bqj")

                    if not (title_el and price_el):
                        continue

                    title = (await title_el.inner_text()).strip()
                    price_raw = (await price_el.inner_text()).strip()

                  
                    price = float(price_raw.replace("₹", "").replace(",", "").strip())

                    href = await item.get_attribute("href")
                    link = BASE_URL + href if href else ""

                    # Filter out accessories
                    blacklist = [
                        "case", "cover", "charger", "accessory", "screen guard",
                        "protector", "cable", "adapter", "stand", "mount", "glass"
                    ]
                    if any(bad in title.lower() for bad in blacklist):
                        continue

                    results.append(SearchResult(
                        productName=title,
                        link=link,
                        price=price,
                        currency="INR"
                    ))

                except Exception as e:
                    logger.warning(f"Error parsing Flipkart item: {e}")
                    continue

            await browser.close()

    except Exception as e:
        logger.error(f"Flipkart scraping failed: {e}")

    return results
