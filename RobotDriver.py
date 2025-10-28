import asyncio
from typing import List
from playwright.async_api import async_playwright, Playwright, Page

WEBSITE = 'https://www.amazon.com/'
PRODUCT = "hand soap"

async def handle_continue_shopping(page: Page):
    '''
    Description:
    Handles Amazon’s occasional “Continue Shopping” interstitial page that may appear before the home page fully loads.

    Steps:
    (1) Waits briefly (2 seconds) for the prompt to appear.

    (2) Checks if a “Continue shopping” button is visible.

    (3) If found, clicks it and returns True.

    (4) Returns False if not visible or an error occurs.

    Purpose:
    Ensures that automation isn’t blocked by unexpected modal interruptions.
    '''
    try:
        # Wait briefly in case it appears
        await page.wait_for_timeout(2000)
        if await page.is_visible("text=Continue shopping"):
            await page.get_by_role("button", name="Continue shopping").click()
            return True
    except:
        pass
    return False

async def search_product(page: Page) -> bool:
    '''
    Navigates to Amazon’s homepage and searches for the specified product.

    Steps:

    (1) Loads the Amazon website.

    (2) Calls handle_continue_shopping() in case the “Continue Shopping” page appears.

    (3) Waits for the search bar to appear.

    (4) Fills the search box with the product name (PRODUCT) and clicks the search button.

    Returns True if the search was successful, otherwise returns False.

    Purpose:
    Automates the process of searching for a product on Amazon.
    '''
    try:
        response = await page.goto(WEBSITE, wait_until="domcontentloaded")

        if not response or not response.ok:
            return False
        
        await handle_continue_shopping(page)

        if await page.wait_for_selector("input#twotabsearchtextbox"):
            await page.fill("input#twotabsearchtextbox", PRODUCT)
            await page.click("#nav-search-submit-button")
            return True
        else:
            await page.fill("input#nav-bb-bar", PRODUCT)
            await page.click("#nav-search-submit-button")
            return True
    except Exception as e:
        print("Search Error:", e)
        return False

async def scrape_price(page: Page) -> str:
    '''
    Description:
    Extracts product prices from the current Amazon search results page.

    Steps:
    (1) Waits for the price elements to appear.

    (2) Locates all price elements using the CSS selector .a-price .a-offscreen.

    (3) Retrieves the first visible price’s text content.

    (4) Returns the price as a string.

    Purpose:
    Collects the displayed product price from the search results.
    '''
    await page.wait_for_selector(".a-price-whole", timeout=10000)
    prices = await page.locator(".a-price .a-offscreen").first.text_content()
    return prices

async def run(playwright: Playwright):
    '''
    Description:
    Controls the overall browsing process for product search and price extraction.

    Steps:
    (1) Launches a Chromium browser (headless mode).

    (2) Creates a new page and runs search_product() to perform the search.

    (3) Calls scrape_price() and prints the result.

    (4) Closes the browser afterward.

    Purpose:
    Serves as the main routine for orchestrating the web scraping flow.
    '''
    
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()

    if await search_product(page):
        price = await scrape_price(page)
        print(f"Success!\nHere are the prices for {PRODUCT}: {price}")
    else:
        print(f"Failed to Search for {PRODUCT}")

    await browser.close()

async def main():
    async with async_playwright() as p:
        await run(p)

if __name__ == "__main__":
    asyncio.run(main())
