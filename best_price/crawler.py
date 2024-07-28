import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from auth_data import olx_username, olx_password
from urllib.parse import urlparse, parse_qs, urlunparse


def init_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Remove this line to run in non-headless mode
    service = Service(r'C:\WebDrivers\chromedriver.exe')  # Update the path if needed
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def login(driver, username, password):
    try:
        driver.get("https://www.olx.ua/uk/")

        # Click on the profile link to navigate to the login page
        profile_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.css-zs6l2q a.css-12l1k7f'))
        )
        profile_link.click()

        # Fill in username and password
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        username_field.clear()
        username_field.send_keys(username)

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'password'))
        )
        password_field.clear()
        password_field.send_keys(password)

        # Submit the form to login
        password_field.submit()

        time.sleep(7)  # Allow time for the login process

        # Verify if login is successful
        current_url = driver.current_url
        if "myaccount" in current_url:
            print("Login successful.")
            navigate_to_my_account(driver)
        else:
            print(f"Login failed. Current URL: {current_url}")

    except Exception as e:
        print(f"Error during login: {e}")


def navigate_to_my_account(driver):
    try:
        driver.get("https://www.olx.ua/d/uk/myaccount")
        print("Navigated to My Account page.")

        # After navigating to My Account, proceed to favorites
        navigate_to_favorites(driver)

    except Exception as e:
        print(f"Error navigating to My Account: {e}")


def scrape_seller_links(driver):
    try:
        seller_links = []

        # Find all links on the page that point to sellers
        seller_elements = driver.find_elements(By.CSS_SELECTOR, 'div.css-1mzzuk6 > a.css-cj7voq, a.css-1giby4d')

        for element in seller_elements:
            link = element.get_attribute('href')
            seller_links.append({'seller_link': link})

        # Save to JSON file
        with open('seller_links.json', 'w', encoding='utf-8') as f:
            json.dump(seller_links, f, ensure_ascii=False, indent=4)

        print(f"Saved {len(seller_links)} seller links to seller_links.json")

    except Exception as e:
        print(f"Error scraping seller links: {e}")


def navigate_to_favorites(driver):
    try:
        driver.get("https://www.olx.ua/uk/favorites/search/")
        print("Navigated to Favorites page.")

        time.sleep(7)

        # Proceed to scrape seller links
        scrape_seller_links(driver)

    except Exception as e:
        print(f"Error navigating to Favorites: {e}")


def get_base_url_with_page(url, page):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params.pop('min_id', None)  # Remove min_id if it exists
    query_params.pop('reason', None)  # Remove reason if it exists
    query_params['page'] = str(page)  # Add the page parameter
    new_query = '&'.join([f"{key}={value[0]}" for key, value in query_params.items()])
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', new_query, ''))
    return new_url


def scrape_product_details(driver, seller_link, start_id):
    products = []

    try:
        # Find the last page number
        driver.get(seller_link)
        time.sleep(5)  # Allow time for the page to load

        # Locate the pagination list and get the last page number
        pagination_items = driver.find_elements(By.CSS_SELECTOR, 'li[data-testid="pagination-list-item"] a')
        if not pagination_items:
            print(f"No pagination items found on {seller_link}. Scraping only the first page.")
            last_page_number = 1
        else:
            last_page_number = max([int(item.text) for item in pagination_items if item.text.isdigit()])

        # Start scraping from the last page to the first page
        for page_number in range(last_page_number, 0, -1):
            page_url = get_base_url_with_page(seller_link, page_number)
            print(f"Scraping page {page_number}: {page_url}")  # Log the page URL being scraped
            driver.get(page_url)
            time.sleep(5)  # Allow time for the page to load

            product_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="l-card"]')

            if not product_elements:
                print(f"No products found on page {page_number}.")
                continue  # Continue if no products are found on this page

            for element in product_elements:
                try:
                    link = element.find_element(By.CSS_SELECTOR, 'a.css-13w8mae').get_attribute('href')
                    title = element.find_element(By.CSS_SELECTOR, 'a.css-z3gu2d').text
                    price = element.find_element(By.CSS_SELECTOR, '[data-testid="ad-price"]').text
                    location = element.find_element(By.CSS_SELECTOR, 'p.css-1pzx3wn').text
                    date_of_publication = element.find_element(By.CSS_SELECTOR, 'p.css-1uf1vew span').text
                    products.append({
                        'id': start_id,
                        'link': link,
                        'title': title,
                        'price': price,
                        'location': location,
                        'date of publication': date_of_publication
                    })
                    start_id += 1
                except Exception as e:
                    print(f"Error scraping product details: {e}")

    except Exception as e:
        print(f"Error scraping seller page: {e}")

    return products, start_id


def main():
    driver = None
    try:
        driver = init_driver()
        login(driver, olx_username, olx_password)

        # Load seller links from JSON file
        with open('seller_links.json', 'r', encoding='utf-8') as f:
            seller_links = json.load(f)

        all_products = []
        current_id = 1

        for seller in seller_links:
            seller_link = seller['seller_link']
            products, current_id = scrape_product_details(driver, seller_link, current_id)
            all_products.extend(products)

        # Save all products to prices.json
        with open('prices.json', 'w', encoding='utf-8') as f:
            json.dump({'products': all_products}, f, ensure_ascii=False, indent=4)

        print(f"Saved {len(all_products)} products to prices.json")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    main()
