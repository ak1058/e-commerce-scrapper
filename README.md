﻿
# Price Comparison Tool

This tool allows you to compare product prices across various e-commerce sellers based on your location (currently supports India and US).

---
Video link fro demo: https://www.loom.com/share/ea7dca53a5c44dbc8055d3aed6ac4ec2?sid=3e9dd156-7b46-4b17-bc12-4e82d928987b
## Getting Started

### Steps to Build Docker Image and Run

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. Open Docker Desktop **or** ensure Docker Engine is running.

3. Run the following command in your terminal (within the project directory):
   ```bash
   docker-compose up --build
   ```

4. Wait for around 5 minutes while the Docker image is built and the container starts.

5. Once up, you can access the API endpoint at:
   ```
   http://localhost:8000/compare-prices
   ```

6. For normal subsequent starts (without rebuild):
   ```bash
   docker-compose up
   ```

---

## API Usage

### Endpoint

- **POST** `/compare-prices`

### How to Test

1. Open **Postman** or any other API client.
2. Create a **POST** request to:
   ```
   http://localhost:8000/compare-prices
   ```
3. Set the request **body** (as `raw` JSON):
   ```json
   {
     "country": "IN",
     "query": "samsung s25 ultra"
   }
   ```

---

## Notes

- Currently supports **two countries**: `IN` (India) and `US` (United States).
- For **India**, it supports a wide range of sellers (Flipkart, Croma, Sangeetha, etc.).
- For **US**, it currently supports **Amazon**.
- Each seller has a **dedicated scraper** to ensure robustness and prevent single-point failures.
- In the future, more robust scrapers can be added for additional sellers.

---

## Future Improvements

- Add support for more countries and marketplaces.
- Implement caching and better error handling.
- Build a frontend interface for easier product search.
