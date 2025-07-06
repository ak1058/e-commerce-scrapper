from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.scraper import amazon, amazon_in, flipkart, sangeetha, reliance_digital, tata_croma, vijay_sales
from app.models import SearchResult
import logging

app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

# Allow testing from Postman, browser, etc.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model
class ProductQuery(BaseModel):
    country: str
    query: str

@app.post("/compare-prices", response_model=list[SearchResult])
async def compare_prices(query: ProductQuery):
    logger.info(f"Received query: {query.query} for country: {query.country}")
    results: list[SearchResult] = []

    if query.country.lower() == "us":
        results += await amazon.fetch(query.query, query.country)

    elif query.country.lower() == "in":
        results += await amazon_in.fetch(query.query, query.country)
        results += await flipkart.fetch(query.query, query.country)
        results += await sangeetha.fetch(query.query, query.country)  
        results += await reliance_digital.fetch(query.query, query.country)
        results += await tata_croma.fetch(query.query, query.country)
        results += await vijay_sales.fetch(query.query, query.country)



    else:
        logger.warning(f"Unsupported country: {query.country}")
        return []

    # Sort all results by price
    results.sort(key=lambda x: x.price)

    return results
