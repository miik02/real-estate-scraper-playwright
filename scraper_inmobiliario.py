from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import pandas as pd
import time

def scrape_zone(base_url, zone_name, max_pages=3):
    """
    Scrapes real estate listings for a specific zone, filtering out professional agencies 
    and returning only private owner listings.
    """
    with Stealth().use_sync(sync_playwright()) as p:
        has_more_pages = True
        current_page = 1
        
        # Launching persistent context to bypass bot detection (e.g., Datadome)
        context = p.chromium.launch_persistent_context(
            user_data_dir="./bot_profile", 
            channel="chrome",             
            headless=False,
            slow_mo=100,                  
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = context.pages[0]

        print(f"[{zone_name}] Initializing browser session...")
        page.goto("https://www.idealista.com")
        time.sleep(2)
        
        private_listings = []

        # Pagination loop
        while has_more_pages:
            try:
                page.set_default_timeout(5000)
                
                # Navigate to the appropriate page number
                if current_page > 1:
                    page.goto(f"{base_url}pagina-{current_page}.htm")
                    time.sleep(2)
                else:
                    page.goto(base_url)
                    time.sleep(2)
                
                # Silent redirect check: if the portal sends us back to page 1, break the loop
                if current_page > 1 and f"pagina-{current_page}" not in page.url:
                    raise ValueError(f"No more pages found in {zone_name}. Skipping to next zone.")
                
                # CSS Selectors: Target listings, explicitly excluding ads and agencies
                listings = page.locator("article.item:not(.item_contains_branding):not(.adv)")
                print(f"[{zone_name} - Page {current_page}] Total listings found: {listings.count()}")
                print("Filtering private owner listings...")

                for i in range(listings.count()):
                    current_listing = listings.nth(i)
                    agency_logo = current_listing.locator(".logo-branding")

                    # If no agency logo is present, extract the data
                    if agency_logo.count() == 0:
                        try:
                            title_element = current_listing.locator(".item-link")
                            price_element = current_listing.locator(".price-row")
                            feature_elements = current_listing.locator(".item-detail")
                            
                            # Safety check for broken DOM elements
                            if title_element.count() == 0 or price_element.count() == 0:
                                continue
                                
                            listing_url = "https://www.idealista.com" + title_element.get_attribute("href")

                            private_listings.append({
                                "Zone": zone_name,
                                "Title": title_element.inner_text(),
                                "Price": price_element.inner_text().split("\n")[0].strip(),
                                "Features": ", ".join([text.strip() for text in feature_elements.all_inner_texts()]),
                                "URL": listing_url
                            })
                            
                        except Exception:
                            print(f"⚠️ Skipped problematic listing in {zone_name} (Position {i})")
                            continue
                            
                time.sleep(2)
                current_page += 1
                
                # Stop if we reach the defined maximum number of pages
                if current_page > max_pages and max_pages > 1:
                    raise ValueError("Maximum selected pages reached.")
                
                # Restore default timeout just in case it's needed for internal processes
                page.set_default_timeout(30000)
                
            except Exception as e:
                # Catches both the raised ValueErrors and actual timeouts to exit the loop cleanly
                print(f"[{zone_name}] Pagination ended: {e}")
                has_more_pages = False

        print(f"[{zone_name}] Extracted {len(private_listings)} private listings.\n")
        
        # Clean up memory and close the browser properly
        context.close()
        return private_listings


# Target configuration dictionary
target_zones = {
    "Las Rosas": "https://www.idealista.com/geo/venta-viviendas/metro-las-rosas/",
    "Colmenar Viejo": "https://www.idealista.com/venta-viviendas/colmenar-viejo-madrid/"
}

all_scraped_data = []

# Main execution loop iterating over multiple geographical zones
for zone_name, target_url in target_zones.items():
    print(f"--- Starting extraction for: {zone_name} ---")
    zone_data = scrape_zone(target_url, zone_name)
    all_scraped_data.extend(zone_data)

# Data transformation and load (ETL)
df = pd.DataFrame(all_scraped_data)

# Note: Ensure the 'Data/' folder exists in your directory, otherwise remove the prefix.
# index=False prevents pandas from writing the row indices to the file.
df.to_csv("Data/private_listings_data.csv", index=False)
print("Data extraction complete. File saved successfully.")