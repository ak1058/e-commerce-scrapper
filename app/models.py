from pydantic import BaseModel

class SearchQuery(BaseModel):
    country: str
    query: str

class SearchResult(BaseModel):
    link: str
    price: float
    currency: str
    productName: str
