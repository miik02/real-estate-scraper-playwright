# 🏙️ Real Estate Lead Generator: Anti-Bot Playwright Scraper

A production-grade web scraping and ETL pipeline built with Python and Playwright. This tool is designed to extract "For Sale By Owner" (FSBO / Particulares) real estate listings from heavily protected property portals (e.g., Idealista), providing highly valuable, ready-to-call leads for real estate agencies.

## 🚀 Business Value
Real estate agencies spend heavily on acquiring new properties to sell. This script automates the lead generation process by filtering out professional competitors (other agencies) and advertisements, extracting only direct-from-owner listings across multiple geographical zones, and structuring the data into a clean CSV format for immediate commercial action.

## 🧠 Technical Challenges Overcome

This project was built to operate in a hostile scraping environment, bypassing advanced security measures and handling unpredictable DOM structures.

### 1. Defeating Advanced Anti-Bot Systems (Datadome)
High-traffic portals use fingerprinting and behavior analysis to block automated scripts instantly. This scraper bypasses these firewalls by:
*   **Persistent Context & Browser Hijacking:** Instead of launching a sterile Chromium instance, the script uses `launch_persistent_context` mapped to a local Google Chrome profile (`channel="chrome"`). This preserves clearance cookies and mimics genuine human browser history.
*   **Stealth Injection:** Implemented `playwright-stealth` to spoof browser fingerprints and mask the `navigator.webdriver = true` flag.
*   **Automation Hiding:** Passed specific Chromium arguments (`--disable-blink-features=AutomationControlled`) to prevent detection at the Blink rendering engine level.

### 2. High-Performance DOM Filtering 
Rather than extracting all elements and filtering them in Python (which is slow and resource-intensive), the script utilizes advanced CSS pseudo-classes to exclude invalid data natively:
*   Used the locator `article.item:not(.item_contains_branding):not(.adv)` to instantly discard advertisements and listings belonging to other real estate agencies, drastically reducing DOM parsing time.

### 3. Fault Tolerance & "Zombie" Element Mitigation
Websites often inject hidden "honeypots" or feature malformed ad containers that cause traditional scrapers to crash via timeouts.
*   **Granular Timeouts:** Overrode Playwright's default 30-second timeout to 5 seconds (`timeout=5000`) for specific element lookups, ensuring the bot fails fast and moves on if it encounters a broken element.
*   **Robust `try...except` Architecture:** Wrapped the extraction logic in exception handlers to isolate problematic elements. If a listing is malformed, the script logs a warning and seamlessly proceeds to the next item without dropping the entire zone's dataset.

### 4. Smart Pagination & Silent Redirect Handling
Portals often employ SEO traps, such as returning Page 1 silently instead of a 404 error when a requested page doesn't exist.
*   Built a URL validation check (`f"pagina-{current_page}" not in page.url`) to detect silent redirects and break the pagination loop automatically, preventing infinite loops and data duplication.

## 🛠️ Tech Stack
*   **Python 3.12**
*   **Playwright (Sync API):** For dynamic rendering and browser automation.
*   **Playwright-Stealth:** For anti-bot evasion.
*   **Pandas:** For data transformation (ETL) and CSV exporting.

## ⚙️ How to Run

1. Clone the repository and install the requirements:
   ```bash
   pip install playwright playwright-stealth pandas
   playwright install
   ```
2. Ensure you have Google Chrome installed on your system (used for the persistent context).

3. Run the script:
    ```bash
    python scraper_inmobiliario.py
    ```
4. Note on First Run: If prompted with a Captcha or cookie consent in the opened browser, resolve it manually. The clearance will be saved in the bot_profile directory, ensuring frictionless access on subsequent runs.


📊 Data Output

The pipeline exports a structured CSV (private_listings_data.csv) containing:

*  **Zone:** The geographical area of the search.
*  **Title:** Property name and location.
*  **Price:** Cleaned price string.
*  **Features:** Concatenated string of key features (e.g., bedrooms, square meters, floor).
*  **URL:** Direct link to the listing.
